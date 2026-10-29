"""Preprocess and check all 16 layout choices with GCC's actual C preprocessor."""
import argparse
import itertools
from pathlib import Path
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "boards/arm/tofu65_3_0"
OPTIONS = ["TOFU_SPLIT_BACKSPACE", "TOFU_ISO_ENTER", "TOFU_SPLIT_LSHIFT", "TOFU_SPACE_7U"]


def check(cpp):
    matrix = (BOARD / "tofu65_3_0-matrix.dtsi").read_text()
    coords = [tuple(map(int, pair)) for pair in re.findall(r"RC\((\d+),(\d+)\)", matrix)]
    assert len(coords) == len(set(coords)) == 69
    assert all(0 <= r < 14 and 0 <= c < 8 for r, c in coords)
    # Test binding shape/selection only; these empty includes are NOT a ZMK build.
    with tempfile.TemporaryDirectory() as tmp:
        inc = Path(tmp)
        (inc / "dt-bindings/zmk").mkdir(parents=True)
        (inc / "behaviors.dtsi").touch()
        (inc / "dt-bindings/zmk/keys.h").touch()
        for split_bs, iso, split_shift, space7 in itertools.product((0, 1), repeat=4):
            values = (split_bs, iso, split_shift, space7)
            args = [cpp, "-E", "-P", "-x", "assembler-with-cpp", "-I", str(inc)]
            args += [f"-D{k}={v}" for k, v in zip(OPTIONS, values)]
            args += [str(ROOT / "include/tofu65_3_0-default-keymap.dtsi")]
            output = subprocess.check_output(args, text=True)
            layers = re.findall(r"bindings\s*=\s*<(.*?)>;", output, re.S)
            assert len(layers) == 2
            bindings = [re.findall(r"&\w+(?:\s+[A-Z0-9_]+)?", layer) for layer in layers]
            assert all(len(layer) == 69 for layer in bindings)
            base = dict(zip(coords, bindings[0]))
            assert base[6, 5] == ("&kp RET" if iso else "&kp BSLH")
            assert base[7, 0] == ("&kp NUHS" if iso else "&kp RET")
            assert base[6, 2] == ("&kp DEL" if split_bs else "&none")
            assert base[1, 4] == ("&kp NUBS" if split_shift else "&none")
            assert base[7, 3] == ("&none" if space7 else "&kp RALT")
            assert base[7, 2] == "&mo 1"
            assert "&uf2_boot" in bindings[1]
        invalid = subprocess.run([cpp, "-E", "-P", "-x", "assembler-with-cpp", "-I", str(inc),
                                  "-DTOFU_ISO_ENTER=2",
                                  str(ROOT / "include/tofu65_3_0-default-keymap.dtsi")],
                                 capture_output=True)
        assert invalid.returncode != 0
    print("PASS: 16 layout combinations, 69 bindings per layer, invalid option rejected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpp", default="gcc")
    check(parser.parse_args().cpp)

