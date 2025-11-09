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
pip install scitex-writer
scitex-writer new my-paper
scitex-writer compile
```

## Demo

<p align="center">
  <a href="01_manuscript/manuscript.pdf">
    <img src="docs/demo-manuscript-preview.png" width="600" alt="Manuscript Preview"/>
  </a>
  <br/>
  <sub><a href="01_manuscript/manuscript.pdf">📄 Full PDF</a></sub>
</p>

## Installation

**Option 1: Native LaTeX** (fastest)
```bash
sudo apt-get install texlive-latex-extra latexdiff parallel
```

**Option 2: Singularity** (HPC, reproducible)
```bash
sudo apt-get install apptainer  # or: module load singularity
```

**Option 3: Docker** (cross-platform)
```bash
curl -fsSL https://get.docker.com | sh
```

## Usage

```bash
scitex-writer compile manuscript
scitex-writer compile supplementary
scitex-writer compile revision
```

```python
from scitex.writer import Writer
Writer("/path/to/project").compile()
```

## Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [Quick Start](docs/01_GUIDE_QUICK_START.md)
- [Architecture](docs/02_ARCHITECTURE_IMPLEMENTATION.md)
- [Full Documentation](docs/)

## License

GNU Affero General Public License v3.0 (AGPL-3.0)

## Contact

ywatanabe@scitex.ai • [scitex.ai](https://scitex.ai)

<!-- EOF -->
