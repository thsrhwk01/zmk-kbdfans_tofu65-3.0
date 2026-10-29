# USB bring-up: Windows Code 10

## Observed evidence (2026-10-29)

- First firmware: source `02f5fab`, Actions run `40863318758`.
- Windows read VID `1D50`, PID `615E`, then HidUsb failed to start with Code 10 / `0xC0000001`.
- The supplied Device Manager screenshot confirms the error, but does not identify its cause.
- The device returned to its factory UniCore-F1 UF2 bootloader.
- Readback saved locally as `build/ci/device-after-code10.uf2`: the application bytes exactly match `dist/40863318758/zmk.bin` (SHA-256 `b3d3d97c512e6c829161e7c414bd809adcdc4a2f324f3468faaf830106143ac2`).
- Readback bootloader (first 16 KiB) and settings (last 8 KiB) match the original snapshot exactly. This rules out a corrupted application upload for that attempt.

## Changes under test

The scanner previously masked interrupts during all 225 clock pulses and 113 input-settle intervals. Configured delays alone total 676 microseconds, before GPIO operations and timing-call overhead. USB was blocked throughout. The new worker masks interrupts only while each clock pulse is high, allowing USB service between pulses; minimum low/settle delays and the serial sequence remain unchanged. Hardware must confirm that longer inter-pulse gaps are tolerated.

ZMK's pinned defaults enable USB at APPLICATION priority 94 and register HID at 95. The board now registers HID at 93 before enabling USB at 94, eliminating the possibility of host requests arriving before report descriptors/callbacks exist. This is a startup-order correction, not proof of the Code 10 root cause.

## Firmware choices and next checks

1. Test the `normal` artifact first: USB enumeration, typing, modifiers, reconnect, physical double-tap recovery.
2. If Code 10 persists, use the `usb-diagnostic` artifact. It retains the same HID descriptors and initial GPIO setup but never schedules periodic scanning. It deliberately cannot type.
3. Diagnostic success would implicate interaction with periodic scanning; diagnostic failure would mean periodic scanning alone does not explain the problem. Next investigate control transfers, clock/PHY behavior, and HID descriptors with bus-level evidence.

No driver replacement, device uninstall, or automatic firmware flashing was performed. Neither revised variant has passed a hardware test yet. Compilation success is not hardware validation.

## User hardware confirmation after the USB fix

The user flashed `771dfc0` normal firmware from run `40866143846` and confirmed USB enumeration and typing. Subsequent switch-pad shorting confirmed expected keycodes for all tested non-split positions, including ANSI/ISO Enter pads, stepped Caps Lock, and 7u bottom-row Ctrl/Alt/GUI pads. Split Backspace and split Left Shift extra positions were disabled in that build and remain to be tested with both options enabled.

The existing Fn + top-right Delete binding uses the target-specific UniCore SRAM marker/reset behavior; Fn + Esc is reset only. This matches Neo65 CU's layer-based shortcut approach without copying its STM32F072 ROM address or entry procedure. Software UF2 entry, reconnect stability, and the two newly enabled split positions still require hardware confirmation.

## Split-key and LED observations

The user confirmed both additional split keys produce their assigned keycodes on build `5475ca9`. The user also observed RGB changing color in UF2 bootloader mode, then remaining on the last color after flashing; unplug/replug clears it. This strongly supports a latched LED state rather than an intentional Caps Lock indication.

Stock `0x08009e30` configures PB15 as output. `0x08009db4` serializes each byte MSB-first with different high/low durations for 0 and 1. `0x08009e40` sends three bytes per pixel then a low latch interval. `0x0800635c` stores G,R,B order; `0x08006370` sends black. `0x080063e8` tests HID Caps Lock bit 1; `0x0800637c` applies the indicator color and sets/clears PB14. Scanner startup also initializes PB14 and PA8 low. Bootloader `0x0800368` sends a changing 24-bit pattern on PB15 and also toggles PB14/PA8. Existing ZMK did not transmit any RGB frame, allowing the last LED color to remain powered.

The new indicator sends black at POST_KERNEL priority 91 (before USB connects), then uses ZMK's host HID indicator event to display dim white for Caps Lock. PA8/PB14 startup levels match stock; PB14 follows the stock Caps Lock state. The byte transmitter preserves the recovered stock instruction sequence for the established 48 MHz clock. Only the 24-bit transfer masks interrupts; 300 us low latch waits do not. RGB model, physical pulse widths, and actual new LED behavior remain unmeasured. Verify both bootloader-to-ZMK startup and cold boot, Caps Lock on/off from the host (including another keyboard), and typing/USB stability.
