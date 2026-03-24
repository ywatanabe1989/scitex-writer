---
name: scitex-writer
description: LaTeX manuscript compilation with bibliography, figures, tables, claims tracking, and journal guideline enforcement. Use when writing, compiling, or managing scientific papers.
allowed-tools: mcp__scitex__writer_*
---

# Scientific Manuscript Writing with scitex-writer

## Quick Start

```python
from scitex_writer import compile_manuscript, add_figure, add_bibentry

# Compile manuscript to PDF
compile_manuscript("./project/")

# Add a figure
add_figure("./project/", "fig1.png", caption="Results overview", label="fig:results")

# Add bibliography entry
add_bibentry("./project/", doi="10.1038/s41586-024-00001-1")
```

## Common Workflows

### "Compile my manuscript"

```bash
scitex-writer compile manuscript ./project/
scitex-writer compile supplementary ./project/
```

### "Manage bibliography"

```bash
scitex-writer bib add ./project/ --doi 10.1038/s41586-024-00001-1
scitex-writer bib enrich ./project/references.bib
scitex-writer bib merge ./project/ -o merged.bib
scitex-writer bib list ./project/
```

### "Add figures and tables"

```bash
scitex-writer figures add ./project/ fig1.png --caption "Results" --label fig:results
scitex-writer tables add ./project/ results.csv --caption "Main results"
scitex-writer tables csv-to-latex data.csv
```

### "Track claims"

```python
writer_add_claim(project_dir="./project/",
    claim="Model achieves 95% accuracy",
    evidence="results/accuracy.csv", section="results")
writer_render_claims(project_dir="./project/")
```

### "Export"

```bash
scitex-writer export overleaf ./project/ -o overleaf_export/
scitex-writer export manuscript ./project/ -o submission/
```

### "Check journal guidelines"

```bash
scitex-writer guidelines list
scitex-writer guidelines get nature
```

## CLI Commands

```bash
# Compilation
scitex-writer compile manuscript|supplementary|revision ./project/

# Bibliography
scitex-writer bib add|list|enrich|merge ./project/

# Figures & Tables
scitex-writer figures add|list|convert ./project/
scitex-writer tables add|list|csv-to-latex ./project/

# Export
scitex-writer export overleaf|manuscript ./project/

# Guidelines & Prompts
scitex-writer guidelines list|get
scitex-writer prompts asta

# Skills
scitex-writer skills list
scitex-writer skills get SKILL
scitex-writer skills get manuscript-workflow
```

## MCP Tools (for AI agents)

| Tool | Purpose |
|------|---------|
| `writer_compile_manuscript` | Compile LaTeX to PDF |
| `writer_compile_supplementary` | Compile supplementary materials |
| `writer_compile_revision` | Compile revision with tracked changes |
| `writer_add_figure` | Add figure to manuscript |
| `writer_list_figures` | List figures in project |
| `writer_add_table` | Add table to manuscript |
| `writer_list_tables` | List tables |
| `writer_csv_to_latex` | Convert CSV to LaTeX table |
| `writer_add_bibentry` | Add bibliography entry |
| `writer_list_bibentries` | List all bib entries |
| `writer_merge_bibfiles` | Merge .bib files |
| `writer_enrich_bibtex` | Enrich with metadata |
| `writer_add_claim` | Add tracked claim |
| `writer_list_claims` | List all claims |
| `writer_render_claims` | Render claims with status |
| `writer_guideline_list` | List journal guidelines |
| `writer_guideline_get` | Get specific guideline |
| `writer_export_manuscript` | Export manuscript |
| `writer_export_overleaf` | Export for Overleaf |
| `writer_get_project_info` | Get project metadata |
| `writer_get_pdf` | Get compiled PDF |

## Specific Topics

* **Manuscript workflow** [references/manuscript-workflow.md](references/manuscript-workflow.md)
