param(
    [Parameter(Mandatory = $true)][string]$FirmwareWorkspace,
    [string]$Python = 'python',
    [string]$West = 'west'
)
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskWorkspace = [IO.Path]::GetFullPath($FirmwareWorkspace)
$taskBuild = Join-Path $taskRoot 'build/firmware'
$taskDist = Join-Path $taskRoot ('dist/' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
if (-not (Test-Path -LiteralPath (Join-Path $taskWorkspace 'zmk/app/CMakeLists.txt'))) {
    throw 'FirmwareWorkspace must contain the initialized ZMK/Zephyr west workspace; see README.md.'
}
Push-Location $taskWorkspace
try {
    & $West build -p always -s zmk/app -d $taskBuild -b tofu65_3_0 -- "-DZMK_CONFIG=$taskRoot/config" "-DZMK_EXTRA_MODULES=$taskRoot"
    if ($LASTEXITCODE -ne 0) { throw 'ZMK build failed; no firmware packaged.' }
    New-Item -ItemType Directory -Path $taskDist | Out-Null
    & $Python "$taskRoot/tools/verify_build.py" --elf "$taskBuild/zephyr/zmk.elf" --bin "$taskBuild/zephyr/zmk.bin" --config "$taskBuild/zephyr/.config" --report "$taskDist/build-verification.json"
    if ($LASTEXITCODE -ne 0) { throw 'ELF/BIN verification failed; no firmware packaged.' }
    & $Python "$taskRoot/tools/package_uf2.py" --application-bin "$taskBuild/zephyr/zmk.bin" --output "$taskDist/tofu65_3_0-zmk-UNTESTED.uf2"
    if ($LASTEXITCODE -ne 0) { throw 'UF2 packaging failed.' }
    Copy-Item -LiteralPath "$taskBuild/zephyr/zmk.elf", "$taskBuild/zephyr/zmk.bin" -Destination $taskDist
    Get-ChildItem -LiteralPath "$taskBuild/zephyr" -Filter '*.map' -File | Copy-Item -Destination $taskDist
    Copy-Item -LiteralPath "$taskRoot/config/layout-options.h" -Destination $taskDist
    Write-Output "Experimental artifacts: $taskDist"
} finally {
    Pop-Location
}

