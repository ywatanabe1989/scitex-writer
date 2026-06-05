---
description: |
  [TOPIC] Manuscript Workflow
  [DETAILS] Complete manuscript workflow from project creation to submission..
tags: [scitex-writer-manuscript-workflow]
---

# Manuscript Workflow

## 1. Create Project
```bash
scitex template clone-template research-paper ./my-paper/
```

## 2. Write Sections
Edit LaTeX files in `sections/`: abstract, introduction, methods, results, discussion.

## 3. Add Figures
```bash
scitex-writer figures add ./my-paper/ fig.png --caption "Results" --label fig:results
```

## 4. Add Tables
```bash
scitex-writer tables add ./my-paper/ data.csv --caption "Summary" --label tab:summary
```

## 5. Manage Bibliography
```bash
scitex-writer bib add ./my-paper/ --doi 10.1038/s41586-024-00001-1
scitex-writer bib enrich ./my-paper/references.bib
```

## 6. Track Claims
Link claims to computational evidence for reproducibility.

## 7. Check Guidelines
```bash
scitex-writer guidelines get nature
```

## 8. Compile
```bash
scitex-writer compile manuscript ./my-paper/
scitex-writer compile supplementary ./my-paper/
scitex-writer compile revision ./my-paper/
```

## 9. Export
```bash
scitex-writer export overleaf ./my-paper/ -o overleaf/
scitex-writer export manuscript ./my-paper/ -o submission/
```

## Directory Structure
```
my-paper/
├── main.tex
├── sections/{abstract,introduction,methods,results,discussion}.tex
├── figures/
├── tables/
├── references.bib
├── claims.yaml
└── project.yaml
```

## Project layout convention — `<proj-root>/paper -> .scitex/writer`

A scitex-writer manuscript inside a scitexified analysis lives at
`<proj-root>/.scitex/writer/` (the canonical `.scitex/<pkg-short>/`
local-state location). A convenience symlink at the project root makes
the manuscript reachable without the `.scitex/writer/` prefix:

```bash
# from <proj-root>
ln -s .scitex/writer paper
```

After this, `<proj-root>/paper/` and
`<proj-root>/.scitex/writer/` refer to the same directory. The
symlink is **a convenience for humans and tooling**, not a different
location.

### Why both names

- `.scitex/writer/` is the canonical, ecosystem-consistent location —
  it parallels `.scitex/io/`, `.scitex/clew/`, `.scitex/session/`,
  etc., so the writer artefacts sit under the same per-package
  local-state convention used by every other scitex package (see
  `~/.claude/skills/scitex/scientific/02_research-project_03_project-structure-config-and-data.md`
  for the `<project>/.scitex/<pkg-short>/` layout).
- `paper/` is the discoverable, human-friendly path — when a
  collaborator clones the project and looks for "where is the
  manuscript", `paper/` is the obvious shape.

Both names should always resolve to the same place. The symlink
ensures it.

### How to create / recreate

```bash
# create (idempotent: -f overwrites a stale symlink)
ln -sfn .scitex/writer paper

# verify it points where you expect
readlink paper      # → .scitex/writer
ls -l paper          # → paper -> .scitex/writer
```

If `paper/` is a real directory (not a symlink), STOP — that's a
broken setup. Either the project was created before the convention
existed (move its contents under `.scitex/writer/` then create the
symlink), or someone bypassed the convention (decide whether to
re-enforce or leave alone, but never have both a real `paper/` AND
a `.scitex/writer/` carrying different content).

### Pre-commit / Makefile target

If practical, wire the symlink check into the project's Makefile so
it gets reinstated automatically after a fresh checkout:

```makefile
.PHONY: paper-symlink
paper-symlink:
	@if [ ! -L paper ]; then ln -sfn .scitex/writer paper; fi
```

### Tooling consequences

- scitex-writer CLI commands accept either path — both resolve via the
  filesystem. Use whichever reads cleaner in the recipe.
- LaTeX `\input{}` and `\includegraphics{}` paths inside the manuscript
  should be RELATIVE to the manuscript file, not absolute — this way
  they work via either name.
- `git status` resolves the symlink target, so committed paths use
  `.scitex/writer/...` (the canonical name). The symlink itself is
  not committed (it's local convenience; recreate via the Makefile
  target on clone).
