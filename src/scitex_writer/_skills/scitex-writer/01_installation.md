---
description: |
  [TOPIC] scitex-writer Installation
  [DETAILS] pip install scitex-writer with optional [desktop], [editor], [scholar], [all] extras; smoke verify.
tags: [scitex-writer-installation]
---

# Installation

## Standard

```bash
pip install scitex-writer
```

## Optional extras

| Extra      | Adds                                          |
|------------|-----------------------------------------------|
| `desktop`  | pywebview (native desktop GUI shell)          |
| `editor`   | reserved (no extra deps yet)                  |
| `scholar`  | scitex-scholar (BibTeX enrichment integration)|
| `all`      | desktop + editor + scholar                    |

```bash
pip install 'scitex-writer[scholar]'
pip install 'scitex-writer[all]'
```

LaTeX itself (a TeX distribution such as TeX Live) must be available on
`PATH` for compilation — `scitex-writer` shells out to `latexmk` /
`pdflatex` / `bibtex`.

## Verify

```bash
python -c "import scitex_writer; print(scitex_writer.__version__)"
scitex-writer --help
```
