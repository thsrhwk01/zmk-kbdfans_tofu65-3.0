"""Exercise the artifact gate with a small synthetic ELF, never a flashable build."""
from pathlib import Path
import struct
import tempfile
import unittest

from verify_build import verify


class BuildVerifierTest(unittest.TestCase):
    def fixture(self):
        binary = struct.pack("<II", 0x20000400, 0x08004009) + b"\x00\xbf" * 12
        elf = bytearray(0x200)
        elf[:7] = b"\x7fELF\x01\x01\x01"
        struct.pack_into("<HHIIIIIHHHHHH", elf, 16,
                         2, 40, 1, 0x08004009, 52, 0x100, 0, 52, 32, 1, 40, 3, 0)
        struct.pack_into("<8I", elf, 52, 1, 0x80, 0x08004000, 0x08004000, 32, 32, 5, 4)
        elf[0x80:0xa0] = binary
        struct.pack_into("<10I", elf, 0x128, 0, 1, 6, 0x08004000, 0x80, 32, 0, 0, 4, 0)
        struct.pack_into("<10I", elf, 0x150, 0, 8, 3, 0x20000000, 0, 0x400, 0, 0, 4, 0)
        return elf, bytearray(binary)

    def run_verify(self, elf, binary, extra_config=""):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "test.elf").write_bytes(elf)
            (root / "test.bin").write_bytes(binary)
            config = "".join(name + "=y\n" for name in (
                "CONFIG_USE_DT_CODE_PARTITION", "CONFIG_INIT_ARCH_HW_AT_BOOT",
                "CONFIG_PLATFORM_SPECIFIC_INIT", "CONFIG_ZMK_USB", "CONFIG_TOFU65_UNICORE"))
            (root / "test.config").write_text(config + extra_config)
            return verify(root / "test.elf", root / "test.bin", root / "test.config")

    def test_valid(self):
        self.assertEqual(self.run_verify(*self.fixture())["bin_size"], 32)

    def test_bootloader_section_rejected(self):
        elf, binary = self.fixture()
        struct.pack_into("<I", elf, 0x128 + 12, 0x08000000)
        with self.assertRaises(ValueError):
            self.run_verify(elf, binary)

    def test_ram_marker_overlap_rejected(self):
        elf, binary = self.fixture()
        struct.pack_into("<I", elf, 0x150 + 12, 0x20004000)
        with self.assertRaises(ValueError):
            self.run_verify(elf, binary)

    def test_settings_load_address_rejected(self):
        elf, binary = self.fixture()
        struct.pack_into("<I", elf, 52 + 12, 0x0801e000)
        with self.assertRaises(ValueError):
            self.run_verify(elf, binary)

    def test_mismatched_bin_rejected(self):
        elf, binary = self.fixture()
        binary[20] ^= 1
        with self.assertRaises(ValueError):
            self.run_verify(elf, binary)

    def test_persistent_settings_rejected(self):
        with self.assertRaises(ValueError):
            self.run_verify(*self.fixture(), extra_config="CONFIG_SETTINGS=y\n")

    def test_segment_padding_is_not_section_data(self):
        elf, binary = self.fixture()
        # PT_LOAD includes trailing padding beyond the 32-byte code section.
        struct.pack_into("<II", elf, 52 + 16, 36, 36)
        binary.extend(b"\xff" * 4)
        self.assertEqual(self.run_verify(elf, binary)["bin_size"], 36)

    def test_initialized_ram_uses_flash_load_address(self):
        elf, binary = self.fixture()
        struct.pack_into("<H", elf, 44, 2)
        struct.pack_into("<8I", elf, 84, 1, 0xa0, 0x20000000, 0x08004020, 4, 4, 6, 4)
        struct.pack_into("<10I", elf, 0x150, 0, 1, 3, 0x20000000, 0xa0, 4, 0, 0, 4, 0)
        elf[0xa0:0xa4] = b"DATA"
        binary.extend(b"DATA")
        self.run_verify(elf, binary)
        binary[-1] ^= 1
        with self.assertRaises(ValueError):
            self.run_verify(elf, binary)


if __name__ == "__main__":
    unittest.main()
