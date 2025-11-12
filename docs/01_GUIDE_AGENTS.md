# AI Agent Guide for SciTeX

Complete guide for AI agents to create scientific manuscripts using SciTeX Writer.

## Quick Start

```bash
export SCITEX_WRITER_DOC_TYPE=manuscript
./compile_manuscript

# Output
manuscript: 01_manuscript/manuscript.pdf
changes: 01_manuscript/diff.pdf
```

## Project to Manuscript Workflow

### 1. Link Research Assets

Use symlinks to maintain single source of truth (don't copy):

```bash
# Link figures
ln -s ~/proj/neurovista/scripts/analysis/output/fig1.png \
      01_manuscript/contents/figures/caption_and_media/.01_seizure_prediction.png

# Link tables
ln -s ~/proj/neurovista/data/results/performance.csv \
      01_manuscript/contents/tables/caption_and_media/.01_performance.csv

# Link diagrams
ln -s ~/proj/neurovista/docs/workflow.mmd \
      01_manuscript/contents/figures/caption_and_media/.02_workflow.mmd
```

### 2. Write Content

Edit files in `01_manuscript/contents/`:

```latex
% introduction.tex
\section{Introduction}
Neural interactions through phase-amplitude coupling...

% Reference figures
As shown in Figure~\ref{fig:01_seizure_prediction}...

% Citations (from 00_shared/bibliography.bib)
Previous work \cite{Tort2010} demonstrated...
```

Note: Bibliography is 00_shared:
- Edit: `00_shared/bibliography.bib`
- Used by: manuscript, supplementary, revision

### 3. Add Figure Captions

Create `01_manuscript/contents/figures/caption_and_media/.01_seizure_prediction.tex`:

```latex
\textbf{Seizure prediction performance.}
(A) ROC curves across patients.
(B) Feature importance analysis.
(C) Temporal dynamics of prediction confidence.
```

### 4. Compile

```bash
./compile_manuscript  # Everything handled automatically
```

## File Naming Rules

### CRITICAL: Naming Conventions

**Figures**: `.XX_descriptive_name.{jpg|png|tif|mmd}`
- Must start with `.`
- XX = two-digit number (01, 02, 03...)
- descriptive_name = lowercase with underscores
- Example: `.01_seizure_prediction.png`

**Tables**: `.XX_descriptive_name.csv`
- Must start with `.`
- XX = two-digit number
- descriptive_name = lowercase with underscores
- Example: `.01_patient_demographics.csv`

**Captions**: Same name with `.tex` extension
- `.01_seizure_prediction.tex` (figure caption)
- `.01_patient_demographics.tex` (table caption)

### LaTeX Citation Syntax

```latex
\cite{key}           % (Author Year)
\cite{key1,key2}     % (Author1 Year1; Author2 Year2)
\citet{key}          % Author (Year)
\cite{key}          % (Author Year)
```

## Manuscript Structure

### Directory Layout

```
01_manuscript/
├── manuscript.tex               # Main entry point
├── contents/
│   ├── abstract.tex
│   ├── introduction.tex
│   ├── methods.tex
│   ├── results.tex
│   ├── discussion.tex
│   ├── figures/
│   │   ├── caption_and_media/  # Place figure files here
│   │   │   ├── .01_figure.png
│   │   │   └── .01_figure.tex
│   │   └── compiled/            # Auto-generated
│   └── tables/
│       ├── caption_and_media/  # Place table files here
│       │   ├── .01_table.csv
│       │   └── .01_table.tex
│       └── compiled/            # Auto-generated
├── 00_shared/
│   ├── authors.tex
│   ├── title.tex
│   ├── keywords.tex
│   └── bibliography.bib
└── scripts/
    └── (compilation scripts)
```

### Content Sections

Each content file should follow LaTeX structure:

```latex
\section{Introduction}
First paragraph introduces topic...

\subsection{Background}
Subsection with relevant background...

\subsubsection{Previous Work}
Detailed discussion of related research...
```

## Compilation Options

### Full Compilation
```bash
./compile_manuscript  # Full document with all features
```

### With Figure Processing
```bash
./compile_manuscript --figs
./compile_manuscript -f
```

Processes:
- PowerPoint to PNG conversion
- Image cropping and normalization
- Caption integration
- Resolution optimization

### View Differences
```bash
./compile_manuscript --diff
```

Shows change tracking from previous version

### Debug Mode
```bash
./compile_manuscript --debug
```

Provides verbose output and keeps intermediate files

## Using with LLMs

### Workflow for Claude, GPT, etc.

1. **Provide context**:
   - Share research outputs (figures, tables, raw data)
   - Provide manuscript skeleton or outlines

2. **Request manuscript generation**:
   - Ask LLM to write specific sections
   - Provide example structure for consistency

3. **Content integration**:
   - Save LLM output to appropriate `.tex` files
   - Link figures/tables as described above

4. **Iterative refinement**:
   - Request revisions through manuscript comments
   - Use diff feature to track changes
   - Iterate until publication-ready

### Example Prompt

```
Create a manuscript introduction for a paper on seizure prediction using PAC analysis.

Requirements:
- Use LaTeX formatting
- Include references to Figure 1 and Table 1
- 500-700 words
- Research context: neurovista patient dataset

Structure:
- Motivate the problem (2 paragraphs)
- Review existing methods (2 paragraphs)
- State our approach (1 paragraph)
```

## Figure Workflow

### Adding Figures for LLM Processing

1. **Generate figure** (Python, R, etc.):
```python
import matplotlib.pyplot as plt
plt.savefig('seizure_prediction.png', dpi=300)
```

2. **Link to manuscript**:
```bash
ln -s /path/to/seizure_prediction.png \
      01_manuscript/contents/figures/caption_and_media/.01_seizure_prediction.png
```

3. **Create caption** (LLM can help):
```latex
% File: .01_seizure_prediction.tex
\caption{\textbf{Seizure prediction performance.}
(A) ROC curves for single-patient models...
(B) Comparison across all patients...}
% width=0.9\textwidth
```

4. **Reference in text**:
```latex
Figure~\ref{fig:01_seizure_prediction} shows...
```

## Table Workflow

### Adding Tables for LLM Processing

1. **Generate table** (CSV format):
```csv
Patient,Accuracy,Sensitivity,Specificity
P001,0.92,0.89,0.94
P002,0.88,0.85,0.91
```

2. **Link to manuscript**:
```bash
ln -s /path/to/results.csv \
      01_manuscript/contents/tables/caption_and_media/.01_results.csv
```

3. **Create caption**:
```latex
% File: .01_results.tex
\caption{\textbf{Classification performance.}
Summary of accuracy, sensitivity, and specificity...}
% alignment=auto
% fontsize=small
```

4. **Reference in text**:
```latex
Table~\ref{tab:01_results} presents...
```

## Version Control

### Track Manuscript Changes

Each compilation creates diff with previous version:
```
01_manuscript/diff.pdf      # Shows all changes
01_manuscript/manuscript.pdf # Current version
```

### Git Integration

```bash
git add 01_manuscript/contents/*.tex
git commit -m "Update results section with new analysis"
git diff HEAD~1  # See what changed in this commit
```

## Troubleshooting

### Common Issues

**Figure not appearing**
- Check file path and naming
- Verify .PNG and .TEX files have same base name
- Examine debug output with `--debug` flag

**Bibliography errors**
- Ensure `00_shared/bibliography.bib` is valid
- Verify all \cite{} keys exist in bibliography
- Run `./compile_manuscript` again if keys were added

**Compilation fails**
- Check for LaTeX syntax errors in content
- Verify all linked files exist
- Check disk space
- Review console output for specific errors

**Symlinks not working**
- Use absolute paths: `/full/path/to/file`
- Verify source files exist before creating link
- Check link with: `ls -l <link_name>`

## Advanced Features

### Custom LaTeX Templates

Override default styling by editing files in `styles/`:
- Document class options
- Color schemes
- Font selections
- Page layout parameters

### Bibliography Management

Add citations from BibTeX format:
```bibtex
@article{Smith2023,
  author = {Smith, John},
  title = {Article Title},
  journal = {Journal Name},
  year = {2023}
}
```

### Supplementary Materials

Create additional documents in `02_supplementary/`:
- Same structure as main manuscript
- Cross-references to main document
- Separate compilation

## Resources

- See `01_GUIDE_CONTENT_CREATION.md` for detailed figure/table guide
- Check `to_claude/guidelines/` for language-specific standards
- Review `structure/` directory for repository organization
