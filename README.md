<!-- ---
!-- Timestamp: 2025-09-26 22:43:59
!-- Author: ywatanabe
!-- File: /ssh:sp:/home/ywatanabe/proj/neurovista/paper/README.md
!-- --- -->

# SciTeX Writer

LaTeX compilation system with predefined project structure

## Quick Start

```bash
# Compile manuscript
$ export STXW_MANUSCRIPT_TYPE=manuscript # SciTeX Writer
$ ./compile_manuscript

# Output: 
# - 01_manuscript/manuscript.pdf (main document)
# - 01_manuscript/diff.pdf (tracked changes)
```

## Installation

```bash
# Check requirements
$ ./scripts/installation/check_requirements.sh

# Optional: Download all containers upfront (~3.2GB total)
$ ./scripts/installation/download_containers.sh
```

**Requirements:**
- Apptainer or Singularity (container runtime)
- yq (YAML parser)
- bash

**Auto-downloaded containers:**
- TeXLive (~2.3GB) - LaTeX, BibTeX, latexdiff
- Mermaid (~750MB) - Diagram rendering
- ImageMagick (~200MB) - Format conversion

## Project Structure

```
paper/
├── compile_manuscript              # Main script
├── config/                         # YAML configurations
├── shared/                         # Common files (single source of truth)
│   ├── bibliography.bib            # References
│   ├── authors.tex                 # Author list
│   ├── title.tex                   # Paper title
│   ├── journal_name.tex            # Target journal
│   ├── keywords.tex                # Keywords
│   └── latex_styles/               # LaTeX formatting
├── scripts/
│   ├── installation/               # Setup scripts
│   └── shell/modules/              # Compilation modules
├── 01_manuscript/
│   ├── src/                        # Document-specific content
│   │   ├── abstract.tex            # Abstract
│   │   ├── introduction.tex        # Introduction
│   │   ├── methods.tex             # Methods
│   │   ├── results.tex             # Results
│   │   ├── discussion.tex          # Discussion
│   │   └── [symlinks to shared/]   # Metadata & styles
│   ├── manuscript.pdf              # Output
│   └── diff.pdf                    # Changes tracking
└── .cache/containers/              # Auto-downloaded
```

## Editing

1. **Text**: Edit `.tex` files in `01_manuscript/src/`
2. **Figures**: Place images in `01_manuscript/src/figures/caption_and_media/`
   - Supports: `.jpg`, `.png`, `.tif`, `.mmd` (Mermaid diagrams)
3. **References**: Update `shared/bibliography.bib` (used by all documents)

## Features

- **Container-based**: Consistent compilation across systems
- **Auto-fallback**: Native → Container → Module system  
- **Version tracking**: Automatic versioning with diff generation
- **Mermaid support**: `.mmd` files auto-convert to images
- **Image processing**: Automatic format conversion via ImageMagick
- **HPC-ready**: Project-local containers for compute clusters

## Troubleshooting

| Issue                   | Solution                                |
|-------------------------|-----------------------------------------|
| "command not found"     | Containers will handle it automatically |
| Chrome/Puppeteer errors | Mermaid container includes Chromium     |
| First run slow          | Downloading containers (~3GB one-time)  |

## Configuration

Edit `config/config_manuscript.yaml` for paths and settings.

## For AI Agents

See [AI_AGENT_GUIDE.md](./AI_AGENT_GUIDE.md) for automated manuscript generation from research projects.

## Contact

Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->