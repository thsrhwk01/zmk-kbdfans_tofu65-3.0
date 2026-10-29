"""Offline corruption/bounds tests. No keyboard or USB access."""

import contextlib
import io
from pathlib import Path
import struct
import tempfile
import unittest

from analyze_uf2 import analyze
from package_uf2 import APP_BASE, SETTINGS_BASE, package


class FirmwareToolsTest(unittest.TestCase):
    def payload(self, length=300):
        data = bytearray(length)
        struct.pack_into("<II", data, 0, 0x20000400, APP_BASE + 9)
        return bytes(data)

    def extract(self, blob):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.uf2"
            source.write_bytes(blob)
            with contextlib.redirect_stdout(io.StringIO()):
                analyze(source, root / "output")
            return (root / "output/current-flash.bin").read_bytes()

    def test_roundtrip_and_family(self):
        payload = self.payload()
        blob = package(payload)
        self.assertEqual(struct.unpack_from("<I", blob, 8)[0], 0x2000)
        self.assertEqual(struct.unpack_from("<I", blob, 28)[0], 0x9D5BCF10)
        self.assertEqual(self.extract(blob), payload + b"\xff" * 212)

    def test_reordered_blocks(self):
        blob = package(self.payload())
        self.assertEqual(self.extract(blob[512:] + blob[:512]), self.extract(blob))

    def test_corrupt_magic(self):
        blob = bytearray(package(self.payload()))
        blob[508] ^= 1
        with self.assertRaises(ValueError):
            self.extract(blob)

    def test_duplicate_number(self):
        blob = bytearray(package(self.payload()))
        struct.pack_into("<I", blob, 512 + 20, 0)
        with self.assertRaises(ValueError):
            self.extract(blob)

    def test_overlap(self):
        blob = bytearray(package(self.payload()))
        struct.pack_into("<I", blob, 512 + 12, APP_BASE)
        with self.assertRaises(ValueError):
            self.extract(blob)

    def test_settings_boundary(self):
        with self.assertRaises(ValueError):
            package(self.payload(SETTINGS_BASE - APP_BASE + 1))

    def test_wrong_link_address(self):
        blob = bytearray(self.payload())
        struct.pack_into("<I", blob, 4, 0x08000009)
        with self.assertRaises(ValueError):
            package(blob)

    def test_invalid_stack(self):
        blob = bytearray(self.payload())
        struct.pack_into("<I", blob, 0, 0x20006000)
        with self.assertRaises(ValueError):
            package(blob)


if __name__ == "__main__":
    unittest.main()
