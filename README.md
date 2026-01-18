<!-- ---
!-- Timestamp: 2026-01-19 04:11:25
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-writer/README.md
!-- --- -->

# SciTeX Writer

A LaTeX compilation system for academic manuscripts with automatic versioning, diff generation, and cross-platform reproducibility.

Part of the fully open-source SciTeX project: https://scitex.ai

## Quick Start

```bash
git clone https://github.com/ywatanabe1989/scitex-writer.git
./scitex-writer/scripts/compile.sh manuscript
```

<details>
<summary><strong>Output Structure</strong></summary>

```
./scitex-writer/
├── 00_shared/                  # Shared resources across all documents
│   ├── bib_files/              # Multiple .bib files (auto-merged)
│   ├── latex_styles/           # Common LaTeX configurations
│   ├── metadata/               # Title, authors, keywords, affiliations
│   └── word_counts/            # Auto-generated word statistics
│
├── 01_manuscript/              # Main manuscript
│   ├── contents/               # Modular content sections
│   │   ├── abstract.tex
│   │   ├── introduction.tex
│   │   ├── methods.tex
│   │   ├── results.tex
│   │   ├── discussion.tex
│   │   ├── figures/            # Figure captions + media
│   │   └── tables/             # Table captions + CSV data
│   ├── archive/                # Version history (gitignored)
│   ├── manuscript.tex          # Compiled LaTeX
│   ├── manuscript_diff.tex     # Change-tracked version
│   └── manuscript.pdf          # Output PDF
│
├── 02_supplementary/           # Supplementary materials
│   ├── contents/               # Supplementary content sections
│   │   ├── supplementary_methods.tex
│   │   ├── supplementary_results.tex
│   │   ├── figures/            # Supplementary figures
│   │   └── tables/             # Supplementary tables
│   ├── archive/                # Version history (gitignored)
│   ├── supplementary.tex       # Compiled LaTeX
│   └── supplementary.pdf       # Output PDF
│
├── 03_revision/                # Revision response letter
│   ├── contents/               # Reviewer responses
│   │   ├── editor/             # E_01_comments.tex, E_01_response.tex
│   │   ├── reviewer1/          # R1_01_comments.tex, R1_01_response.tex
│   │   └── reviewer2/          # R2_01_comments.tex, R2_01_response.tex
│   ├── archive/                # Version history (gitignored)
│   ├── revision.tex            # Compiled LaTeX
│   └── revision.pdf            # Output PDF
│
├── config/                     # Configuration files
│   └── config_manuscript.yaml  # Citation style, engine settings
│
└── scripts/shell/              # Compilation scripts
    ├── compile_manuscript.sh
    ├── compile_supplementary.sh
    └── compile_revision.sh
```

</details>

## Features

<details>
<summary><strong>Details</strong></summary>

| Feature                | Description                                                           |
|------------------------|-----------------------------------------------------------------------|
| **Separated Files**    | Modular sections (abstract, intro, methods, results, discussion)      |
| **Built-in Templates** | Pre-configured manuscript, supplementary materials, and revision      |
| **Bibliography**       | Multi-file with auto-deduplication, 20+ citation styles               |
| **Assets**             | Parallel figure/table processing (PNG, PDF, SVG, Mermaid, CSV)        |
| **Multi-Engine**       | Auto-selects best engine (Tectonic 1-3s, latexmk 3-6s, 3-pass 12-18s) |
| **Cross-Platform**     | Linux, macOS, WSL2, Docker, Singularity, HPC clusters                 |

</details>

## Usage

<details>
<summary><strong>PDF Compilation</strong></summary>

```bash
# Basic compilation
./scripts/shell/compile_manuscript.sh          # Manuscript
./scripts/shell/compile_supplementary.sh       # Supplementary
./scripts/shell/compile_revision.sh            # Revision letter

# Performance options
./scripts/shell/compile_manuscript.sh --draft      # Fast single-pass
./scripts/shell/compile_manuscript.sh --no-figs    # Skip figures
./scripts/shell/compile_manuscript.sh --no-tables  # Skip tables
./scripts/shell/compile_manuscript.sh --no-diff    # Skip diff generation

# Engine selection
./scripts/shell/compile_manuscript.sh --engine tectonic  # Fastest
./scripts/shell/compile_manuscript.sh --engine latexmk   # Standard
./scripts/shell/compile_manuscript.sh --engine 3pass     # Most compatible

# Development
./scripts/shell/compile_manuscript.sh --watch  # Hot-reload on file changes
./scripts/shell/compile_manuscript.sh --clean  # Remove cache
```

</details>

<details>
<summary><strong>Figures</strong></summary>

1. Place media files in `01_manuscript/contents/figures/caption_and_media/`:
   ```
   01_example_figure.png
   01_example_figure.tex  # Caption file
   ```

2. Caption file format (`01_example_figure.tex`):
   ```latex
   %% Figure caption
   \caption{Your figure caption here. Explain panels (A, B, C) if applicable.}
   \label{fig:example_figure_01}
   ```

3. Supported formats: PNG, JPEG, PDF, SVG, TIFF, Mermaid (.mmd)

4. Figures auto-compile and include in `FINAL.tex`

</details>

<details>
<summary><strong>Tables</strong></summary>

1. Place CSV + caption in `01_manuscript/contents/tables/caption_and_media/`:
   ```
   01_example_table.csv
   01_example_table.tex  # Caption file
   ```

2. CSV auto-converts to LaTeX table format

3. Caption file format (`01_example_table.tex`):
   ```latex
   %% Table caption
   \caption{Your table caption. Define abbreviations used.}
   \label{tab:example_table_01}
   ```

</details>

<details>
<summary><strong>References</strong></summary>

Organize references in multiple `.bib` files - they auto-merge with deduplication:

```bash
00_shared/bib_files/
├── methods_refs.bib      # Method-related references
├── field_background.bib  # Background literature
└── my_papers.bib         # Your own publications
```

Change citation style in `config/config_manuscript.yaml`:
- `unsrtnat` (numbered, order of citation)
- `plainnat` (numbered, alphabetical)
- `apalike` (author-year, APA style)
- `IEEEtran` (IEEE format)
- `naturemag` (Nature style)

</details>

## Installation

<details>
<summary><strong>Ubuntu/Debian</strong></summary>

```bash
sudo apt-get install texlive-latex-extra latexdiff parallel imagemagick ghostscript
```

</details>

<details>
<summary><strong>macOS</strong></summary>

```bash
brew install texlive latexdiff parallel imagemagick ghostscript
```

</details>

<details>
<summary><strong>HPC / Containers</strong></summary>

```bash
# Module system
module load texlive latexdiff parallel

# Docker
docker run -v $(pwd):/work scitex-writer

# Singularity/Apptainer
singularity run scitex-writer.sif
```

</details>

## Documentation

<details>
<summary><strong>Details</strong></summary>

| Guide | Description |
|-------|-------------|
| [Installation](docs/01_GUIDE_INSTALLATION.md) | Setup for all environments |
| [Quick Start](docs/01_GUIDE_QUICK_START.md) | Common workflows |
| [Content Creation](docs/01_GUIDE_CONTENT_CREATION.md) | Writing manuscripts |
| [Bibliography](docs/01_GUIDE_BIBLIOGRAPHY.md) | Reference management |
| [Architecture](docs/02_ARCHITECTURE_IMPLEMENTATION.md) | Technical details |

</details>

---

<p align="center">
  <a href="https://scitex.ai" target="_blank"><img src="docs/scitex-icon-navy-inverted.png" alt="SciTeX" width="40"/></a>
  <br>
  AGPL-3.0 · ywatanabe@scitex.ai
</p>

<!-- EOF -->