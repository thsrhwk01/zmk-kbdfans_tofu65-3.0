"""Package a TOFU65 UniCore-F1 application locally; never access a device."""

import argparse
import hashlib
import json
from pathlib import Path
import struct

APP_BASE = 0x08004000
SETTINGS_BASE = 0x0801E000
FLASH_END = 0x08020000
FAMILY = 0x9D5BCF10
STOCK_HASH = "be6f662de85df5af75fd977df4650df08b53f48c9b66951f031ba09c6463cc71"


def package(payload, end=SETTINGS_BASE):
    if not 8 <= len(payload) <= end - APP_BASE:
        raise ValueError("Application length exceeds the allowed code partition")
    sp, reset = struct.unpack_from("<II", payload)
    sram_end = 0x20005000 if end == FLASH_END else 0x20004000
    if not 0x20000000 < sp <= sram_end or sp % 8:
        raise ValueError("Invalid F103-class initial stack pointer")
    if not reset & 1 or not APP_BASE <= (reset & ~1) < APP_BASE + len(payload):
        raise ValueError("Reset handler must point inside this application at 0x08004000")
    padded = payload + b"\xff" * (-len(payload) % 256)
    if APP_BASE + len(padded) > end:
        raise ValueError("UF2 padding would cross the partition boundary")
    total = len(padded) // 256
    result = bytearray()
    for index in range(total):
        result.extend(struct.pack("<8I", 0x0A324655, 0x9E5D5157, 0x2000,
                                  APP_BASE + index * 256, 256, index, total, FAMILY))
        result.extend(padded[index * 256:(index + 1) * 256])
        result.extend(bytes(220))
        result.extend(struct.pack("<I", 0x0AB16F30))
    return bytes(result)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--application-bin", type=Path, help="Raw application linked at 0x08004000")
    inputs.add_argument("--stock-flash-bin", type=Path, help="Exact original extracted 128 KiB snapshot")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.stock_flash_bin:
        source = args.stock_flash_bin.read_bytes()
        if hashlib.sha256(source).hexdigest() != STOCK_HASH:
            raise ValueError("Stock recovery requires the verified original snapshot")
        payload = source[APP_BASE - 0x08000000:]
        end = FLASH_END
        kind = "stock application plus original settings; excludes bootloader; UNTESTED"
    else:
        payload = args.application_bin.read_bytes()
        end = SETTINGS_BASE
        kind = "application only; preserves bootloader and stock settings; UNTESTED"
    result = package(payload, end)
    # Exclusive creation avoids silently replacing a prior firmware artifact.
    with args.output.open("xb") as stream:
        stream.write(result)
    manifest = {"kind": kind, "hardware_tested": False, "base": hex(APP_BASE),
                "payload_length": len(payload), "uf2_length": len(result),
                "family_id": hex(FAMILY), "sha256": hashlib.sha256(result).hexdigest()}
    args.output.with_suffix(args.output.suffix + ".json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
