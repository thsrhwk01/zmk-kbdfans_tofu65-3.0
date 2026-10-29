"""Validate and extract a UF2 snapshot without accessing keyboard hardware."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess


def analyze(source, output, objdump=None):
    raw = source.read_bytes()
    if not raw or len(raw) % 512:
        raise ValueError("UF2 length must be a nonzero multiple of 512")
    blocks = []
    for offset in range(0, len(raw), 512):
        header = struct.unpack_from("<8I", raw, offset)
        magic0, magic1, flags, address, size, number, total, family = header
        end = struct.unpack_from("<I", raw, offset + 508)[0]
        if (magic0, magic1, end) != (0x0A324655, 0x9E5D5157, 0x0AB16F30):
            raise ValueError(f"Bad magic at file offset {offset:#x}")
        if flags & ~0x2000 or not 0 < size <= 476:
            raise ValueError(f"Unsupported flags or size at block {number}")
        blocks.append((address, number, total, flags, family,
                       raw[offset + 32:offset + 32 + size]))
    count = len(blocks)
    if sorted(b[1] for b in blocks) != list(range(count)) or any(b[2] != count for b in blocks):
        raise ValueError("Missing, duplicated, or inconsistent block numbers")
    blocks.sort()
    base = blocks[0][0]
    data = bytearray()
    for address, *_, payload in blocks:
        if address != base + len(data):
            raise ValueError("Noncontiguous or overlapping payload addresses")
        data.extend(payload)
    output.mkdir(parents=True, exist_ok=True)
    binary = output / "current-flash.bin"
    binary.write_bytes(data)
    vectors = []
    for offset in range(0, len(data) - 64, 128):
        words = struct.unpack_from("<16I", data, offset)
        if 0x20000000 <= words[0] <= 0x20010000 and base <= words[1] < base + len(data) and words[1] & 1:
            vectors.append({"address": hex(base + offset), "initial_sp": hex(words[0]),
                            "reset_handler": hex(words[1]), "words": [hex(w) for w in words]})
    strings = []
    for encoding, pattern in [("ascii", rb"[\x20-\x7e]{6,}"),
                              ("utf-16-le", rb"(?:[\x20-\x7e]\x00){6,}")]:
        for match in re.finditer(pattern, data):
            strings.append({"address": hex(base + match.start()), "encoding": encoding,
                            "text": match.group().decode(encoding)})
    report = {"source": str(source), "source_sha256": hashlib.sha256(raw).hexdigest(),
              "file_size": len(raw), "block_count": count, "base": hex(base),
              "end_exclusive": hex(base + len(data)), "payload_size": len(data),
              "payload_sha256": hashlib.sha256(data).hexdigest(),
              "flags": sorted(set(hex(b[3]) for b in blocks)),
              "family_field": sorted(set(hex(b[4]) for b in blocks)),
              "vector_candidates": vectors, "strings": strings}
    (output / "uf2-analysis.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if objdump:
        result = subprocess.run([str(objdump), "-D", "-b", "binary", "-m", "arm",
                                 "-M", "force-thumb", f"--adjust-vma={base}", str(binary)],
                                check=True, capture_output=True, text=True)
        lines = []
        for line in result.stdout.splitlines():
            literal = re.search(r"\bldr(?:eq|ne|pl|mi|cc|cs|hi|ls|ge|lt|gt|le)?(?:\.w)?\s+.*\[pc,.*@ \(?0x([0-9a-f]+)\)?", line)
            if literal:
                offset = int(literal[1], 16) - base
                if 0 <= offset <= len(data) - 4:
                    line += f" ; literal=0x{struct.unpack_from('<I', data, offset)[0]:08x}"
            lines.append(line)
        (output / "current-flash.disasm.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "strings"}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--output", type=Path, default=Path("analysis"))
    parser.add_argument("--objdump", type=Path)
    args = parser.parse_args()
    analyze(args.source, args.output, args.objdump)
