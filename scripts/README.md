<!-- ---
!-- Timestamp: 2026-01-19 05:16:50
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-writer/scripts/README.md
!-- --- -->

# Scripts

```
scripts/
├── containers/      # Container image builds (Apptainer/Singularity)
├── installation/    # Environment setup and dependency installation
├── maintenance/     # Repository maintenance (usage, update, demos)
├── powershell/      # Windows PowerShell scripts
├── python/          # Python utilities
└── shell/           # Core compilation scripts
```

## Directory Overview

| Directory | Purpose |
|-----------|---------|
| `containers/` | Build scripts for Apptainer/Singularity containers (texlive, mermaid) |
| `installation/` | Setup scripts for different environments (Linux, macOS, HPC) |
| `maintenance/` | Repository tasks: `show_usage.sh`, `update.sh`, `generate_demo_previews.sh` |
| `powershell/` | Windows-specific scripts for WSL integration |
| `python/` | Python utilities for bibliography and asset processing |
| `shell/` | Main compilation pipeline (`compile_manuscript.sh`, etc.) |

## Quick Reference

```bash
# Compilation (via shell/)
./compile.sh manuscript
./compile.sh supplementary
./compile.sh revision

# Maintenance (via Makefile)
make usage          # Show project guide
make update         # Update to latest version
make demo-previews  # Generate README screenshots
```

<!-- EOF -->