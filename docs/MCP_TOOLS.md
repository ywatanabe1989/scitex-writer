# SciTeX Writer MCP Tools (29 total)

Model Context Protocol tools for AI agent integration.

```bash
scitex-writer mcp list-tools    # List all tools
scitex-writer mcp start         # Start MCP server (stdio)
scitex-writer mcp doctor        # Health check
scitex-writer mcp installation  # Show Claude Desktop config
```

## Tools by Module

### bib (6 tools)
| Tool | Description |
|------|-------------|
| `writer_add_bibentry` | Add a BibTeX entry to a bibliography file |
| `writer_get_bibentry` | Get a specific BibTeX entry by citation key |
| `writer_list_bibentries` | List all BibTeX entries in the project |
| `writer_list_bibfiles` | List all bibliography files in the project |
| `writer_merge_bibfiles` | Merge all .bib files into one, with deduplication |
| `writer_remove_bibentry` | Remove a BibTeX entry by citation key |

### compile (4 tools)
| Tool | Description |
|------|-------------|
| `writer_compile_content` | Compile raw LaTeX content to PDF with color modes |
| `writer_compile_manuscript` | Compile manuscript LaTeX document to PDF |
| `writer_compile_revision` | Compile revision document to PDF with change tracking |
| `writer_compile_supplementary` | Compile supplementary materials to PDF |

### figures (5 tools)
| Tool | Description |
|------|-------------|
| `writer_add_figure` | Add a figure (copy image + create caption) |
| `writer_convert_figure` | Convert figure between formats (e.g., PDF to PNG) |
| `writer_list_figures` | List all figures in a writer project |
| `writer_pdf_to_images` | Render PDF pages as images |
| `writer_remove_figure` | Remove a figure (image + caption) |

### general (1 tool)
| Tool | Description |
|------|-------------|
| `usage` | Get usage guide for SciTeX Writer |

### guidelines (3 tools)
| Tool | Description |
|------|-------------|
| `writer_guideline_build` | Build editing prompt by combining guideline with draft |
| `writer_guideline_get` | Get IMRAD writing guideline for a manuscript section |
| `writer_guideline_list` | List available IMRAD writing guideline sections |

### project (4 tools)
| Tool | Description |
|------|-------------|
| `writer_clone_project` | Create a new LaTeX manuscript project from template |
| `writer_get_pdf` | Get path to compiled PDF for a document type |
| `writer_get_project_info` | Get writer project structure and status |
| `writer_list_document_types` | List available document types in a writer project |

### prompts (1 tool)
| Tool | Description |
|------|-------------|
| `writer_prompts_asta` | Generate AI2 Asta prompt for finding related papers |

### tables (5 tools)
| Tool | Description |
|------|-------------|
| `writer_add_table` | Add a new table (CSV + caption) to the project |
| `writer_csv_to_latex` | Convert CSV file to LaTeX table format |
| `writer_latex_to_csv` | Convert LaTeX table to CSV format |
| `writer_list_tables` | List all tables in a writer project |
| `writer_remove_table` | Remove a table (CSV + caption) from the project |

## Claude Desktop Configuration

Add to `~/.config/Claude/claude_desktop_config.json` (Linux) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "scitex-writer": {
      "command": "scitex-writer",
      "args": ["mcp", "start"]
    }
  }
}
```
