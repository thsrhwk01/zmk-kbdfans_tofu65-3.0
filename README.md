# TOFU65 3.0 Wired ZMK — Experimental

KBDfans TOFU65 3.0 **유선 핫스왑 UniCore-F1** 기판을 위한 ZMK 포팅 소스입니다.
제공된 순정 `CURRENT.UF2`를 분석해 작성했습니다. 다른 TOFU 기판용이 아닙니다.

**현재 상태: 빌드와 파일 검증은 통과했지만, 첫 실기기 시험에서 Windows HID Code 10이 발생했습니다.**
기판에서 읽어 낸 ZMK 데이터는 배포 BIN과 정확히 일치하며 부트로더·순정 설정도 보존됐습니다.
현재 소스는 USB 인터럽트 차단 시간을 줄이고 HID 초기화를 USB 연결보다 먼저 실행합니다.
이 변경으로 실기기 문제가 해결됐는지는 아직 확인되지 않았습니다.
자세한 관찰과 시험 순서는 [USB bring-up 기록](analysis/usb-bringup.md)을 참고하세요.

## 구현 범위

- PB12 클럭 / PB13 양방향 데이터의 112비트 직렬 스캔 드라이버.
- 순정의 채움 극성 및 입력 풀 방향 탐지, 히스토리 기반 디바운스.
- 69개 스위치 위치를 포함하는 공통 매핑: 기본 ANSI 67키와 분할 키 2개.
- 백스페이스 분할, 좌시프트 분할, ISO 엔터, 6.25u/7u 하단 배열 선택.
- USB 전용, HSI 기반 48 MHz 클럭 설정, 순정 UF2 부트로더 진입 동작.
- ELF/BIN 메모리 검사 및 Family ID `0x9D5BCF10`의 UF2 패키징.

첫 버전은 Studio, CapsLock 색상/조명 제어, 영구 설정 저장을 포함하지 않습니다.
스캔의 펄스 폭과 풀 방향 탐지는 실제 기판에서 확인해야 합니다.

## 보존하는 영역

| 영역 | 주소 | 처리 |
| --- | --- | --- |
| 순정 부트로더 | `0x08000000`–`0x08003FFF` | 기록하지 않음 |
| ZMK 코드 | `0x08004000`–`0x0801DFFF` | 최대 104 KiB |
| 순정 설정 | `0x0801E000`–`0x0801FFFF` | 기록하지 않음 |
| ZMK RAM | `0x20000000`–`0x20003FFF` | 하위 16 KiB만 사용 |
| 부트 요청 매직 | `0x20004000` | 순정 규약대로 요청 후 리셋 |

앱 시작 주소는 순정 부트로더의 분기 코드로 확인했습니다. 정확한 MCU 제조사와
실제 ZMK 동작은 아직 하드웨어에서 확인하지 않았습니다. 근거와 주소는
[리버싱 기록](analysis/reverse-engineering.txt)에 있습니다.

## 배열과 키맵

`config/layout-options.h`의 각 값을 `0` 또는 `1`로 설정한 후 다시 빌드합니다.

```c
#define TOFU_SPLIT_BACKSPACE 1
#define TOFU_ISO_ENTER 0
#define TOFU_SPLIT_LSHIFT 1
#define TOFU_SPACE_7U 0
```

위 예시는 분할 백스페이스/좌시프트, ANSI 엔터, 6.25u 하단 배열입니다.
기본 제공값은 모두 `0`입니다. 실제 장착한 스위치 배열과 맞춰야 합니다.
분할 추가 키의 기본값은 각각 Delete와 NUBS이며 원하는 기능으로 변경할 수 있습니다.
ISO에서는 엔터/추가 문자 키를 해당 좌표로 바꾸고, 7u에서는 빠지는 하단 키를
`&none`으로 처리합니다. 선택 옵션과 관계없이 키맵은 69개 위치를 유지합니다.

`config/tofu65_3_0.keymap`은 기본 키맵을 불러옵니다. 개인 키맵을 만들 때는
`include/tofu65_3_0-default-keymap.dtsi`의 내용을 복사해 수정하고,
69개 바인딩의 순서를 유지하세요. 생성된 기본 파일은 `tools/generate_layout.py`가
다시 쓸 수 있습니다. `config/`의 개인 파일은 생성기가 수정하지 않습니다.

기본 Fn은 `(7,2)` 위치이며 Fn+Esc는 재시작, Fn+맨 오른쪽 상단 Delete는
UF2 부트로더 진입입니다. 둘 다 실기기 테스트 전입니다. 물리 double-tap 버튼은
순정 부트로더에 남아 있습니다.

## 빌드

ZMK는 `v0.3.0`의 정확한 커밋 `edf5c0814fd3ea202e43aad2d68fd32e882a518c`를 사용합니다.
GitHub의 **Experimental TOFU65 ZMK build** 워크플로는 테스트, 의존성 설치,
빌드, ELF 검사, UF2 패키징을 차례로 실행합니다. 실패하면 플래싱용 UF2를 배포하지
않으며, 성공 시 `TOFU65-3.0-ZMK-normal-EXPERIMENTAL`과
`TOFU65-3.0-ZMK-usb-diagnostic-EXPERIMENTAL` 아티팩트를 만듭니다.
일반 시험에는 `normal`을 사용합니다. `usb-diagnostic`은 반복 키 스캔을 끈
원인 분리용이며 정상 인식되어도 키 입력이 되지 않습니다.
의존성 전체의 실제 커밋은 `manifest-frozen.yml`에 기록합니다.

푸시 후 해당 커밋의 빌드가 끝날 때까지 3분 간격으로 확인할 수 있습니다.
성공은 종료 코드 0, 실패는 1, 감시 시간 초과는 2입니다. 시간 초과를 성공으로 간주하지 마세요.

```powershell
python tools/watch_actions.py --sha (git rev-parse HEAD) --interval 180
```

로컬 빌드는 ZMK/Zephyr용 Python, west, CMake, Ninja, ARM 툴체인이 필요합니다.
별도의 west 작업 폴더에서 이 저장소의 `config/`를 복사해 초기화합니다.

```sh
mkdir -p firmware-workspace/config
cp -R config/. firmware-workspace/config/
cd firmware-workspace
west init -l config
west update
west zephyr-export
west build -s zmk/app -d build -b tofu65_3_0 -- \
  -DZMK_CONFIG=/absolute/path/to/this/repository/config \
  -DZMK_EXTRA_MODULES=/absolute/path/to/this/repository
```

Windows에서 준비된 west 작업 폴더가 있다면 이 저장소에서 실행합니다.

```powershell
./tools/build.ps1 -FirmwareWorkspace 'D:/path/to/firmware-workspace'
```

스크립트는 빌드 성공 뒤 ELF/BIN을 검사하고 `dist/<timestamp>/`에 UF2를 만듭니다.
키보드를 찾거나 파일을 장치에 복사하지 않습니다. 다른 보드의 BIN을 이름만 바꾸거나
임의의 주소로 변환해서 사용하지 마세요.

## 오프라인 검증

```sh
python tools/test_firmware_tools.py
python tools/test_build_verifier.py
python tools/test_layouts.py --cpp arm-none-eabi-gcc
cc -std=c11 -Wall -Wextra -Werror -Isrc tests/test_scan_core.c -o test-scan
./test-scan
```

검사 범위: UF2 손상/주소/벡터, 16개 배열 조합, 양 극성의 112개 위치,
225회 클럭 시퀀스, 입력/출력 전환, 디바운스. 배열 테스트는 전처리 검사이며,
Zephyr Devicetree·Kconfig와 전체 펌웨어 빌드 검증을 대신하지 않습니다.

최초 실기기 검증은 빌드 산출물이 확보된 뒤 USB 인식, 모든 키와 조합 입력,
케이블 재연결, 물리 double-tap 재진입, 소프트웨어 부트 진입을 확인해야 합니다.
`analysis/stock-application-recovery.UNTESTED.uf2`는 순정 복구 준비 파일이며 ZMK가 아닙니다.

## 순정 복구

물리 버튼을 두 번 눌러 `UniCore-F1` 드라이브로 진입한 뒤
`analysis/stock-application-recovery.UNTESTED.uf2`를 복사합니다.
이 파일은 최초 스냅샷에서 부트로더 16 KiB를 제외한 순정 펌웨어·설정을
그대로 보존하고, 쓰기에 필요한 UF2 Family ID와 플래그를 지정한 파일입니다.
장치가 내보내는 원본 `CURRENT.UF2`는 해당 쓰기 조건을 만족하지 않으므로
그대로 복사하는 복구 방법을 사용하지 마세요. 실제 복구 성공 여부는 별도 확인이 필요합니다.
