# SciTex Quick Reference Guide

This guide provides a quick reference for common tasks and commands in SciTex.

## Getting Started

### Basic Workflow

1. Edit content files in `manuscript/contents/`
2. Add figures to `manuscript/contents/figures/contents/`
3. Add tables to `manuscript/contents/tables/contents/`
4. Add citations to `manuscript/contents/bibliography.bib`
5. Compile with `./compile`
6. View PDF in `manuscript/main/manuscript.pdf`

### Project Structure

```
SciTex/
├── manuscript/         # Main manuscript
│   ├── contents/            # Source files
│   │   ├── figures/    # Figure files
│   │   ├── tables/     # Table files
│   │   └── *.tex       # Content files (intro, methods, etc.)
├── revision/           # Revision responses
├── supplementary/      # Supplementary materials
├── docs/               # Documentation
├── examples/           # Example files
└── scripts/            # Compilation scripts
```

## Figure Management

### Adding a Figure

1. Create your figure image (300 DPI PNG recommended)
2. Save in `manuscript/contents/figures/contents/` as `.XX_description.png`
   - Replace `XX` with sequential number (01, 02, etc.)
   - Use descriptive name (e.g., `.01_workflow.png`)
3. Create caption file `.XX_description.tex` with same name
4. Reference in text: `Figure~\ref{fig:XX}`
5. Compile with figures: `./compile --figs`

### Figure Caption Template

```latex
\caption{\textbf{
Figure title goes here.
}
\smallskip
\\
Detailed figure description goes here. Include relevant details such as sample size,
statistical tests, and interpretation of the results.
}
% width=1\textwidth
```

### Multi-panel Figure Caption

```latex
\caption{\textbf{
Multi-panel figure title.
}
\smallskip
\\
\textbf{\textit{A.}} Description of panel A with specific details. 
\textbf{\textit{B.}} Description of panel B with methodology information.
\textbf{\textit{C.}} Description of panel C with quantitative results.
\textbf{\textit{D.}} Description of panel D with statistical significance (p < 0.05).
}
% width=1\textwidth
% panel_labels=A,B,C,D
% panel_layout=2x2
% panel_spacing=0.5em
```

### Creating Multi-panel Figures Programmatically

For complex multi-panel figures, SciTex provides helper scripts:

```bash
# Basic multi-panel figure with 2x2 grid
python examples/generate_multipanel_figure.py --id 05 --name experiment_results

# Advanced layout with custom panel arrangement
python examples/advanced_multipanel_figure.py --id 06 --name complex_analysis

# Use the multipanel_helper module for customization
python
import multipanel_helper as mph
fig, axes = mph.create_multi_panel_layout(2, 2, panel_labels=['A', 'B', 'C', 'D'])
mph.generate_caption_template('.07_analysis.tex', title='Analysis of results')
```

### PowerPoint to PNG Conversion

If you create figures in PowerPoint:

1. Save your PowerPoint file to `manuscript/contents/figures/contents/.XX_description.pptx`
2. Run conversion: `./compile -m --pptx2png`
3. Creates PNG files automatically
4. Continue with normal figure workflow

See [MULTIPANEL_FIGURE_GUIDE.md](MULTIPANEL_FIGURE_GUIDE.md) for detailed information on creating complex figures.

### Referencing Figures

```latex
Figure~\ref{fig:01}                 % Whole figure
Figure~\ref{fig:01}A                % Panel A
Figure~\ref{fig:01}A,B              % Panels A and B
Figure~\ref{fig:01}A--C             % Panels A through C
Figures~\ref{fig:01} and \ref{fig:02}  % Multiple figures
```

### Checking Figure Compilation

If figures don't appear or look incorrect:

1. Check debug files in `manuscript/contents/figures/compiled/debug/`
2. Verify image paths and existence
3. Ensure proper caption format
4. Rebuild using `./compile -m --figs --debug`

## Table Management

### Adding a Table

1. Create data as CSV: `.XX_description.csv`
   - Replace `XX` with sequential number (01, 02, etc.)
   - Use descriptive name (e.g., `.01_results.csv`)
2. Save in `manuscript/contents/tables/contents/`
3. Create caption file `.XX_description.tex` with same name
4. Reference in text: `Table~\ref{tab:XX}`
5. Compile: `./compile`

### Table CSV Format

```csv
Column1,Column2,Column3
Value1,Value2,Value3
Value4,Value5,Value6
```

Notes:
- First row is treated as header (bold formatting)
- Use commas as separators (no semicolons)
- Wrap text with quotes if it contains commas: `"Text, with comma",Value2,Value3`
- Numeric formatting is preserved (decimals, scientific notation)

### Table Caption Template

```latex
\caption{\textbf{
Table title goes here.
}
\smallskip
\\
Detailed table description goes here. Include sample size, measurement units, 
and important notes for interpreting the data.
}
% width=0.8\textwidth
```

### Table Formatting Options

Add these comments to your caption file to control table appearance:

```latex
% fontsize=small      % Options: tiny, scriptsize, footnotesize, small, normalsize
% tabcolsep=4pt       % Controls column spacing
% alignment=r         % Options: l (left), c (center), r (right), auto
% orientation=landscape  % For wide tables
% no-color            % Disables alternating row colors
```

### Referencing Tables

```latex
Table~\ref{tab:01}                   % Basic reference
Table~\ref{tab:01} (row 2, column 3) % Specific cell
Tables~\ref{tab:01} and \ref{tab:02} % Multiple tables
```

## Compilation Commands

### Basic Compilation

```bash
# From project root directory
./compile -m           # Compile manuscript only
./compile -s           # Compile supplementary only
./compile -r           # Compile revision only
./compile              # Compile all (default)
```

### Compilation with Options

```bash
# With figures
./compile -m --figs    # Compile manuscript with figures (or -f)

# PowerPoint to PNG conversion
./compile -m --pptx2png --figs  # Convert PPTX, then compile with figures (or -p2p -f)

# Verbose output
./compile -m -v        # Show detailed compilation logs (or --verbose)

# Debug mode
./compile -m -d        # Preserve intermediate files for debugging (or --debug)

# GPT Integration
./compile -m --citations  # Insert citations using GPT (or -c)
./compile -m --terms      # Check terminology using GPT (or -t)
./compile -m --revise     # Revise text using GPT
```

### Compilation Process

When you run `./compile`:

1. Figures and tables are processed (if --figs flag is used)
2. All text files from `contents/` are gathered
3. LaTeX is compiled to generate PDF
4. If requested, GPT processes the text (citations, terminology)
5. Output files are generated in the `main/` directory

### View Compilation Results

```bash
# Main manuscript
open manuscript/main/manuscript.pdf  # macOS
xdg-open manuscript/main/manuscript.pdf  # Linux

# Supplementary materials
open supplementary/main/supplementary.pdf

# Revision response
open revision/main/revision.pdf
```

## File Locations

### Content Files

```
manuscript/contents/
├── abstract.tex           # Abstract
├── introduction.tex       # Introduction
├── methods.tex            # Methods
├── results.tex            # Results
├── discussion.tex         # Discussion
├── bibliography.bib       # References in BibTeX format
├── latex_styles/                # Style definitions
│   ├── packages.tex       # Package imports
│   └── formatting.tex     # Format settings
```

### Asset Files

```
manuscript/contents/figures/
├── contents/                   # Figure source files (your files go here)
├── compiled/              # Auto-generated figure files (don't edit)
├── jpg/                   # Processed images (don't edit)
└── templates/             # Figure templates

manuscript/contents/tables/
├── contents/                   # Table source files (your files go here)
└── compiled/              # Auto-generated table files (don't edit)
```

### Output Files

```
manuscript/main/
├── manuscript.tex         # Auto-generated main LaTeX file
├── manuscript.pdf         # Output PDF
├── diff.tex               # Changes since last compilation
└── diff.pdf               # Visual diff of changes
```

## Troubleshooting

### Missing Figures

1. Check that figure files exist in the correct directory (`manuscript/contents/figures/contents/`)
2. Verify file naming matches the convention (`.XX_description.png`)
3. Ensure `--figs` flag was used during compilation
4. Check for errors in the figure caption file
5. Look at debug logs in `manuscript/contents/figures/compiled/debug/`
6. Try rebuilding with `./compile -m --figs --debug`

### Incorrect References

1. Verify label format in references (`fig:XX` for figures, `tab:XX` for tables)
2. Check that the figure/table number matches the filename
3. Remember the non-breaking space: `Figure~\ref{fig:XX}` (not `Figure\ref{fig:XX}`)
4. Run LaTeX compilation twice to resolve references
5. Check for proper label definition in the figure/table files

### Compilation Issues

1. Check log files in `.logs/` directory
2. Verify LaTeX syntax in caption files
3. Check for special characters in CSV files that might need escaping
4. Look at the detailed log with `./compile -m -v`
5. Ensure all required packages are installed
6. Verify no syntax errors in BibTeX files

### Common Errors

| Error Message | Likely Cause | Solution |
|---------------|--------------|----------|
| "File not found" | Missing figure/table file | Check path and filename |
| "Undefined reference" | Missing or incorrect label | Check reference format |
| "Missing $ inserted" | Special character in text | Escape special characters like % _ # & |
| "Missing \begin{document}" | LaTeX syntax error | Check for mismatched braces or commands |
| "Overfull \hbox" | Content too wide | Reduce table width or use landscape |

## Common Examples

### Multi-panel Figure Reference

```latex
As shown in Figure~\ref{fig:01}A, the process begins with data collection.
Figure~\ref{fig:01}B,C presents the analysis and results.
The complete workflow is illustrated in Figure~\ref{fig:01}.
```

### Table with Performance Metrics

```latex
Table~\ref{tab:01} summarizes the performance metrics of the system.
The improvement in accuracy (Table~\ref{tab:01}, column 3) was statistically significant.
```

### Cross-reference with Section

```latex
As discussed in Section~\ref{sec:methods} and illustrated in Figure~\ref{fig:02},
the processing pipeline consists of several steps.
```

### Citation Examples

```latex
Prior research has established this effect \citep{Smith2019}.
\citet{Johnson2020} demonstrated similar results in their work.
Multiple studies support this conclusion \citep{Wang2018, Miller2021, Davis2022}.
```

## Best Practices

### General Workflow

1. Create an outline before writing detailed content
2. Write modular content in separate files
3. Add figures and tables as you write
4. Compile frequently to catch errors early
5. Use version control (Git) to track changes

### Figure and Table Best Practices

1. Use descriptive filenames for figures and tables
2. Keep captions informative but concise
3. Always include panel labels (A, B, C, etc.) in multi-panel figures
4. Reference all figures and tables in the text
5. Use consistent formatting and labeling style

### Citations and References

1. Add complete citation information to BibTeX file
2. Use consistent citation keys (e.g., LastnameYear)
3. Include DOI when available
4. Verify journal names are consistent
5. Use \citet{} for in-text citations and \citep{} for parenthetical citations

### Final Preparation

1. Run spelling and grammar checks
2. Verify all references are correctly formatted
3. Check all figures and tables appear correctly
4. Ensure all citations in text have corresponding entries in the bibliography
5. Generate a final PDF with `./compile -m --figs`

## Additional Resources

- [FIGURE_TABLE_GUIDE.md](FIGURE_TABLE_GUIDE.md): Detailed guide for figure and table management
- [MULTIPANEL_FIGURE_GUIDE.md](MULTIPANEL_FIGURE_GUIDE.md): Instructions for complex multi-panel figures
- [COMPILATION_GUIDE.md](COMPILATION_GUIDE.md): Detailed explanation of the compilation process
- Examples directory: `examples/` contains sample code and templates