# KBDfans TOFU65 3.0 ZMK

[English](README.md)

KBDfans TOFU65 3.0 유선 핫스왑 UniCore-F1 PCB용 기본 키맵입니다. USB 전용이며 공장 UF2 부트로더와 순정 설정 영역을 보존합니다.

## 설치

1. [Releases](https://github.com/thsrhwk01/zmk-kbdfans_tofu65-3.0/releases/latest)에서 `tofu65_3_0-zmk-normal.uf2`과 `SHA256SUMS.txt`를 받습니다.
2. 기판 버튼을 두 번 누르거나 **Fn + 맨 오른쪽 상단 Delete**로 UF2 모드에 진입합니다.
3. UF2를 `UniCore-F1`에 복사하고 재시작을 기다립니다. 필요하면 복사 완료 후 USB를 다시 연결합니다.

일반 펌웨어를 사용하세요. `usb-diagnostic`은 키 스캔이 꺼진 진단판입니다.

## 기능과 키맵

- 백스페이스·좌시프트 분할, ANSI/ISO 엔터, 6.25u/7u 하단 배열 지원.
- Caps Lock LED: 활성화 시 약한 흰색, 부팅 시 초기화.
- NKRO 기본 비활성화, 표준 6키 롤오버 사용.

| 키 | 동작 |
| --- | --- |
| Fn + 맨 오른쪽 상단 Delete | UF2 부트로더 |
| Fn + Esc | 물결표 (`~`) |
| Fn + 1…0, Minus, Equal | F1…F12 |
| 분할 백스페이스 추가 키 | Delete |
| 분할 좌시프트 추가 키 | NUBS / IntlBackslash |

Fn은 왼쪽 화살표 바로 왼쪽 키입니다. 기본값은 분할 두 옵션 활성화, ANSI 엔터, 6.25u입니다. [배열 옵션](config/layout-options.h)과 [키맵](config/tofu65_3_0.keymap)을 수정한 뒤 다시 빌드합니다.

## 검증과 지원 범위

2026-11-01 사용자 테스트 완료: USB, 키 입력과 대체 패드, Caps Lock LED, 부트로더 진입. [검증 기록](analysis/hardware-validation.json). CI는 배열 16조합을 검사하며, 모든 조합을 실조립한 것은 아닙니다.

대상 Board ID는 `ARM32F103-UniCore-F1-v1.x`입니다. VIA/Vial, ZMK Studio, 무선, 영구 설정 저장은 지원하지 않습니다.

## 개발과 복구

- [빌드·테스트 방법](dev/build.md) — ZMK v0.3.0 고정, 로컬 빌드와 CI 검사.
- [포팅 기록](dev/porting-notes.md) — 리버싱, 발생한 문제와 해결 과정.
- [USB/LED 조사 이력](analysis/usb-bringup.md).

최초 순정 백업을 보관하세요. 추출한 `CURRENT.UF2`는 직접 플래싱할 수 없습니다. [재패키징한 순정 복구 파일](analysis/stock-application-recovery.UNTESTED.uf2)은 부트로더를 보존하고 최초 앱·설정을 복원합니다. 원본 내용 일치는 검증했으나 실기 복구 성공은 미확인입니다.
