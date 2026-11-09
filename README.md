# KBDfans TOFU65 3.0 ZMK

[한국어](README_ko.md)

Default keymap for the KBDfans TOFU65 3.0 wired hotswap UniCore-F1 PCB. USB only; preserves the factory UF2 bootloader and stock settings.

## Install

1. Download `tofu65_3_0-zmk-normal.uf2` and `SHA256SUMS.txt` from [Releases](https://github.com/thsrhwk01/zmk-kbdfans_tofu65-3.0/releases/latest).
2. Double-tap the PCB button, or press **Fn + top-right Delete**, to enter UF2 mode.
3. Copy the UF2 to `UniCore-F1` and wait for restart. Reconnect USB if needed after copying finishes.

Use the normal firmware; `usb-diagnostic` builds intentionally disable key scanning.

## Features and keymap

- Split Backspace/Left Shift, ANSI/ISO Enter, 6.25u/7u bottom row.
- Caps Lock LED: dim white when on; cleared at startup.
- NKRO is not enabled by default; standard 6-key rollover is used.

| Key | Action |
| --- | --- |
| Fn + top-right Delete | UF2 bootloader |
| Fn + Esc | Tilde (`~`) |
| Fn + 1…0, Minus, Equal | F1…F12 |
| Extra split Backspace | Delete |
| Extra split Left Shift | NUBS / IntlBackslash |

Fn is immediately left of Left Arrow. Defaults: both splits enabled, ANSI Enter, 6.25u. Edit [layout options](config/layout-options.h) and [keymap](config/tofu65_3_0.keymap), then rebuild.

## Validation and scope

Owner testing completed on 2026-11-01: USB, key input and alternative pads, Caps Lock LED and bootloader entry. [Validation record](analysis/hardware-validation.json). CI checks all 16 layout combinations; not every combination was physically assembled.

Targets Board ID `ARM32F103-UniCore-F1-v1.x`. VIA/Vial, ZMK Studio, wireless and persistent settings are not supported.

## Development and recovery

- [Build and tests](dev/build.md) — pinned ZMK v0.3.0, local build and CI checks.
- [Porting notes](dev/porting-notes.md) — reverse engineering, problems and fixes.
- [USB/LED investigation](analysis/usb-bringup.md).

Keep the original factory backup. Exported `CURRENT.UF2` is not directly flashable. The [repacked stock recovery](analysis/stock-application-recovery.UNTESTED.uf2) restores the original application and settings while preserving the bootloader; its payload is verified, but hardware restoration is not confirmed.
