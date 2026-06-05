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

## Per-figure symlink rule

Figure outputs produced by FigRecipe + `stx.io.save(fig, ...)` land
in the canonical scitexified analysis path (typically
`<proj-root>/data/results/figures/`). They are placed into
`<proj-root>/.scitex/writer/` (equivalently `<proj-root>/paper/` via
the symlink above) **via a per-figure symlink, NOT a copy**.

```bash
# canonical artefact stays in source location
data/results/figures/fig1_cohort_overview.pdf       # ← real file

# writer-side reference is a symlink
.scitex/writer/01_manuscript/contents/figures/caption_and_media/fig1_cohort_overview.pdf
  └─→ ../../../../../../data/results/figures/fig1_cohort_overview.pdf
```

### Why symlink (not copy)

- **Canonical artefact stays in source location.** The figure file
  with full DAG provenance lives where `stx.io.save` put it. The
  writer side just *references* it. Copying creates two-files-of-truth
  and breaks the canonical-source rule.
- **DAG provenance preserved.** A reviewer who follows the symlink
  reaches the rendered figure → its source script (`scripts/for_paper/
  plot_fig1_*.py`) → its data inputs (`data/source/...`), all via
  scitex-clew's DAG. A copied file has no such chain.
- **Single-edit re-render.** When a figure is re-rendered (parameter
  tweak, dataset update), the canonical file changes in
  `data/results/figures/`; the symlink picks up the new version
  automatically. No second sync step.

### Where the figure scripts live

Figure-generation scripts (the FigRecipe `compose` calls that
assemble panels into multi-panel composites) live in
`<proj-root>/scripts/for_paper/`. One script per figure (or per
panel + composite). See
[40_paper-writing-protocol.md](40_paper-writing-protocol.md)
§"Manuscript-scripts layout" for the convention.

### Forbidden

- Copying a figure file directly into `.scitex/writer/` (creates
  two-files-of-truth, breaks DAG provenance).
- Editing a figure inside `.scitex/writer/` (the writer side is a
  reference; the canonical artefact is at the source location).
- Putting figure-generation scripts anywhere other than
  `scripts/for_paper/` (breaks the manuscript-scripts-layout
  convention; see 40_protocol).
