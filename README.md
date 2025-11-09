<!-- ---
!-- Timestamp: 2025-11-09 19:20:50
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-writer/README.md
!-- --- -->

<p align="center">
  <img src="docs/scitex-logo-banner.png" alt="SciTeX Logo" width="800"/>
</p>

<h1 align="center">SciTeX Writer</h1>

<p align="center">
  LaTeX compilation system for scientific documents with Python API and version control
</p>

<p align="center">
  <a href="https://scitex.ai">🌐 SciTeX Ecosystem</a> •
  <a href="https://github.com/ywatanabe1989/scitex-writer">📖 Documentation</a> •
  <a href="https://github.com/ywatanabe1989/scitex-writer/issues">🐛 Issues</a>
</p>

<p align="center">
  Part of the <a href="https://scitex.ai"><strong>SciTeX</strong></a> family of scientific computing tools
</p>

---

## Quick Start

```bash
git clone https://github.com/ywatanabe1989/scitex-writer.git
cd scitex-writer
./compile.sh
```

🎉 That's it! 🎉   

PDF is produced at [`01_manuscript/manuscript.pdf`](01_manuscript/manuscript.pdf) ([Log Available](./docs/compilation_log.txt))

## Installation

### Method 1: Python Package (Recommended)

```bash
pip install scitex-writer
```

**Usage:**
```python
from scitex.writer import Writer

# Compile manuscript
writer = Writer("/path/to/manuscript")
writer.compile()

# Or use CLI
scitex-writer compile manuscript
scitex-writer new my_paper
scitex-writer update
```

### Method 2: Git Clone

```bash
git clone https://github.com/ywatanabe1989/scitex-writer.git
cd scitex-writer
make develop  # Install in development mode
```

### Update to Latest Version

```bash
scitex-writer update    # If installed via pip
./scripts/update.sh     # If cloned from git
make update             # Via Makefile
```

## How to write your paper

<details>
<summary>⚙️ Detailed Installation</summary>

## Detailed Installation

SciTeX Writer supports **three deployment options** for LaTeX dependencies. Choose the one that fits your environment:

---

### **Option 1: Native Installation** (Fastest - If You Have LaTeX)

**Best for:** Users with existing LaTeX installation, fastest compilation

**Ubuntu/Debian:**
```bash
sudo apt-get install -y \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-bibtex-extra \
    texlive-extra-utils \
    latexdiff \
    parallel
```

**Fedora/RHEL:**
```bash
sudo dnf install -y \
    texlive-scheme-medium \
    latexdiff \
    parallel
```

**macOS (via Homebrew):**
```bash
brew install --cask mactex
brew install parallel
```

✅ **Pros:** Fast, lightweight, no containers needed
⚠️ **Cons:** Version differences across systems

---

### **Option 2: Containers** (Reproducible - Zero Configuration)

**Best for:** Reproducible builds, HPC clusters, CI/CD

Containers are **automatically downloaded** on first compilation. No manual setup needed!

#### **2A. Apptainer/Singularity** (Recommended for HPC)

**Ubuntu/Debian:**
```bash
sudo apt-get install -y apptainer
```

**HPC Clusters:**
```bash
module load singularity  # or: module load apptainer
```

**Optional - Pre-download:**
```bash
./scripts/installation/download_containers.sh
# Downloads: texlive (~2GB), mermaid (~750MB), imagemagick (~200MB)
```

#### **2B. Docker**

```bash
# Install Docker
curl -fsSL https://get.docker.com | sh

# Done! Containers auto-download on first use
./compile.sh
```

✅ **Pros:** Reproducible, consistent across systems, auto-downloads
⚠️ **Cons:** Initial download size (~3.2GB), slower than native

---

### **Option 3: HPC Module System** (HPC Only)

**Best for:** HPC clusters with pre-installed modules

```bash
module load texlive parallel
./compile.sh
```

SciTeX Writer automatically detects and uses loaded modules.

✅ **Pros:** Already available on HPC, no installation
⚠️ **Cons:** Only available on HPC systems

---

### Verify Installation

Check which option you have:
```bash
./scripts/installation/check_requirements.sh
```

Output shows:
- ✓ Native tools found (if installed)
- ✓ Container runtime available
- ✓ Module system detected

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
   - [`00_shared/title.tex`](00_shared/title.tex) - Manuscript title
   - [`00_shared/authors.tex`](00_shared/authors.tex) - Author list and affiliations
   - [`00_shared/keywords.tex`](00_shared/keywords.tex) - Keywords
   - [`00_shared/bib_files/bibliography.bib`](00_shared/bib_files/bibliography.bib) - References

</details>

<details>
<summary>📂 Project Structure</summary>

### Project Structure

```
scitex-writer/
├── compile.sh                  # Main
├── 00_shared/
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
<summary>📚 Citations & Bibliography Styles</summary>

## Citations

### Adding References

Edit `00_shared/bib_files/bibliography.bib`:

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

### Changing Citation Style

Simply edit the `citation.style` field in your config file:

**config/config_manuscript.yaml:**
```yaml
citation:
  style: "unsrtnat"  # Change to any supported style
```

**Available styles (ready to use):**
- `unsrtnat` - Numbered [1], order of appearance (Vancouver-like) - **default**
- `plainnat` - Numbered [1], alphabetical by author
- `abbrvnat` - Numbered, abbreviated author names
- `apalike` - Author-year, APA-like style
- `IEEEtran` - IEEE Transactions style
- `naturemag` - Nature magazine style
- `elsarticle-num` - Elsevier numbered, alphabetical
- `elsarticle-harv` - Elsevier Harvard (author-year)

**Advanced styles** (APA 7th, Chicago, MLA, MHRA, etc.):

See `00_shared/latex_styles/bibliography.tex` for 15+ additional citation formats including:
- American Chemical Society (ACS)
- American Medical Association (AMA) 11th edition
- American Psychological Association (APA) 7th edition
- American Sociological Association (ASA)
- Chicago Manual of Style (author-date, notes, shortened notes)
- Modern Language Association (MLA) 9th edition
- Modern Humanities Research Association (MHRA)
- Harvard variations (Cite Them Right, etc.)

For these advanced styles, see instructions in `bibliography.tex` for switching from natbib to biblatex.

The citation style is automatically applied during compilation - no manual LaTeX editing needed!

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
- **Flexible citation styles**: 15+ citation formats via simple config change
  - IEEE, Nature, APA, Chicago, MLA, Harvard, Vancouver, and more
  - Automatic style switching without manual LaTeX editing
- **Version tracking**: Automatic diff generation
- **Watch mode**: Auto-recompile on file changes
- **HPC-ready**: Works on compute clusters

</details>

## License

GNU Affero General Public License v3.0 (AGPL-3.0) - See LICENSE file for details

## Support

For issues or questions, please open an issue on the GitHub repository.

## Contact
Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->