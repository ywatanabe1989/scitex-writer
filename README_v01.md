<!-- ---
!-- Timestamp: 2025-10-29 12:55:23
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-writer/README.md
!-- --- -->

# SciTeX Writer

A LaTeX compilation system with predefined project structure for scientific manuscript writing.

## Quick Start

### Project Structure

```
scitex-writer/
├── compile                      # Main compilation script
├── shared/                      # Common files (shared across all documents)
│   ├── title.tex               # Paper title
│   ├── authors.tex             # Author list
│   ├── keywords.tex            # Keywords
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
│   └── manuscript.pdf          # Output
├── 02_supplementary/           # Supplementary materials
└── 03_revision/               # Revision responses
```

### Manuscript Compilation

1. **Edit your manuscript content** in [`01_manuscript/contents/`](01_manuscript/contents/):
   - `abstract.tex`
   - `introduction.tex`
   - `methods.tex`
   - `results.tex`
   - `discussion.tex`

2. **Add metadata** in `shared/`:
   - `title.tex` - Manuscript title
   - `authors.tex` - Author list and affiliations
   - `keywords.tex` - Keywords
   - `bib_files/bibliography.bib` - References

3. **Compile your manuscript**:
   ```bash
   ./compile
   ```

   Output: `01_manuscript/manuscript.pdf`



<details>
<summary>Figures</summary>

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
<summary>Tabless</summary>

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
<summary>Citations</summary>

## Compilation Options

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
<summary>Citations</summary>

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

## Features

- **Container-based compilation**: Consistent builds across systems
- **Auto-format conversion**:
  - Images: `.jpg`, `.png`, `.tif` automatically processed
  - Tables: `.xlsx` and `.csv` converted to LaTeX
  - Mermaid diagrams: `.mmd` files rendered to images
- **Version tracking**: Automatic diff generation
- **Watch mode**: Auto-recompile on file changes
- **HPC-ready**: Works on compute clusters

<details>
<summary>Installation</summary>

## Installation

Check requirements:
```bash
./scripts/installation/check_requirements.sh
```

Optionally download containers upfront (~3.2GB):
```bash
./scripts/installation/download_containers.sh
```

## Configuration

YAML configuration files in `config/`:
- `config_manuscript.yaml` - Manuscript settings
- `config_supplementary.yaml` - Supplementary settings
- `config_revision.yaml` - Revision settings

</details>
## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on the GitHub repository.

## Contact
Yusuke Watanabe (ywatanabe@scitex.ai)

<!-- EOF -->