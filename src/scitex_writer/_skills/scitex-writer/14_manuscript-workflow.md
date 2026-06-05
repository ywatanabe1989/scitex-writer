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

## Per-figure symlink chain (canonical → ./data → .scitex/writer → PDF)

Figure outputs follow a **canonical symlink chain** with the
`@stx.session` output directory as the source of truth and every
downstream location as a symlink — never a copy. The full chain:

```
session out / run dir (source of truth)
  └─ symlink ─→ ./data/...
       └─ symlink ─→ .scitex/writer/.../caption_and_media/...
            └─ symlink ─→ PDF (LaTeX \includegraphics resolves through it)
```

Concretely:

1. **Session out/run dir** — every figure script (run under
   `@stx.session.start(...)`) saves its figure via
   `stx.io.save(fig, eval(CONFIG.PATH.FIG_X))`. The file lands in
   the session's resolved output directory, e.g.
   `<proj-root>/.scitex/io/runs/<timestamp>/<script>/fig1_cohort.pdf`.
   This is the **canonical artefact** with full DAG provenance.
2. **`./data` symlink** — the canonical artefact is symlinked into
   `<proj-root>/data/results/figures/` (the project-tree location
   the rest of the project refers to). `stx.io.save`'s
   `symlink_to=eval(CONFIG.PATH.X)` mechanism creates this symlink
   automatically when configured. The `./data` location is the
   project-level handle.
3. **`.scitex/writer` symlink** — the `./data` location is symlinked
   in turn into the writer-side
   `<proj-root>/.scitex/writer/01_manuscript/contents/figures/caption_and_media/...`
   so the LaTeX build can resolve it as a manuscript figure file.
   Equivalently reachable via `<proj-root>/paper/...` through the
   `paper -> .scitex/writer` symlink at the project root.
4. **PDF inclusion via symlink** — the manuscript LaTeX loads each
   figure via `\includegraphics{...}` whose path resolves through
   the symlink chain. The PDF rendering reads from the symlinked
   location; **the PDF build never copies the figure file**. The
   same source-of-truth file feeds every downstream consumer.

```bash
# (1) canonical artefact stays in session out / run dir
.scitex/io/runs/2026-06-05T18:42:00/plot_fig1_cohort.py/fig1_cohort_overview.pdf

# (2) symlinked into ./data
data/results/figures/fig1_cohort_overview.pdf
  └─→ ../../../.scitex/io/runs/2026-06-05T18:42:00/plot_fig1_cohort.py/fig1_cohort_overview.pdf

# (3) symlinked into .scitex/writer (LaTeX-visible location)
.scitex/writer/01_manuscript/contents/figures/caption_and_media/fig1_cohort_overview.pdf
  └─→ ../../../../../../data/results/figures/fig1_cohort_overview.pdf

# (4) LaTeX \includegraphics resolves through the chain; no copy at build time
```

### Why symlink at every step of the chain (not copy)

- **Single source of truth.** The figure file with full DAG provenance
  lives where `stx.io.save` put it (the session out/run dir). Every
  downstream location is just a *reference*. Copying anywhere in the
  chain creates two-files-of-truth and breaks the canonical-source
  rule.
- **DAG provenance preserved.** A reviewer who follows the symlink
  chain reaches the rendered figure → its source script
  (`scripts/for_paper/plot_fig1_*.py`) → its session out/run dir →
  its data inputs (`data/source/...`), all via scitex-clew's DAG.
  A copied file anywhere in the chain has no such backward chain.
- **Single-edit re-render.** When a figure is re-rendered (parameter
  tweak, dataset update), the canonical file changes in the session
  out/run dir; the chain of symlinks picks up the new version
  automatically. The PDF builds from the new content without any
  sync step.
- **PDF stays canonical too.** The LaTeX `\includegraphics{}`
  resolves through the symlink chain at build time. The PDF doesn't
  embed a stale copy; the figure inside the PDF IS the figure at the
  source-of-truth location. Re-running the LaTeX build after a
  figure re-render produces a PDF with the new figure, no copy step
  needed.

### Where the figure scripts live (primary vs fallback)

**Primary rule.** A figure (or panel) is generated as **close as
possible to the analysis script that produces its data**. The figure
script lives **next to its analysis script**, at the related location
inside `./scripts/` where the analysis runs — typically the analysis
script itself owns its panel as a side-output via `stx.io.save(fig,
...)`. The session out/run dir is the source of truth at this layer.

**Fallback.** `<proj-root>/scripts/for_paper/` is an **aggregation
compromise**, NOT the primary figure home. It exists to:

1. **Compose** the per-panel artefacts that the analysis scripts
   produced into multi-panel manuscript figures (FigRecipe `compose`).
2. **Centralise** the figure-list-to-script mapping for the manuscript
   build, so the LaTeX side has a single discoverable location.
3. **Plot NEW only when necessary** — when a paper-specific
   aggregation or transformation is genuinely missing from the
   analysis pipeline and cannot reasonably move there.

Default to the primary rule. Use `scripts/for_paper/` for composition
+ centralisation; resort to plotting-NEW there only when the primary
location can't reasonably host it. See
[40_paper-writing-protocol.md](40_paper-writing-protocol.md)
§"Manuscript-scripts layout" for the full primary-vs-fallback
discussion.

### Forbidden

- Copying a figure file at any step of the symlink chain (session
  out/run dir → `./data` → `.scitex/writer` → PDF). Creates
  two-files-of-truth and breaks DAG provenance at the layer where
  the copy happens.
- Editing a figure inside `./data/results/figures/` or inside
  `.scitex/writer/` (both are references; the canonical artefact is
  in the session out/run dir).
- Embedding a copy of the figure into the PDF at build time —
  `\includegraphics{}` resolves through the symlink chain; do not
  pre-render or pre-copy figures into a "submission_figures/"
  directory.
- Putting figure-generation scripts anywhere other than
  `scripts/for_paper/` (breaks the manuscript-scripts-layout
  convention; see 40_protocol).
