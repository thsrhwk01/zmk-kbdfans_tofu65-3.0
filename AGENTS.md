# Repository Guidelines

## Project Goal and Structure

Port ZMK to the KBDfans TOFU65 3.0 wired hotswap PCB while preserving its factory UF2 bootloader. This workspace currently contains firmware evidence only; no ZMK source tree, build workflow, or tests exist yet. It has no local Git metadata.

- `uf2 storage/CURRENT.UF2`: original device-exported firmware snapshot; preserve unchanged.
- `uf2 storage/INFO_UF2.TXT`: UniCore-F1 identification and bootloader version.
- `uf2 storage/INDEX.HTM`: vendor configurator redirect.

Use sibling projects `../zmk-Owlab_Link` and `../zmk-neo_neo65cu` as read-only references. When implementing the port, follow their separation of board definitions (`boards/arm/`), user configuration (`config/`), and workflows (`.github/workflows/`). These directories are proposed, not currently present.

## Development and Verification Commands

Run these PowerShell commands from this directory:

```powershell
Get-Content 'uf2 storage/INFO_UF2.TXT'
Get-FileHash 'uf2 storage/CURRENT.UF2' -Algorithm SHA256
rg --files --hidden
```

They inspect board identification, verify snapshot integrity, and list project files. No build, test, or lint command is configured. Add reproducible build instructions and pin the ZMK revision when introducing firmware sources.

## Coding Style and Naming

Use four-space indentation for new Devicetree and C code, two spaces for YAML, and descriptive lowercase identifiers such as `tofu65_3_0`. Keep hardware definitions separate from personal keymaps. Match surrounding syntax when adapting existing files; no formatter is configured yet.

## Testing Guidelines

Validate UF2 headers, block numbering, payload addresses, and image bounds before packaging firmware. Record hashes and distinguish static checks from physical keyboard tests. Hardware validation should cover USB enumeration, every key, modifiers, reconnects, and double-tap bootloader entry. No coverage threshold or test framework exists.

## Commit and Pull Request Guidelines

No local commit convention can be inferred. Sibling history uses prefixes such as `fix:` and `docs:`; use concise, scoped messages. PRs should describe hardware assumptions, evidence sources, build results, and actual hardware checks. Attach matrix diagrams or PCB photos when they substantiate wiring changes.

## Hardware Constraints

The reported board ID is `ARM32F103-UniCore-F1-v1.x`; confirm the physical MCU marking. Treat `0x08004000` as an application-start candidate, not a verified flashing address. Never copy another keyboard's pins, flash partitions, or flashing commands without target-specific evidence. Preserve original snapshots and keep generated artifacts separate.
