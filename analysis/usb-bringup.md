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
