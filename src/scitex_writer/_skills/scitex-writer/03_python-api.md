---
description: |
  [TOPIC] scitex-writer Python API
  [DETAILS] Top-level public surface — Writer facade, ensure_workspace, gui launcher, usage helper, dataclass result types, and submodule namespaces (bib, claim, compile, figures, tables, project, migration, guidelines, prompts, export).
tags: [scitex-writer-python-api]
---

# Python API

Top-level public surface re-exported from `scitex_writer`.

## Core

| Name                | Purpose                                                  |
|---------------------|----------------------------------------------------------|
| `Writer`            | Project facade — compile, manage figures/tables/bib      |
| `ensure_workspace`  | Set up a project workspace (idempotent)                  |
| `gui`               | Launch the browser-based editor (Django-backed)          |
| `usage`             | Long-form usage guide as a string                        |

## Result dataclasses (re-exported under `_*` aliases)

| Name                      | Returned by                                |
|---------------------------|--------------------------------------------|
| `_CompilationResult`      | `Writer.compile_manuscript()` etc.         |
| `_ManuscriptTree`         | Manuscript directory introspection         |
| `_RevisionTree`           | Revision letter introspection              |
| `_SupplementaryTree`      | Supplementary materials introspection      |

## Submodule namespaces

| Module       | Purpose                                                |
|--------------|--------------------------------------------------------|
| `bib`        | List / add / remove / merge BibTeX entries             |
| `claim`      | `\vclaim{}` traceable assertions                       |
| `compile`    | Compile manuscript / supplementary / revision          |
| `figures`    | List / add / remove / convert figure assets            |
| `tables`     | List / add / remove / `csv_to_latex`                   |
| `project`    | Clone, info, get_pdf                                   |
| `migration`  | Import / export Overleaf, arXiv tarballs               |
| `guidelines` | IMRAD writing tips                                     |
| `prompts`    | AI2 Asta prompts for manuscript workflows              |
| `export`     | Export for arXiv submission                            |

## Example

```python
import scitex_writer as sw

w = sw.Writer(project_dir="./paper")
result = w.compile_manuscript()
assert result.success
print(result.pdf_path, result.log_excerpt)
```

See `07_cli-reference.md` for the legacy CLI reference and
`08_mcp-tools.md` for the MCP tool catalog.
