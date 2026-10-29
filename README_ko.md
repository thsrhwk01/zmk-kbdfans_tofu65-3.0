# KBDfans TOFU65 3.0 유선 ZMK 펌웨어

[English](README.md)

**KBDfans TOFU65 3.0 유선 핫스왑 UniCore-F1 PCB**용 USB 전용 ZMK 포트입니다. 기판에서 추출한 순정 UF2를 분석해 구현했으며, 공장 부트로더와 순정 설정 영역을 보존합니다.

## 기능

- PB12/PB13 양방향 직렬 스캔: 112단계 입력, 논리 스위치 위치 69개
- 백스페이스·좌시프트 분할, ANSI/ISO 엔터, 6.25u/7u 배열 선택
- PC의 Caps Lock 상태에 따라 약한 흰색으로 켜지는 RGB 표시등
- 부팅 시 검정 프레임을 전송해 부트로더의 잔류 색 제거
- Fn + Delete로 순정 UF2 부트로더 진입
- ZMK 커밋 고정, 자동 테스트, ELF/BIN 메모리 검사 및 UF2 생성

다른 저장소의 Windows/macOS·홈로우·마우스 개인 키맵은 **아직 이식하지 않았습니다**. VIA/Vial 설정, ZMK Studio, 무선, 영구 설정 저장, 실행 중 LED 색상 변경도 현재 구현 범위에 포함되지 않습니다.

## 지원 하드웨어

| 항목 | 대상 / 확인 근거 |
| --- | --- |
| PCB | TOFU65 3.0 유선 핫스왑 UniCore-F1 |
| Board ID | `ARM32F103-UniCore-F1-v1.x` |
| 부트로더 | `v24.07.23i`, UF2 볼륨 `UniCore-F1` |
| Zephyr SoC 설정 | STM32F103xB 호환 설정; 실제 MCU 마킹 미확인 |
| 플래시 | 원본 덤프 128 KiB, ZMK 코드 영역 104 KiB |
| ZMK SRAM | 하위 16 KiB 사용, `0x20004000` 부트 요청 영역 예약 |
| 클럭 | HSI/2 × 12 = 48 MHz, USB PLL/1 |
| 연결 | USB 전용 |

TOFU라는 이름이 같더라도 다른 PCB에 주소와 핀을 그대로 적용하지 마세요. MCU 제조사와 정확한 LED 부품명은 아직 확인되지 않았습니다.

## 검증된 펌웨어

2026-10-29 사용자 실기기 확인 기준입니다. 현재 기준 빌드는 분할 키 설정과 Caps Lock 표시등을 포함합니다.

| 항목 | 값 |
| --- | --- |
| 소스 커밋 | `8f92936e28cb3d0207dd13631b5caf775f3328aa` |
| Actions | [40869663384](https://github.com/thsrhwk01/zmk-kbdfans_tofu65-3.0/actions/runs/40869663384) |
| 아티팩트 | `TOFU65-3.0-ZMK-normal-EXPERIMENTAL` |
| 파일 | `tofu65_3_0-zmk-normal-UNTESTED.uf2` |
| UF2 크기 | 73,216바이트 |
| UF2 SHA-256 | `d2f47a4ee2df1ad861b695805dfa5e1d84c762ff4e1597ca9b412282e6f411b3` |
| 앱 / 할당 RAM | 36,588바이트 / 10,376바이트 |

USB 인식·키 입력, 분할 추가 키 두 개, ANSI/ISO 엔터·계단식 Caps Lock·7u 하단 패드의 원하는 키코드, Caps Lock LED, Fn + Delete 부트로더 진입을 확인했습니다. 현재 사용자는 입력 씹힘을 느끼지 못했다고 보고했습니다. 이는 지연 계측이나 장시간 내구 시험 결과는 아닙니다. 선택 패드 시험과 16개 배열 조합 전체의 실조립 검증도 구분합니다.

파일명의 `UNTESTED`는 CI가 매번 만드는 파일에 붙이는 이름입니다. 자동 빌드가 모든 새 펌웨어의 실기기 검증을 보장하지 않으며, 위 표가 실제 확인한 기준 빌드를 특정합니다. ZIP이 아니라 **UF2 파일 자체**의 해시를 비교하세요.

## Windows 빠른 설치

1. 위 검증 빌드 또는 성공한 [빌드 워크플로](https://github.com/thsrhwk01/zmk-kbdfans_tofu65-3.0/actions/workflows/build.yml)를 엽니다.
2. `TOFU65-3.0-ZMK-normal-EXPERIMENTAL`을 받아 압축을 풉니다. `usb-diagnostic`은 의도적으로 키 스캔을 끈 진단판입니다.
3. 필요하면 패키지의 `SHA256SUMS.txt`와 UF2 해시를 비교합니다.

   ```powershell
   Get-FileHash .\tofu65_3_0-zmk-normal-UNTESTED.uf2 -Algorithm SHA256
   ```

4. 기판의 double-tap 버튼 또는 ZMK 실행 중 Fn + 맨 오른쪽 상단 Delete로 UF2 모드에 진입합니다.
5. 생성된 `.uf2`만 `UniCore-F1` 드라이브에 복사합니다. 복사가 끝나고 재시작될 때까지 기다립니다. 필요하면 복사 완료 후 USB를 다시 연결합니다.
6. 키 입력과 Caps Lock 표시를 확인합니다. 최초 순정 백업은 별도로 보관합니다.

이 USB 저장장치 복사 방식에는 QMK Toolbox, dfu-util, 드라이버 교체가 필요하지 않습니다. 장치에서 읽은 원본 `CURRENT.UF2`를 그대로 복원용으로 복사하지 마세요.

## 키맵과 단축키

현재 기본값은 분할 두 옵션 활성화, ANSI 엔터, 6.25u 하단입니다. [config/layout-options.h](config/layout-options.h)를 수정한 뒤 다시 빌드합니다.

```c
#define TOFU_SPLIT_BACKSPACE 1
#define TOFU_ISO_ENTER 0
#define TOFU_SPLIT_LSHIFT 1
#define TOFU_SPACE_7U 0
```

| 키 / 조합 | 동작 |
| --- | --- |
| 기존 백스페이스 / 좌시프트 | Backspace / Left Shift |
| 분할 백스페이스 추가 키 | Delete |
| 분할 좌시프트 추가 키 | NUBS (`IntlBackslash`, 문자는 OS 배열에 따라 달라짐) |
| Fn + 맨 오른쪽 상단 Delete | 순정 UF2 진입, 사용자 확인 완료 |
| Fn + Esc | ZMK 애플리케이션 재시작 |
| Fn + 1…0, Minus, Equal | F1…F12 |

Fn은 하단 왼쪽 화살표 바로 왼쪽 키(`7,2`)입니다. 부트로더 진입에는 상단 Delete(`6,3`)를 사용하며 분할 백스페이스의 추가 Delete는 해당하지 않습니다. 다중 키 combo 대신 레이어 바인딩을 사용해 combo 대기 지연을 만들지 않습니다.

사용자는 Fn + Esc로 부트로더에서 ZMK로 돌아왔다고도 보고했습니다. 다만 구현된 Fn + Esc는 ZMK 키맵의 재시작 기능이며 순정 부트로더는 이 키맵을 실행하지 않습니다. **복귀 관찰은 기록하되 부트로더 자체의 보장된 단축키로 설명하지 않습니다.** 필요하면 USB를 다시 연결합니다.

[config/tofu65_3_0.keymap](config/tofu65_3_0.keymap)은 [include/](include/)의 생성된 기본 키맵을 불러옵니다. 개인 키맵은 `config/`에 두세요. `tools/generate_layout.py`는 기본 파일을 재생성할 수 있습니다. 모든 배열은 69개 논리 위치를 유지하며 ISO는 엔터 주변 바인딩을 교환하고, 7u는 사용하지 않는 오른쪽 Alt 위치를 끕니다.

## 부트로더 보존과 순정 복구

| 영역 | 범위 | 일반 ZMK 업로드 |
| --- | --- | --- |
| 공장 부트로더 | `0x08000000`–`0x08003FFF` | 보존 |
| 애플리케이션 | `0x08004000`–`0x0801DFFF` | 코드만 기록 |
| 순정 설정 | `0x0801E000`–`0x0801FFFF` | 보존 |
| ZMK SRAM | `0x20000000`–`0x20003FFF` | 할당 RAM |

앱 시작 주소는 순정 부트로더의 분기 코드에서 확인했습니다. 패키징은 코드 범위, 초기 스택·리셋 벡터, UF2 Family ID `0x9D5BCF10`을 검사합니다.

순정 복구에는 물리 버튼으로 UF2 모드에 진입한 뒤 [stock-application-recovery.UNTESTED.uf2](analysis/stock-application-recovery.UNTESTED.uf2)를 복사합니다. **최초 순정 앱과 설정을 함께 복원**하고 부트로더는 제외합니다. 내용의 원본 일치는 검증했지만 실제 순정 복구 성공은 명시적으로 보고받지 못했습니다. 원본 `CURRENT.UF2`는 flags/family가 0이고 부트로더 블록까지 포함하는 읽기용 덤프여서 그대로 받아들이는 복원 이미지가 아닙니다.

## 빌드와 검증

ZMK는 `edf5c0814fd3ea202e43aad2d68fd32e882a518c`(v0.3.0)에 고정합니다. 각 아티팩트에는 `manifest-frozen.yml`, ELF/BIN, map, 실제 config/DTS, 배열 옵션, 검증 보고서와 SHA-256이 포함됩니다. CI는 일반판과 스캔 없는 진단판을 만들며, 태그 Release 게시나 장치 플래싱은 수행하지 않습니다.

Python, west, CMake, Ninja, 호환 ARM/Zephyr 툴체인을 준비한 뒤:

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

초기화된 west 작업 폴더가 있으면 Windows용 [tools/build.ps1](tools/build.ps1)로 빌드·검사·로컬 패키징을 수행할 수 있습니다.

```powershell
./tools/build.ps1 -FirmwareWorkspace 'D:/path/to/firmware-workspace'
python tools/watch_actions.py --sha (git rev-parse HEAD) --interval 180
```

감시기는 성공 0, 실패 1, 시간 초과 2를 반환합니다. 시간 초과는 성공이 아닙니다.

```sh
python tools/test_firmware_tools.py
python tools/test_build_verifier.py
python tools/test_layouts.py --cpp arm-none-eabi-gcc
cc -std=c11 -Wall -Wextra -Werror -Isrc tests/test_scan_core.c -o test-scan
./test-scan
```

배열 전처리 검사는 16조합, 네이티브 검사는 직렬 프로토콜과 디바운스를 확인합니다. 전체 ZMK 빌드 및 실기기 시험과 함께 사용합니다.

## 포팅 기록과 다음 작업

[포팅 기록](dev/porting-notes.md)에 근거, 발생한 문제, 수정 내용과 재사용할 교훈을 정리했습니다. 상세 자료는 [리버싱 기록](analysis/reverse-engineering.txt)과 [USB/LED 조사 이력](analysis/usb-bringup.md)에 남아 있습니다.

다음 개발은 개인 키맵과 그림을 좌표에 맞춰 이식하는 작업입니다. 장시간 입력·동시 키·반복 재연결 검증도 이어갑니다. Studio와 영구 저장은 별도의 플래시/RAM 설계가 필요하며 남는 공간만으로 자동 활성화하지 않습니다.
