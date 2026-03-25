---
description: LaTeX manuscript compilation with bibliography, figures, tables, claims tracking, and journal guideline enforcement.
allowed-tools: mcp__scitex__writer_*
---

# scitex-writer

LaTeX manuscript compilation framework for scientific papers.

## Sub-skills

- [quick-start.md](quick-start.md) — Basic manuscript workflow
- [compilation.md](compilation.md) — Compile manuscript, supplementary, revision
- [bibliography.md](bibliography.md) — BibTeX management, enrichment
- [figures-and-tables.md](figures-and-tables.md) — Figure/table insertion and conversion
- [claims.md](claims.md) — Claim tracking and rendering
- [cli-reference.md](cli-reference.md) — CLI commands
- [mcp-tools.md](mcp-tools.md) — MCP tools for AI agents

## CLI

```bash
scitex-writer <command> [options]
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `writer_compile_manuscript` | Compile LaTeX manuscript to PDF |
| `writer_compile_content` | Compile content sections |
| `writer_compile_supplementary` | Compile supplementary materials |
| `writer_compile_revision` | Compile revision with tracked changes |
| `writer_add_figure` | Add figure to manuscript |
| `writer_add_table` | Add table to manuscript |
| `writer_add_bibentry` | Add bibliography entry |
| `writer_add_claim` | Add verifiable claim |
| `writer_render_claims` | Render claims to LaTeX |
| `writer_export_manuscript` | Export for submission |
| `writer_export_overleaf` | Export to Overleaf format |
