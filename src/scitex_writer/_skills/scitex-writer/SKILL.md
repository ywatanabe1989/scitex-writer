---
name: scitex-writer
description: End-to-end LaTeX manuscript toolchain — 45 MCP tools — project (clone/info/get_pdf), compile (manuscript / supplementary / revision with tracked changes), BibTeX (add/list/get/remove/merge, dedup by DOI), figures + tables (add/list/remove/archive, csv_to_latex, pdf_to_images), claims (`\vclaim{}` linked to scitex-clew session hashes for verifiable assertions), checks (float order, references), export + Overleaf migration, per-journal guidelines (Nature/Science/PNAS/...), AI2 Asta prompts. Python API — `scitex_writer.{claim,compile,export,project,tables,figures,bib,guidelines,prompts,migration,checks}` submodules + `Writer` class + `ensure_workspace()` + `gui()` browser editor. Use whenever the user asks to compile manuscript / build PDF / supplementary / revision with tracked changes, add figure/table/bibentry, merge or dedup .bib, csv_to_latex, add a verifiable claim, audit float order, check references, export to arXiv, import/export Overleaf, show guidelines for a target journal, or mentions IMRAD, \vclaim, `.scitex/writer/` workspace. Drop-in replacement for raw `latexmk` / `pdflatex` / `biber` loops, hand-rolled BibTeX dedup, `df.to_latex`, `pdf2image`, and manual Overleaf git sync.
allowed-tools: mcp__scitex__writer_*
---

# scitex-writer

LaTeX manuscript compilation framework. Compiles manuscripts,
supplementary materials, and revisions with tracked changes. Manages
bibliography (BibTeX merge, DOI dedup, enrichment), figures/tables
(auto-discovery from `caption_and_media/`, CSV-to-LaTeX), and verifiable
claims linked to session hashes via `sw.claim.add()`.

## Installation & import (two equivalent paths)

The same module is reachable via two install paths. Both forms work at
runtime; which one a user has depends on their install choice.

```python
# Standalone — pip install scitex-writer
import scitex_writer as sw
sw.CompilationResult(...)

# Umbrella — pip install scitex
import scitex.writer as sw
sw.CompilationResult(...)
```

`pip install scitex-writer` alone does NOT expose the `scitex` namespace;
`import scitex.writer` raises `ModuleNotFoundError`. To use the
`scitex.writer` form, also `pip install scitex`.

See [../../general/02_interface-python-api.md] for the ecosystem-wide
rule and empirical verification table.

## Core / interfaces

- [01_quick-start.md](01_quick-start.md) — basic workflow: create project, add content, compile PDF
- [02_cli-reference.md](02_cli-reference.md) — CLI commands reference
- [03_mcp-tools.md](03_mcp-tools.md) — MCP tools for AI agents

## Workflows

- [10_compilation.md](10_compilation.md) — compile manuscript/supplementary/revision, env vars
- [11_bibliography.md](11_bibliography.md) — BibTeX add/list/merge/enrich, DOI dedup
- [12_figures-and-tables.md](12_figures-and-tables.md) — figure/table lifecycle, supplementary moves
- [13_claims.md](13_claims.md) — verifiable claims with session hash + `\vclaim{}` rendering
- [14_manuscript-workflow.md](14_manuscript-workflow.md) — end-to-end manuscript workflow
- [15_audit-paper.md](15_audit-paper.md) — pre-submission audit: numbers, citations, figure-text alignment

## Scientific writing standards

- [20_writing-attitude.md](20_writing-attitude.md) — evidence requirements, critical analysis
- [21_writing-proofreading.md](21_writing-proofreading.md) — language rules, anti-patterns, tone, hedging
- [22_writing-figures-stats.md](22_writing-figures-stats.md) — figure rules, stats reporting (effect sizes, FDR)
- [23_writing-mermaid.md](23_writing-mermaid.md) — academic mermaid diagram style guide

## Section templates

- [30_writing-abstract.md](30_writing-abstract.md) — 7-section abstract structure
- [31_writing-introduction.md](31_writing-introduction.md) — 8-section introduction structure
- [32_writing-methods.md](32_writing-methods.md) — reproducibility-focused methods, passive voice
- [33_writing-discussion.md](33_writing-discussion.md) — 5-section discussion structure
