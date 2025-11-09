# Quick Start Guide

Fast reference for common tasks and workflows in SciTeX.

## Basic Workflow

1. Edit content files in `manuscript/contents/`
2. Add figures to `manuscript/contents/figures/contents/`
3. Add tables to `manuscript/contents/tables/contents/`
4. Update bibliography in `00_shared/bibliography.bib`
5. Compile with `./compile`
6. View PDF at `manuscript/main/manuscript.pdf`

## Project Structure

```
SciTeX/
├── 01_manuscript/      # Main manuscript
│   ├── contents/       # Source files
│   │   ├── figures/    # Figure files
│   │   ├── tables/     # Table files
│   │   └── *.tex       # Content (intro, methods, etc.)
├── 02_supplementary/   # Supplementary materials
├── 03_revision/        # Revision responses
├── 00_shared/             # Shared metadata
├── docs/               # Documentation
└── scripts/            # Compilation scripts
```

## Common Commands

```bash
# Full compilation
./compile_manuscript

# Compile with figures
./compile_manuscript --figs

# Show changes from previous version
./compile_manuscript --diff

# Debug mode with verbose output
./compile_manuscript --debug
```

## Content Files

**Manuscript sections** in `manuscript/contents/`:
- `abstract.tex` - Abstract
- `introduction.tex` - Introduction
- `methods.tex` - Methods
- `results.tex` - Results
- `discussion.tex` - Discussion

**Shared metadata** in `00_shared/`:
- `authors.tex` - Author list
- `title.tex` - Title
- `keywords.tex` - Keywords
- `bibliography.bib` - References

## Quick Tasks

### Add a Figure

1. Create PNG/JPG (300 DPI)
2. Name: `.01_description.png`
3. Place in: `manuscript/contents/figures/contents/`
4. Create caption: `.01_description.tex`
5. Reference in text: `Figure~\ref{fig:01}`

### Add a Table

1. Create CSV data file
2. Name: `.01_description.csv`
3. Place in: `manuscript/contents/tables/contents/`
4. Create caption: `.01_description.tex`
5. Reference in text: `Table~\ref{tab:01}`

### Add a Citation

1. Add to `00_shared/bibliography.bib`:
```bibtex
@article{Smith2023,
  author = {Smith, John},
  title = {Title},
  journal = {Journal},
  year = {2023}
}
```

2. Cite in text: `\cite{Smith2023}`

### Update Authors

Edit `00_shared/authors.tex`:
```latex
John Smith\textsuperscript{1,*},
Jane Doe\textsuperscript{1,2}

\textsuperscript{1}Department, University
\textsuperscript{2}Other Department, University
```

### Update Title/Keywords

- Title: `00_shared/title.tex`
- Keywords: `00_shared/keywords.tex`

## File Naming

**Figures**: `.XX_name.{png|jpg|tif|mmd}`
- Example: `.01_workflow.png`

**Tables**: `.XX_name.csv`
- Example: `.01_results.csv`

**Captions**: `.XX_name.tex`
- Example: `.01_workflow.tex`

## Compilation Output

After compilation:
- `manuscript.pdf` - Final manuscript
- `diff.pdf` - Changes from previous version
- Debug info in `compiled/debug/`

## Troubleshooting

**Figure not appearing**:
- Check file exists
- Verify naming (must start with `.`)
- Both PNG and TEX files must have same name

**Bibliography errors**:
- Check syntax in `.bib` file
- Verify all `\cite{}` keys exist in bibliography

**Compilation fails**:
- Check for LaTeX errors in content
- Verify all linked files exist
- Review compiler output for details

## Best Practices

1. **Version control**: Commit changes regularly
   ```bash
   git add manuscript/contents/
   git commit -m "Update results section"
   ```

2. **Consistent naming**: Use descriptive names
   - `.01_methods_overview.png` (good)
   - `.01_Fig.png` (bad)

3. **High-quality figures**: 300 DPI minimum
   - Use PNG for screenshots
   - Use EPS/PDF for diagrams

4. **Clear captions**: Explain each figure/table
   - What is shown
   - Why it matters
   - How to interpret

5. **Regular backups**: Use git or external storage

## More Information

- Full content guide: `01_GUIDE_CONTENT_CREATION.md`
- AI agent guide: `G_AGENTS.md`
- For language-specific standards: `to_claude/guidelines/`
