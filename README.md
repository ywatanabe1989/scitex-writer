<!-- ---
!-- Timestamp: 2025-11-10 02:24:18
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

<p align="center">
  <a href="https://github.com/ywatanabe1989/scitex-writer/actions/workflows/comprehensive-tests.yml">
    <img src="https://github.com/ywatanabe1989/scitex-writer/actions/workflows/comprehensive-tests.yml/badge.svg" alt="Comprehensive Tests"/>
  </a>
  <a href="https://github.com/ywatanabe1989/scitex-writer/actions/workflows/python-tests.yml">
    <img src="https://github.com/ywatanabe1989/scitex-writer/actions/workflows/python-tests.yml/badge.svg" alt="Python Tests"/>
  </a>
  <a href="https://github.com/ywatanabe1989/scitex-writer/actions/workflows/compile-test.yml">
    <img src="https://github.com/ywatanabe1989/scitex-writer/actions/workflows/compile-test.yml/badge.svg" alt="Compilation Test"/>
  </a>
  <a href="https://codecov.io/gh/ywatanabe1989/scitex-writer">
    <img src="https://codecov.io/gh/ywatanabe1989/scitex-writer/branch/main/graph/badge.svg" alt="Code Coverage"/>
  </a>
  <a href="https://github.com/ywatanabe1989/scitex-writer/actions/workflows/lint.yml">
    <img src="https://github.com/ywatanabe1989/scitex-writer/actions/workflows/lint.yml/badge.svg" alt="Lint"/>
  </a>
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
  <br/>
  <sub><a href="scripts/shell/.compile_manuscript.sh.log">📄 Compilation Log</a></sub>
</td>
<td width="33%" align="center">
  <a href="02_supplementary/supplementary.pdf">
    <img src="docs/demo-supplementary-preview.png" width="100%" alt="Supplementary"/>
  </a>
  <br/>
  <sub><a href="02_supplementary/supplementary.pdf">📄 Supplementary</a></sub>
  <br/>
  <sub><a href="scripts/shell/.compile_supplementary.sh.log">📄 Compilation Log</a></sub>  
</td>
<td width="33%" align="center">
  <a href="03_revision/revision.pdf">
    <img src="docs/demo-revision-preview.png" width="100%" alt="Revision"/>
  </a>
  <br/>
  <sub><a href="03_revision/revision.pdf">📄 Revision</a></sub>
  <br/>
  <sub><a href="scripts/shell/.compile_revision.sh.log">📄 Compilation Log</a></sub>
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

## Testing

### Running Tests

```bash
# Run all tests (Shell + Python)
./tests/run_all_tests.sh

# Run shell script tests only
./tests/scripts/run_all_tests.sh

# Run Python tests only
pytest tests/scitex/writer/ -v

# Run specific test suites
./tests/scripts/test_compile_options.sh  # Compilation options
./tests/scripts/test_dark_mode.sh        # Dark mode features
./tests/scripts/test_performance.sh      # Performance optimizations
pytest tests/scitex/writer/test_compile.py -v  # Python compilation API
```

### Test Coverage

- **70+ tests** covering all features
- **Shell Script Tests**: 30 tests
  - Compilation options (10 tests)
  - Dark mode functionality (10 tests)
  - Performance optimizations (10 tests)
- **Python Tests**: 40 tests
  - API functions (13 tests)
  - Integration tests (6 tests)
  - Template creation (6 tests)
  - Version management (6 tests)
  - Writer class (9 tests)

### Continuous Integration

All tests run automatically on GitHub Actions:
- ✅ Full compilation with PDF validation
- ✅ Fast mode (`--no_figs --no_diff`)
- ✅ Ultra-fast mode (`--draft --no_tables`)
- ✅ Dark mode (`--dark-mode`)
- ✅ All document types (manuscript, supplementary, revision)
- ✅ Option name flexibility (hyphens/underscores)

## License

GNU Affero General Public License v3.0 (AGPL-3.0)

## Contact

ywatanabe@scitex.ai • [scitex.ai](https://scitex.ai)

<!-- EOF -->