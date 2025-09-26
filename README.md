<!-- ---
!-- Timestamp: 2025-09-26 22:40:36
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/neurovista/paper/README.md
!-- --- -->

# SciTeX Manuscript Compilation System

Container-based LaTeX compilation for reproducible scientific manuscripts.

## Quick Start

```bash
# Compile manuscript
$ export STXW_MANUSCRIPT_TYPE=manuscript
$ ./compile_manuscript

# Output: 
# - 01_manuscript/manuscript.pdf (main document)
# - 01_manuscript/diff.pdf (tracked changes)
```

## Installation

```bash
# Check requirements
$ ./scripts/installation/check_requirements.sh

# Optional: Download containers upfront (~3GB)
$ ./scripts/installation/download_containers.sh
```

**Requirements:**
- Apptainer or Singularity (container runtime)
- yq (YAML parser)
- bash

Containers are auto-downloaded on first use if not present.

## Project Structure

```
paper/
├── compile_manuscript              # Main script
├── config/                         # YAML configurations
├── scripts/
│   ├── installation/               # Setup scripts
│   └── shell/modules/              # Compilation modules
├── 01_manuscript/
│   ├── src/                        # Edit these files
│   │   ├── *.tex                   # Sections
│   │   ├── bibliography.bib        # References
│   │   └── figures/                # Images & diagrams
│   ├── manuscript.pdf              # Output
│   └── diff.pdf                    # Changes tracking
└── .cache/containers/              # Auto-downloaded
```

## Editing

1. **Text**: Edit `.tex` files in `01_manuscript/src/`
2. **Figures**: Place images in `01_manuscript/src/figures/caption_and_media/`
   - Supports: `.jpg`, `.png`, `.tif`, `.mmd` (Mermaid diagrams)
3. **References**: Update `01_manuscript/src/bibliography.bib`

## Features

- **Container-based**: Consistent compilation across systems
- **Auto-fallback**: Native → Container → Module system
- **Version tracking**: Automatic versioning with diff generation
- **Mermaid support**: `.mmd` files auto-convert to images
- **HPC-ready**: Project-local containers for compute clusters

## Troubleshooting

| Issue                   | Solution                                |
|-------------------------|-----------------------------------------|
| "command not found"     | Containers will handle it automatically |
| Chrome/Puppeteer errors | Mermaid container includes Chromium     |
| First run slow          | Downloading containers (~3GB one-time)  |

## Configuration

Edit `config/config_manuscript.yaml` for paths and settings.

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->