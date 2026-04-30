---
name: scitex-writer
description: End-to-end LaTeX manuscript toolchain — 45 MCP tools — project (clone/info/get_pdf), compile (manuscript / supplementary / revision with tracked changes), BibTeX (add/list/get/remove/merge, dedup by DOI), figures + tables (add/list/remove/archive, csv_to_latex, pdf_to_images), claims (`\vclaim{}` linked to scitex-clew session hashes for verifiable assertions), checks (float order, references), export + Overleaf migration, per-journal guidelines, AI2 Asta prompts. Python API — `scitex_writer.{claim,compile,export,project,tables,figures,bib,guidelines,prompts,migration,checks}` submodules + `Writer` class + `ensure_workspace()` + `gui()` browser editor. Use whenever the user asks to compile manuscript / build PDF / supplementary / revision with tracked changes, add figure/table/bibentry, merge or dedup .bib, csv_to_latex, add a verifiable claim, audit float order, check references, export to arXiv, import/export Overleaf, or mentions IMRAD, \vclaim, `.scitex/writer/` workspace. Drop-in replacement for raw `latexmk` / `pdflatex` / `biber` loops, hand-rolled BibTeX dedup, `df.to_latex`, `pdf2image`, and manual Overleaf git sync.
allowed-tools: mcp__scitex__writer_*
primary_interface: mixed
interfaces:
  python: 1
  cli: 3
  mcp: 3
  skills: 2
  hook: 0
  http: 0
tags: [scitex-writer, scitex-package]
---

# scitex-writer

> **Interfaces:** Python ⭐ · CLI ⭐⭐⭐ · MCP ⭐⭐⭐ · Skills ⭐⭐ · Hook — · HTTP —

LaTeX manuscript compilation framework. Compiles manuscripts,
supplementary materials, and revisions with tracked changes. Manages
bibliography (BibTeX merge, DOI dedup), figures/tables (auto-discovery,
CSV-to-LaTeX), and verifiable claims linked to session hashes.

## Install & import

`pip install scitex-writer` gives `import scitex_writer as sw`. Also
`pip install scitex` to get `import scitex.writer as sw`. See
[../../general/02_interface-python-api.md].

## Core / interfaces

- [01_quick-start.md](01_quick-start.md) — basic workflow
- [02_cli-reference.md](02_cli-reference.md) — CLI reference
- [03_mcp-tools.md](03_mcp-tools.md) — MCP tools for AI agents

## Workflows

- [10_compilation.md](10_compilation.md) — compile manuscript/supp/revision
- [11_bibliography.md](11_bibliography.md) — BibTeX add/merge/dedup
- [12_figures-and-tables.md](12_figures-and-tables.md) — figure/table lifecycle
- [13_claims.md](13_claims.md) — verifiable `\vclaim{}` with session hash
- [14_manuscript-workflow.md](14_manuscript-workflow.md) — end-to-end workflow
- [15_audit-paper.md](15_audit-paper.md) — pre-submission audit: cross-refs + tables
- [16_audit-paper-figures-data.md](16_audit-paper-figures-data.md) — audit: figures, variables, data
- [17_audit-paper-methods-output.md](17_audit-paper-methods-output.md) — audit: methods, structure, cross-doc, pitfalls

## Scientific writing standards

- [20_writing-attitude.md](20_writing-attitude.md) — evidence, critical analysis
- [21_writing-proofreading.md](21_writing-proofreading.md) — language rules, corrections, section-specific
- [22_writing-figures-stats.md](22_writing-figures-stats.md) — figure rules, stats reporting
- [23_writing-mermaid.md](23_writing-mermaid.md) — academic mermaid style
- [24_writing-proofreading-style.md](24_writing-proofreading-style.md) — tone, hedging, transitions, anti-patterns

## Section templates

- [30_writing-abstract.md](30_writing-abstract.md) — 7-section abstract
- [31_writing-introduction.md](31_writing-introduction.md) — 8-section introduction template
- [32_writing-methods.md](32_writing-methods.md) — reproducibility-focused methods
- [33_writing-discussion.md](33_writing-discussion.md) — 5-section discussion template
- [34_writing-introduction-example.md](34_writing-introduction-example.md) — intro section tags + example
- [35_writing-discussion-example.md](35_writing-discussion-example.md) — discussion section tags + example


## Environment

- [40_env-vars.md](40_env-vars.md) — SCITEX_* env vars read by scitex-writer at runtime
