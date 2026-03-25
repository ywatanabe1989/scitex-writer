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

## Scientific Writing

- [writing-attitude.md](writing-attitude.md) — Evidence requirements, critical analysis, scientific standards
- [writing-figures-stats.md](writing-figures-stats.md) — Figure rules, statistical reporting, document format
- [writing-proofreading.md](writing-proofreading.md) — Proofreading corrections, language rules, formatting
- [writing-abstract.md](writing-abstract.md) — Abstract template with 7-section structure
- [writing-introduction.md](writing-introduction.md) — Introduction template with 8-section structure
- [writing-methods.md](writing-methods.md) — Methods template with reproducibility guidelines
- [writing-discussion.md](writing-discussion.md) — Discussion template with 5-section structure
- [writing-mermaid.md](writing-mermaid.md) — Academic mermaid diagram style guide

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
