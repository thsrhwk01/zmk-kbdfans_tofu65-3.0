# Build and verification


ZMK is pinned to `edf5c0814fd3ea202e43aad2d68fd32e882a518c` (v0.3.0). Each artifact includes `manifest-frozen.yml`, ELF/BIN, map files, resolved config/DTS, layout choices, verification report and SHA-256 checksums. The workflow builds normal and no-scan diagnostic variants; release assets are published separately.

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

