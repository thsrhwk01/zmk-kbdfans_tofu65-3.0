# KBDfans TOFU65 3.0 Wired ZMK Firmware

[한국어](README_ko.md)

USB-only ZMK firmware for the **KBDfans TOFU65 3.0 wired hotswap UniCore-F1 PCB**. The port was developed from the board-exported factory UF2 snapshot and preserves its flash bootloader and stock settings.

## Features

- Custom PB12/PB13 bidirectional serial scanner: 112 stages, 69 mapped switch positions
- Split Backspace, split Left Shift, ANSI/ISO Enter, and 6.25u/7u layout choices
- Host-controlled Caps Lock RGB indicator, dim white when enabled
- Black RGB frame at startup to clear the bootloader's last color
- Fn + Delete entry into the factory UF2 bootloader
- Pinned ZMK source, automated tests, ELF/BIN memory checks, and UF2 packaging

The personal Windows/macOS, home-row, and mouse keymaps from the sibling projects have **not yet been ported**. VIA/Vial configuration, ZMK Studio, wireless, persistent settings, and runtime color selection are not implemented.

## Supported hardware

| Item | Target / evidence |
| --- | --- |
| PCB | TOFU65 3.0 wired hotswap, UniCore-F1 |
| Board ID | `ARM32F103-UniCore-F1-v1.x` |
| Bootloader | `v24.07.23i`, `UniCore-F1` UF2 volume |
| Zephyr SoC configuration | STM32F103xB-compatible; physical MCU marking not confirmed |
| Flash | 128 KiB in the exported snapshot; ZMK code partition 104 KiB |
| SRAM used by ZMK | Lower 16 KiB; boot request at `0x20004000` reserved |
| Clock | HSI/2 × 12 = 48 MHz, USB PLL/1 |
| Connection | USB only |

These addresses and pins apply to this observed PCB, not every keyboard bearing the TOFU name. MCU vendor and exact LED part number remain unconfirmed.

## Verified firmware

Hardware observations were reported by the owner on 2026-10-29. The current tested baseline includes the split-key configuration and Caps Lock indicator.

| Item | Value |
| --- | --- |
| Source commit | `8f92936e28cb3d0207dd13631b5caf775f3328aa` |
| Actions run | [40869663384](https://github.com/thsrhwk01/zmk-kbdfans_tofu65-3.0/actions/runs/40869663384) |
| Artifact | `TOFU65-3.0-ZMK-normal-EXPERIMENTAL` |
| File | `tofu65_3_0-zmk-normal-UNTESTED.uf2` |
| UF2 size | 73,216 bytes |
| UF2 SHA-256 | `d2f47a4ee2df1ad861b695805dfa5e1d84c762ff4e1597ca9b412282e6f411b3` |
| Application / allocated RAM | 36,588 bytes / 10,376 bytes |

Confirmed: USB enumeration and typing; both extra split keys; expected keycodes on tested ANSI/ISO Enter, stepped Caps Lock and 7u bottom-row pads; Caps Lock LED; Fn + Delete bootloader entry. The owner currently notices no missed input. This is not a measured latency or long-duration endurance result. Alternative-pad testing does not mean all 16 compiled layout combinations were physically assembled and tested.

`UNTESTED` remains the automatic packaging filename: CI cannot certify each new build on hardware. The baseline above identifies the specific owner-tested build. Check the UF2 hash, not the ZIP hash.

## Quick install on Windows

1. Open the verified run above, or a successful [build workflow](https://github.com/thsrhwk01/zmk-kbdfans_tofu65-3.0/actions/workflows/build.yml).
2. Download `TOFU65-3.0-ZMK-normal-EXPERIMENTAL` and extract it. The `usb-diagnostic` artifact deliberately does not scan keys.
3. Optionally compare the UF2 against the package's `SHA256SUMS.txt`:

   ```powershell
   Get-FileHash .\tofu65_3_0-zmk-normal-UNTESTED.uf2 -Algorithm SHA256
   ```

4. Enter UF2 mode with the PCB's double-tap button, or Fn + top-right Delete while ZMK is running.
5. Copy only the generated `.uf2` to the `UniCore-F1` volume. Wait for copying to finish and the application to restart; reconnect USB if needed after copying completes.
6. Check typing and Caps Lock indication. Save the original factory snapshot separately.

No QMK Toolbox, dfu-util, or driver replacement is required for this mass-storage upload method. Do not copy the exported original `CURRENT.UF2` as a recovery upload; see below.

## Keymap and shortcuts

The current default enables both split options, with ANSI Enter and a 6.25u bottom row. Edit [config/layout-options.h](config/layout-options.h), then rebuild:

```c
#define TOFU_SPLIT_BACKSPACE 1
#define TOFU_ISO_ENTER 0
#define TOFU_SPLIT_LSHIFT 1
#define TOFU_SPACE_7U 0
```

| Key / combination | Action |
| --- | --- |
| Original Backspace / Left Shift | Backspace / Left Shift |
| Extra split Backspace | Delete |
| Extra split Left Shift | NUBS (`IntlBackslash`; character depends on host layout) |
| Fn + top-right Delete | Factory UF2 entry, owner-confirmed |
| Fn + Esc | ZMK application reset |
| Fn + 1…0, Minus, Equal | F1…F12 |

Fn is the bottom-row key immediately left of Left Arrow (matrix `7,2`). Boot entry uses top-right Delete (`6,3`), **not** the additional split Backspace key. Layer bindings avoid combo waiting delays.

The owner also reported returning from bootloader to ZMK after Fn + Esc. The implemented binding belongs to ZMK; the factory bootloader does not execute this keymap. Treat that report as an observed return, not a guaranteed bootloader-side shortcut. USB reconnection remains the documented fallback.

[config/tofu65_3_0.keymap](config/tofu65_3_0.keymap) imports the generated default from [include/](include/). Keep personal keymaps in `config/`; `tools/generate_layout.py` may regenerate the default. All layouts retain 69 logical positions. ISO exchanges the Enter-area bindings; 7u disables the unused right-Alt position.

## Bootloader preservation and recovery

| Region | Range | Normal ZMK upload |
| --- | --- | --- |
| Factory bootloader | `0x08000000`–`0x08003FFF` | Preserved |
| Application | `0x08004000`–`0x0801DFFF` | Code only |
| Factory settings | `0x0801E000`–`0x0801FFFF` | Preserved |
| ZMK SRAM | `0x20000000`–`0x20003FFF` | Allocated RAM |

The application offset is supported by the factory bootloader's branch code. Normal packaging enforces the code boundary, stack/reset vectors, and UF2 Family ID `0x9D5BCF10`.

For stock recovery, enter the physical UF2 bootloader and copy [stock-application-recovery.UNTESTED.uf2](analysis/stock-application-recovery.UNTESTED.uf2). It contains the original application **and original settings**, excludes the bootloader, and sets upload-compatible UF2 headers. Its payload was verified against the original snapshot; successful stock restoration has not been explicitly reported. Original `CURRENT.UF2` has flags/family zero and includes bootloader blocks, so it is a readback format, not a directly accepted restore image.

## Build and verification

ZMK is pinned to `edf5c0814fd3ea202e43aad2d68fd32e882a518c` (v0.3.0). Each artifact includes `manifest-frozen.yml`, ELF/BIN, map files, resolved config/DTS, layout choices, verification report and SHA-256 checksums. The workflow builds normal and no-scan diagnostic variants; it does not publish tagged Releases or flash a device.

With Python, west, CMake, Ninja and a compatible ARM/Zephyr toolchain installed:

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

On Windows, after initializing the west workspace, [tools/build.ps1](tools/build.ps1) also verifies and packages the build locally:

```powershell
./tools/build.ps1 -FirmwareWorkspace 'D:/path/to/firmware-workspace'
python tools/watch_actions.py --sha (git rev-parse HEAD) --interval 180
```

The watcher returns 0 for success, 1 for failure, 2 for timeout. A timeout is not success.

```sh
python tools/test_firmware_tools.py
python tools/test_build_verifier.py
python tools/test_layouts.py --cpp arm-none-eabi-gcc
cc -std=c11 -Wall -Wextra -Werror -Isrc tests/test_scan_core.c -o test-scan
./test-scan
```

Layout preprocessing covers 16 combinations; native tests cover the serial sequence and debounce. These checks complement the full ZMK build and hardware testing.

## Porting notes and remaining work

Read [the porting notes (Korean)](dev/porting-notes.md) for the evidence, mistakes, fixes and transferable lessons. [Reverse-engineering details](analysis/reverse-engineering.txt) and [USB/LED investigation history](analysis/usb-bringup.md) retain the lower-level observations.

Next: port the personal keymap and diagrams by coordinates, then check extended typing, simultaneous-key combinations and repeated reconnects. Studio/persistent storage require a separate flash/RAM design; they are not enabled implicitly by available space.
