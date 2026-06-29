---
description: |
  [TOPIC] Figures and Tables
  [DETAILS] Add, list, and manage figures and tables in manuscripts..
tags: [scitex-writer-figures-and-tables]
---

# Figures and Tables

## File Structure

The compile script auto-discovers figures and tables from source directories:

```
01_manuscript/contents/figures/
├── caption_and_media/       # Source: .tex captions + .jpg/.png images
│   ├── 01_clew_dag.tex      # Caption/label
│   ├── 01_clew_dag.jpg      # Image file
│   ├── jpg_for_compilation/ # JPGs used by latexmk
│   └── mermaid_originals/   # Mermaid source .mmd files
├── compiled/                # Auto-generated from caption_and_media/
│   ├── FINAL.tex            # Auto-generated: includes all figures
│   └── 01_clew_dag.tex      # Auto-generated per figure
└── legacy/                  # Dropped figures (not deleted, preserved)
```

Tables follow the same structure under `01_manuscript/contents/tables/`.

## Removing a Figure from the Manuscript

The compile script rebuilds `compiled/FINAL.tex` from whatever `.tex` files exist in `caption_and_media/`. To remove a figure, you must move **all** associated files:

```bash
# Move ALL files for a figure to legacy/
mkdir -p 01_manuscript/contents/figures/legacy
for ext in tex jpg png mmd; do
  mv -f "01_manuscript/contents/figures/caption_and_media/${NAME}.${ext}" \
       "01_manuscript/contents/figures/legacy/" 2>/dev/null
done

# Also clean subdirectories
mv -f "01_manuscript/contents/figures/caption_and_media/jpg_for_compilation/${NAME}.jpg" \
     "01_manuscript/contents/figures/legacy/" 2>/dev/null
```

If you only move the `.tex` caption, the compile script will recreate it from the remaining image files.

## Moving Tables to Supplementary

Move all table source files out of `caption_and_media/`:

```bash
mkdir -p 01_manuscript/contents/tables/legacy
mv -f 01_manuscript/contents/tables/caption_and_media/*.tex \
     01_manuscript/contents/tables/legacy/
mv -f 01_manuscript/contents/tables/caption_and_media/*.csv \
     01_manuscript/contents/tables/legacy/
```

Reference tables as Supplementary Tables (S1, S2, ...) in the manuscript text.
(Supplementary figures/tables are auto-numbered with the `S` prefix by the
`02_supplementary` template.)

## CSV table-header conventions

Author CSV column headers as the FINAL rendered label — the csv→LaTeX converter
passes them through faithfully (it no longer title-cases or strips them):

- **Math** renders when written in `$...$`: `$n_{\mathrm{SZ}}$`, `$F_1$`,
  `Sens$_{15}$`, `$R^2$` (a header containing `$` or `\` is emitted verbatim).
- **Human labels** read as written: `SOP (min)`, `# of Patients`, `ROC-AUC` —
  NOT raw underscore-derived `SOP min` / `n patients` / `n SZ`. Use real words
  and spaces (or math) in the header, not `snake_case`.
- Numeric **columns auto-align** to a consistent decimal precision (a column
  with `0.333` and `0.35` renders `0.333` / `0.350`); all-integer count columns
  stay bare.

## Archiving Figures and Tables

Use the `archive()` function to move figures/tables to `legacy/` without deleting them:

```python
import scitex_writer as sw

# Archive a figure (moves all files to legacy/)
sw.figures.archive(project_dir, "01_clew_dag")

# Archive a table
sw.tables.archive(project_dir, "01_results")
```

The `remove()` function recursively cleans all subdirectories including `jpg_for_compilation/` and `mermaid_originals/`.

## Format Conversion Notes

- PNG-to-JPG conversion flattens alpha channels onto a white background (`-background white -flatten`)
- This prevents transparent regions from appearing as black in the compiled PDF

## MCP Tools

| Tool | Description |
|------|-------------|
| `writer_figures_add` | Add figure to manuscript |
| `writer_figures_list` | List all figures |
| `writer_figures_remove` | Remove a figure (recursively cleans subdirectories) |
| `writer_tables_add` | Add table to manuscript |
| `writer_tables_list` | List all tables |
| `writer_tables_remove` | Remove a table |
| `writer_figures_convert` | Convert figure format |
| `writer_tables_csv_to_latex` | Convert CSV to LaTeX table |
| `writer_tables_latex_to_csv` | Convert LaTeX table to CSV |
| `writer_figures_pdf_to_images` | Convert PDF pages to images |
