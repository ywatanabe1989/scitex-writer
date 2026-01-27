# SciTeX Writer MCP Tools (29 total)

Model Context Protocol tools for AI agent integration.

```bash
scitex-writer mcp list-tools    # List all tools
scitex-writer mcp start         # Start MCP server (stdio)
```

## Tools by Category

| Category | Tool | Description |
|----------|------|-------------|
| **add** (3) | `add_bibentry` | Add a BibTeX entry to a bibliography file. |
|  | `add_figure` | Add a figure (copy image + create caption) to the  |
|  | `add_table` | Add a new table (CSV + caption) to the project. |
| **clone** (1) | `clone_project` | Create a new LaTeX manuscript project from templat |
| **compile** (4) | `compile_content` | Compile raw LaTeX content to PDF with color mode. |
|  | `compile_manuscript` | Compile manuscript LaTeX document to PDF. |
|  | `compile_revision` | Compile revision document to PDF with optional cha |
|  | `compile_supplementary` | Compile supplementary materials LaTeX document to  |
| **convert** (1) | `convert_figure` | Convert figure between formats (e.g., PDF to PNG). |
| **csv** (1) | `csv_to_latex` | Convert CSV file to LaTeX table format. |
| **general** (1) | `usage` | Get usage guide for SciTeX Writer LaTeX manuscript |
| **get** (3) | `get_bibentry` | Get a specific BibTeX entry by citation key. |
|  | `get_pdf` | Get path to compiled PDF for a document type. |
|  | `get_project_info` | Get writer project structure and status informatio |
| **guideline** (3) | `guideline_build` | Build editing prompt by combining guideline with d |
|  | `guideline_get` | Get IMRAD writing guideline for a manuscript secti |
|  | `guideline_list` | List available IMRAD writing guideline sections. |
| **latex** (1) | `latex_to_csv` | Convert LaTeX table to CSV format. |
| **list** (5) | `list_bibentries` | List all BibTeX entries in the project or specific |
|  | `list_bibfiles` | List all bibliography files in the project. |
|  | `list_document_types` | List available document types in a writer project. |
|  | `list_figures` | List all figures in a writer project directory. |
|  | `list_tables` | List all tables in a writer project. |
| **merge** (1) | `merge_bibfiles` | Merge all .bib files into one, with optional dedup |
| **pdf** (1) | `pdf_to_images` | Render PDF pages as images. |
| **prompts** (1) | `prompts_asta` | Generate AI2 Asta prompt for finding related paper |
| **remove** (3) | `remove_bibentry` | Remove a BibTeX entry by citation key. |
|  | `remove_figure` | Remove a figure (image + caption) from the project |
|  | `remove_table` | Remove a table (CSV + caption) from the project. |
