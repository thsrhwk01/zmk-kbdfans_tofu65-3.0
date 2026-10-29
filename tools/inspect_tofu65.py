"""Extract address-specific evidence from the supplied TOFU65 stock snapshot."""

import csv
import hashlib
import json
import lzma
from pathlib import Path
import struct


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "analysis"
EXPECTED = "be6f662de85df5af75fd977df4650df08b53f48c9b66951f031ba09c6463cc71"


def inspect():
    data = (OUT / "current-flash.bin").read_bytes()
    if hashlib.sha256(data).hexdigest() != EXPECTED:
        raise ValueError("Address-specific analysis requires the original verified snapshot")
    dec = lzma.LZMADecompressor(memlimit=64 * 1024 * 1024)
    unpacked = dec.decompress(data[0xF512:], max_length=1024 * 1024)
    if not dec.eof:
        raise ValueError("Incomplete or oversized Vial definition")
    definition = json.loads(unpacked)
    (OUT / "vial-definition.json").write_text(json.dumps(definition, indent=2) + "\n", encoding="utf-8")
    compressed_size = len(data) - 0xF512 - len(dec.unused_data)
    labels = [
        "ESC 1 2 3 4 5 6 7 8 9 0 MINUS EQUAL BACKSPACE DELETE".split(),
        "TAB Q W E R T Y U I O P LBRACKET RBRACKET BACKSLASH PGUP".split(),
        "CAPS A S D F G H J K L SEMICOLON APOSTROPHE ENTER PGDN".split(),
        "LSHIFT Z X C V B N M COMMA DOT SLASH RSHIFT UP END".split(),
        "LCTRL LGUI LALT SPACE RALT RGUI LEFT DOWN RIGHT".split(),
    ]
    rows = []
    for physical_row, items in enumerate(definition["layouts"]["keymap"]):
        selected = []
        decoration = False
        for item in items:
            if isinstance(item, dict):
                decoration = item.get("d", False)
                continue
            parts = item.split("\n\n\n")
            include = not decoration and (len(parts) == 1 or parts[1].split(",")[1] == "0")
            decoration = False
            if include:
                row, col = map(int, parts[0].split(","))
                selected.append((row, col))
        if not selected:
            continue
        if physical_row >= len(labels) or len(selected) != len(labels[physical_row]):
            raise ValueError("Unexpected default layout")
        for label, (row, col) in zip(labels[physical_row], selected):
            rows.append({"position": len(rows), "label": label, "physical_row": physical_row,
                         "matrix_row": row, "matrix_col": col, "serial_index": row * 8 + col})
    if len(rows) != 67 or len({r["serial_index"] for r in rows}) != 67:
        raise ValueError("Invalid ANSI layout mapping")
    with (OUT / "ansi-matrix.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    transform = ["/* Recovered stock default ANSI mapping; not a standalone board definition. */",
                 "/* Logical matrix: 14 rows x 8 columns; serial index = row * 8 + column. */",
                 "map = <"]
    for row in range(5):
        transform.append("    " + " ".join(f"RC({p['matrix_row']},{p['matrix_col']})" for p in rows if p["physical_row"] == row))
    transform.append(">;")
    (OUT / "ansi-transform.dtsi").write_text("\n".join(transform) + "\n", encoding="utf-8")
    gpio = {}
    for index, port in enumerate("ABCDE"):
        odr, crl, crh = struct.unpack_from("<III", data, 0xFDA0 + index * 12)
        gpio[port] = {"odr": hex(odr), "crl": hex(crl), "crh": hex(crh)}
    result = {
        "payload_sha256": EXPECTED,
        "application_start": "0x08004000",
        "application_reset_handler": "0x08004239",
        "bootloader_handoff": "0x08000644",
        "uf2_write_handler": "0x08000bb0",
        "required_upload_flags": "0x00002000",
        "required_upload_family": "0x9d5bcf10",
        "accepted_upload_range": ["0x08004000", "0x08020000 (exclusive)"],
        "upload_address_alignment": 256,
        "upload_max_payload": 256,
        "stock_settings_range": ["0x0801e000", "0x08020000 (exclusive)"],
        "recommended_initial_code_limit": "0x0801e000 (exclusive; preserve stock settings)",
        "boot_request_address": "0x20004000",
        "boot_request_magic": "0x9d5bfc2b",
        "bootloader_usb_vid_pid": "1209:db42",
        "application_usb_vid_pid": "9d5b:2505",
        "vial_address": "0x0800f512",
        "vial_compressed_bytes": compressed_size,
        "vial_uncompressed_bytes": len(unpacked),
        "logical_matrix": definition["matrix"],
        "default_ansi_keys": len(rows),
        "scanner_address": "0x08006168",
        "scanner_initialization": "0x0800606c",
        "serial_clock_pin": "PB12",
        "serial_bidirectional_data_pin": "PB13",
        "serial_sample_polarity": "low is active",
        "scan_bits": 112,
        "gpio_initial_values_address": "0x0800fda0",
        "gpio_initial_values": gpio,
        "gpio_mode_translation_address": "0x0800fd6a",
        "gpio_mode_translation": list(data[0xFD6A:0xFD72]),
        "clock_init_address": "0x0800e7f8",
        "clock_cfgr_configuration_excluding_readonly_sws": "0x00684402",
        "clock_interpretation": "STM32F103 register model: HSI/2 x 12, SYSCLK 48 MHz, APB1 24 MHz, USB PLL/1",
        "hardware_tested": False,
    }
    (OUT / "tofu65-evidence.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    inspect()
