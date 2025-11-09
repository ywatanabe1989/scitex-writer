<!-- ---
!-- Timestamp: 2025-11-09 20:45:00
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-writer/README.md
!-- --- -->

<p align="center">
  <img src="docs/scitex-logo-banner.png" alt="SciTeX Logo" width="800"/>
</p>

<h1 align="center">SciTeX Writer</h1>

<p align="center">
  LaTeX compilation system for academic manuscripts
</p>

<p align="center">
  <a href="https://scitex.ai">scitex.ai</a> •
  <a href="docs/">Documentation</a> •
  <a href="https://github.com/ywatanabe1989/scitex-writer/issues">Issues</a>
</p>

---

## Quick Start

```bash
# Clone or use template
git clone https://github.com/ywatanabe1989/scitex-writer.git
cd scitex-writer

# Try compiling (checks dependencies automatically)
./scripts/shell/compile_manuscript.sh

# If dependencies missing, install suggested packages and retry
```

## Demo

<table>
<tr>
<td width="33%" align="center">
  <a href="01_manuscript/manuscript.pdf">
    <img src="docs/demo-manuscript-preview.png" width="100%" alt="Manuscript"/>
  </a>
  <br/>
  <sub><a href="01_manuscript/manuscript.pdf">📄 Manuscript</a></sub>
</td>
<td width="33%" align="center">
  <a href="02_supplementary/supplementary.pdf">
    <img src="docs/demo-supplementary-preview.png" width="100%" alt="Supplementary"/>
  </a>
  <br/>
  <sub><a href="02_supplementary/supplementary.pdf">📄 Supplementary</a></sub>
</td>
<td width="33%" align="center">
  <a href="03_revision/revision.pdf">
    <img src="docs/demo-revision-preview.png" width="100%" alt="Revision"/>
  </a>
  <br/>
  <sub><a href="03_revision/revision.pdf">📄 Revision</a></sub>
</td>
</tr>
</table>

## Installation

Dependencies are checked automatically during compilation. If missing, install as suggested:

**Native LaTeX (Debian/Ubuntu):**
```bash
sudo apt-get install texlive-latex-extra latexdiff parallel
```

**HPC Environments:**
```bash
module load texlive  # or use Singularity container
```

**Container (Docker/Singularity):**
```bash
# No manual installation needed
# Container includes all dependencies
```

See [Installation Guide](docs/INSTALLATION.md) for details.

## Features

- Multi-file bibliography with deduplication (DOI or title+year matching)
- Hash-based caching for incremental compilation
- Automatic diff generation with latexdiff
- Container support (Docker, Singularity, Native)
- Parallel processing for figures, tables, and word count
- Citation style configuration via YAML

## Usage

```bash
./scripts/shell/compile_manuscript.sh
./scripts/shell/compile_supplementary.sh
./scripts/shell/compile_revision.sh
```

**Bibliography Management:**
```bash
# Organize references by topic
cd 00_shared/bib_files/
vim methods_refs.bib
vim field_background.bib
vim my_papers.bib

# Auto-merge during compilation
./scripts/shell/compile_manuscript.sh
```

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Quick Start](docs/01_GUIDE_QUICK_START.md)
- [Bibliography Management](docs/01_GUIDE_BIBLIOGRAPHY.md)
- [Architecture](docs/02_ARCHITECTURE_IMPLEMENTATION.md)
- [Full Documentation](docs/)

## License

GNU Affero General Public License v3.0 (AGPL-3.0)

## Contact

ywatanabe@scitex.ai • [scitex.ai](https://scitex.ai)

<!-- EOF -->
