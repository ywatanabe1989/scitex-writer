---
description: |
  [TOPIC] scitex-writer CLI Reference
  [DETAILS] Top-level subcommands of `scitex-writer` — compile, bib, figures, tables, claims, mcp, migration, guidelines, prompts, launch-gui, etc.
tags: [scitex-writer-cli-reference]
---

# CLI Reference

`scitex-writer` is the entry point installed by `pip install scitex-writer`.

## Top-level options

| Flag                | Purpose                                                |
|---------------------|--------------------------------------------------------|
| `-V / --version`    | Show version and exit                                  |
| `--help-recursive`  | Show help for the root and every subcommand            |
| `--json`            | Emit machine-readable JSON output where supported      |
| `-h / --help`       | Show help                                              |

## Compile

| Command                  | Purpose                                          |
|--------------------------|--------------------------------------------------|
| `compile-manuscript`     | Compile the main manuscript to PDF               |
| `compile-supplementary`  | Compile supplementary materials to PDF           |
| `compile-revision`       | Compile a revision letter (response to reviews)  |
| `compile-content`        | Compile raw LaTeX content (file or stdin)        |

## Asset management

| Command     | Purpose                                                       |
|-------------|---------------------------------------------------------------|
| `bib`       | Bibliography management (`.bib` files and entries)            |
| `figures`   | Figure management (image files + caption + label)             |
| `tables`    | Table management (CSV-backed LaTeX tables)                    |

## Project / workflow

| Command            | Purpose                                                |
|--------------------|--------------------------------------------------------|
| `update-project`   | Update engine files in a scitex-writer project         |
| `migration`        | Import / export to external platforms (Overleaf)       |
| `export-manuscript`| Export the manuscript as an arXiv-ready tarball        |
| `launch-gui`       | Launch the browser-based editor                        |

## Reference / helpers

| Command            | Purpose                                                |
|--------------------|--------------------------------------------------------|
| `mcp`              | MCP (Model Context Protocol) server commands           |
| `guidelines`       | IMRAD writing guidelines for scientific manuscripts    |
| `prompts`          | Action prompts for manuscript workflows (AI2 Asta)     |
| `list-python-apis` | List the public Python API surface                     |
| `show-api`         | Print the public API tree of a Python package          |
| `show-usage`       | Print the long-form usage guide                        |

## Configuration precedence

```
1. Explicit CLI flags
2. ./config.yaml (project-local)
3. $SCITEX_WRITER_CONFIG (path to a YAML file)
4. ~/.scitex/writer/config.yaml (user-wide)
5. Built-in defaults
```

## Examples

```bash
scitex-writer compile-manuscript
scitex-writer bib add citation.bib
scitex-writer figures add results.png --caption "..." --label fig:main
scitex-writer migration import-overleaf <project-id>
scitex-writer mcp list-tools -vv
```

See `07_cli-reference.md` for prior detailed reference.
