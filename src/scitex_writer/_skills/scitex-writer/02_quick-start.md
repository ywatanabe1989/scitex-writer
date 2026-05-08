---
description: |
  [TOPIC] scitex-writer Quick Start
  [DETAILS] Smallest useful example — clone a project template and compile a manuscript via the CLI.
tags: [scitex-writer-quick-start]
---

# Quick Start

## Clone a project template and compile

```bash
scitex-writer migration clone my-paper
cd my-paper
scitex-writer compile-manuscript
```

The compiled PDF lands under `out/manuscript.pdf`. Re-running the same
command picks up edits to `manuscript.tex`, figures under `figures/`,
and BibTeX entries under `bib/`.

## Add a figure / table / bib entry

```bash
scitex-writer figures add results.png --caption "Main result" --label fig:main
scitex-writer tables  add stats.csv  --caption "Test stats" --label tab:stats
scitex-writer bib     add citation.bib
```

## Python API

```python
import scitex_writer as sw

w = sw.Writer(project_dir="./my-paper")
result = w.compile_manuscript()
print(result.pdf_path)
```

## Next steps

- `06_quick-start.md` — extended walkthrough
- `04_cli-reference.md` — full CLI surface
- `10_compilation.md` — manuscript / supp / revision modes
- `13_claims.md` — verifiable `\vclaim{}` linked to scitex-clew sessions
