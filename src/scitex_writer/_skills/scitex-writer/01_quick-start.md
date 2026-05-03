---
description: |
  [TOPIC] Quick Start
  [DETAILS] Basic manuscript workflow — create project, add content, compile PDF..
tags: [scitex-writer-quick-start]
---

# Quick Start

```python
import scitex_writer as sw

# Create or open a project
writer = sw.Writer("/path/to/project")

# Compile manuscript to PDF
result = writer.compile_manuscript()
# result.pdf_path → Path to generated PDF

# Compile supplementary
result = writer.compile_supplementary()

# Compile revision with tracked changes
result = writer.compile_revision()

# Get compiled PDF
pdf = writer.get_pdf("manuscript")

# Ensure workspace structure
sw.ensure_workspace("/path/to/project", git_strategy="child")
```

## Pre-compilation checks (#44, #45)

```python
import scitex_writer as sw

# Validate every \ref / \cite / \label resolves (otherwise PDF shows ??)
result = sw.checks.references("./my-paper")
if result["summary"]["errors"]:
    raise SystemExit(result["stdout"])

# Validate figure/table reference order, preview the renumber, then apply
sw.checks.float_order("./my-paper", dry_run=True)
sw.checks.float_order("./my-paper", fix=True)
```

Both return ``{success, exit_code, summary, stdout, stderr}``. Same
logic is exposed over MCP as ``writer_check_references`` and
``writer_check_float_order``, and wired into ``check_project.sh``.

## Key Classes

- `Writer` — Main class for manuscript operations
- `CompilationResult` — Result of compilation (pdf_path, log, success)
- `ManuscriptTree` — Manuscript directory structure
- `RevisionTree` — Revision directory structure
- `SupplementaryTree` — Supplementary materials structure
