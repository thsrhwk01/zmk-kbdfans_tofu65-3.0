"""Reject ELF/BIN artifacts outside the experimental TOFU65 flash/RAM partitions."""
import argparse
import hashlib
import json
from pathlib import Path
import struct

from package_uf2 import APP_BASE, SETTINGS_BASE, package


def verify(elf_path, bin_path, config_path):
    elf = elf_path.read_bytes()
    binary = bin_path.read_bytes()
    if len(elf) < 52 or len(binary) < 8 or elf[:7] != b"\x7fELF\x01\x01\x01":
        raise ValueError("Expected little-endian ELF32")
    if struct.unpack_from("<HH", elf, 16) != (2, 40):
        raise ValueError("Expected ARM executable")
    entry, = struct.unpack_from("<I", elf, 24)
    reset, = struct.unpack_from("<I", binary, 4)
    if entry & ~1 != reset & ~1:
        raise ValueError("ELF entry and BIN reset handler disagree")
    phoff, = struct.unpack_from("<I", elf, 28)
    phsize, phnum = struct.unpack_from("<HH", elf, 42)
    if phsize != 32 or not phnum or phoff + phsize * phnum > len(elf):
        raise ValueError("Invalid ELF program table")
    load_segments = []
    for index in range(phnum):
        kind, offset, vaddr, paddr, filesz, memsz, _, _ = struct.unpack_from("<8I", elf, phoff + index * 32)
        if kind != 1:
            continue
        if filesz > memsz or offset + filesz > len(elf):
            raise ValueError("Invalid ELF load segment")
        if not ((APP_BASE <= vaddr and vaddr + memsz <= SETTINGS_BASE) or
                (0x20000000 <= vaddr and vaddr + memsz <= 0x20004000)):
            raise ValueError("ELF load segment exceeds memory partitions")
        if filesz:
            if not APP_BASE <= paddr < paddr + filesz <= SETTINGS_BASE:
                raise ValueError("ELF load image is outside the flash code partition")
            load_segments.append((offset, paddr, filesz))
    shoff, = struct.unpack_from("<I", elf, 32)
    shsize, shnum = struct.unpack_from("<HH", elf, 46)
    if shsize != 40 or not shnum or shoff + shsize * shnum > len(elf):
        raise ValueError("Invalid ELF section table")
    flash_start = SETTINGS_BASE
    ram_end = 0x20000000
    for index in range(shnum):
        _, kind, flags, address, offset, size, *_ = struct.unpack_from("<10I", elf, shoff + index * 40)
        if not flags & 2 or not size:
            continue
        if APP_BASE <= address and address + size <= SETTINGS_BASE:
            flash_start = min(flash_start, address)
        elif 0x20000000 <= address and address + size <= 0x20004000:
            ram_end = max(ram_end, address + size)
        else:
            raise ValueError(f"Allocated section outside partitions: {address:#x}+{size:#x}")
        if kind != 8:  # SHT_NOBITS has no file contents. Compare every other allocated section.
            matches = [(paddr + offset - poffset) for poffset, paddr, filesz in load_segments
                       if poffset <= offset and offset + size <= poffset + filesz]
            if len(matches) != 1 or offset + size > len(elf):
                raise ValueError("Allocated section has no unique flash load image")
            load_address = matches[0]
            if binary[load_address - APP_BASE:load_address - APP_BASE + size] != elf[offset:offset + size]:
                raise ValueError(f"ELF section and BIN disagree at load address {load_address:#x}")
    if flash_start != APP_BASE:
        raise ValueError("ELF does not start at the factory application boundary")
    config = config_path.read_text()
    for setting in ("CONFIG_USE_DT_CODE_PARTITION", "CONFIG_INIT_ARCH_HW_AT_BOOT",
                    "CONFIG_PLATFORM_SPECIFIC_INIT", "CONFIG_ZMK_USB", "CONFIG_TOFU65_UNICORE"):
        if f"{setting}=y\n" not in config:
            raise ValueError(f"Required setting missing: {setting}")
    for setting in ("CONFIG_SETTINGS", "CONFIG_ZMK_STUDIO", "CONFIG_ZMK_BLE"):
        if f"{setting}=y\n" in config:
            raise ValueError(f"Unsupported bring-up setting: {setting}")
    package(binary)  # Also check vector bounds, initial stack, and padded size.
    return {"hardware_tested": False, "bin_size": len(binary),
            "bin_sha256": hashlib.sha256(binary).hexdigest(),
            "elf_sha256": hashlib.sha256(elf).hexdigest(), "entry": hex(entry),
            "allocated_ram_end": hex(ram_end), "code_limit": hex(SETTINGS_BASE)}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--elf", type=Path, required=True)
    parser.add_argument("--bin", type=Path, required=True)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = verify(args.elf, args.bin, args.config)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
