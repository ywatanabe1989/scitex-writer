<!-- ---
!-- Timestamp: 2025-10-29 13:39:14
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-writer/README.md
!-- --- -->

# SciTeX Writer

A LaTeX compilation system with predefined project structure for scientific manuscript writing.

## Quick Start

```bash
git clone https://github.com/ywatanabe1989/scitex-writer.git
cd scitex-writer
./compile.sh
```

🎉 That's it! 🎉   

PDF is produced at [`01_manuscript/manuscript.pdf`](01_manuscript/manuscript.pdf) ([Log Available](./docs/compilation_log.txt))

## How to write your paper

<details>
<summary>⚙️ Installation</summary>

## Installation

### Requirements

This project uses **Singularity/Apptainer containers** for LaTeX compilation, ensuring consistent results across different systems (local machines, HPC clusters, CI/CD platforms).

**Container system options:**
- **Apptainer** (recommended, actively maintained) - Install via package manager
- **Singularity** (legacy) - Still supported as fallback

#### System-specific installation:

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y apptainer
```

**Fedora/RHEL:**
```bash
sudo dnf install -y apptainer
```

**macOS (via Homebrew):**
```bash
brew install apptainer
```

**HPC Clusters:**
Most clusters have Singularity/Apptainer available via module system:
```bash
module load singularity  # or: module load apptainer
```

### Verify Installation

Check requirements:
```bash
./scripts/installation/check_requirements.sh
```

### Optional: Pre-download Containers

Containers are automatically downloaded on first run (~3.2GB total). Optionally download upfront:
```bash
./scripts/installation/download_containers.sh
```

This downloads:
- **texlive/texlive:latest** - LaTeX compilation (~2GB)
- **minlag/mermaid-cli:latest** - Diagram rendering
- **dpokidov/imagemagick:latest** - Image processing

## Configuration

YAML configuration files in `config/`:
- `config_manuscript.yaml` - Manuscript settings
- `config_supplementary.yaml` - Supplementary settings
- `config_revision.yaml` - Revision settings

</details>


<details>
<summary>📝 Which files to edit?</summary>

### Which files to edit?

1. **Manuscript contents**
   - [`01_manuscript/contents/abstract.tex`](01_manuscript/contents/abstract.tex)
   - [`01_manuscript/contents/introduction.tex`](01_manuscript/contents/introduction.tex)
   - [`01_manuscript/contents/methods.tex`](01_manuscript/contents/methods.tex)
   - [`01_manuscript/contents/results.tex`](01_manuscript/contents/results.tex)
   - [`01_manuscript/contents/discussion.tex`](01_manuscript/contents/discussion.tex)

2. **Metadata**
   - [`shared/title.tex`](shared/title.tex) - Manuscript title
   - [`shared/authors.tex`](shared/authors.tex) - Author list and affiliations
   - [`shared/keywords.tex`](shared/keywords.tex) - Keywords
   - [`shared/bib_files/bibliography.bib`](shared/bib_files/bibliography.bib) - References

</details>

<details>
<summary>📂 Project Structure</summary>

### Project Structure

```
scitex-writer/
├── compile.sh                  # Main
├── shared/
│   ├── title.tex
│   ├── authors.tex
│   ├── keywords.tex
│   └── bib_files/
│       └── bibliography.bib    # References
├── 01_manuscript/              # Main manuscript
│   ├── contents/
│   │   ├── abstract.tex
│   │   ├── introduction.tex
│   │   ├── methods.tex
│   │   ├── results.tex
│   │   ├── discussion.tex
│   │   ├── figures/caption_and_media/
│   │   └── tables/caption_and_media/
│   └── manuscript.pdf          # Compiled PDF
├── 02_supplementary/           # Supplementary materials
└── 03_revision/                # Revision responses
```

</details>

<details>
<summary>📈 Figures</summary>

## Figures
Place figure caption files in `01_manuscript/contents/figures/caption_and_media/`:

```tex
%% Example: 01_my_figure.tex
\caption{Description of your figure. Explain what is shown, define abbreviations, and provide sufficient detail for standalone understanding.}
\label{fig:my_figure}
```

Add corresponding image files (`.jpg`, `.png`, `.tif`) with the same base name:
- `01_my_figure.jpg` or `01_my_figure.png`

Reference in text: `Figure~\ref{fig:my_figure}`

</details>

<details>
<summary>📋 Tables</summary>

## Tables
Place table caption files in `01_manuscript/contents/tables/caption_and_media/`:

```tex
%% Example: 01_my_table.tex
\caption{Description of your table. Explain what data is shown and define any abbreviations.}
\label{tab:my_table}
```

Add corresponding data files (`.xlsx` or `.csv`) with the same base name:
- `01_my_table.xlsx` or `01_my_table.csv`

Reference in text: `Table~\ref{tab:my_table}`

</details>

<details>
<summary>📚 Citations</summary>

## Citations

Edit `shared/bib_files/bibliography.bib`:

```bibtex
@article{your_reference_2024,
  author  = {LastName, FirstName and Another, Author},
  title   = {Your Article Title},
  journal = {Journal Name},
  year    = {2024},
  volume  = {42},
  pages   = {123--145},
  doi     = {10.1234/example.2024.001}
}
```

Cite in text: `\cite{your_reference_2024}`

</details>

<details>
<summary>🔨 LaTeX to PDF</summary>

```bash
# Compile manuscript (default)
./compile

# Or specify document type explicitly
./compile -m                    # manuscript
./compile -s                    # supplementary materials
./compile -r                    # revision responses
 
# Watch mode (auto-recompile on changes)
./compile -m -w
```

</details>

<details>
<summary>✨ Features</summary>

## Features

- **Container-based compilation**: Consistent builds across systems
- **Auto-format conversion**:
  - Images: `.jpg`, `.png`, `.tif` automatically processed
  - Tables: `.xlsx` and `.csv` converted to LaTeX
  - Mermaid diagrams: `.mmd` files rendered to images
- **Version tracking**: Automatic diff generation
- **Watch mode**: Auto-recompile on file changes
- **HPC-ready**: Works on compute clusters

</details>

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on the GitHub repository.

## Contact
Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->