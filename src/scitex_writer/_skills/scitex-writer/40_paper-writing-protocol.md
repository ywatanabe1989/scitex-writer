---
description: |
  [TOPIC] Paper-writing umbrella protocol — agent ↔ user collaborative flow for turning a (typically scitexified) analysis into a manuscript.
  [DETAILS] The top-level scaffold that composes the existing scitex-writer skill set into a single agent-driven flow: figure-first communication (`41_*`) → results-section drafting (anchored to the agreed figure list) → methods (reproducibility) → introduction (gap → hypothesis spine) → abstract (last, distilled from the rest) → discussion (fulfils the introduction's promise). Reuses the existing per-section templates verbatim — `30_writing-abstract`, `31_writing-introduction`, `32_writing-methods`, `33_writing-discussion`, `36_writing-results` (v0 skeleton; operator iteration to refine) — and the in-flight discipline in `26_writing-during-exploration` (`\vclaim{}`, `\placeholder{}`, `\hlref{XXX}`, pre-submission grep gate). Bakes in the operator's framing: paper-writing is CONCURRENT with experiments, not sequential after them. V0 SKELETON awaiting operator iteration on the inter-section flow specifics.
tags: [scitex-writer-paper-writing-protocol]
requires:
  - figrecipe
  - scitex-io
  - scitex-clew
  - scitex-stats
---

<!--
v0 skeleton status:
  - Protocol structure captured from operator messages (9215 / "write the
    paper WHILE running experiments"; 9220 / 9221 figure-logic seeds;
    9226 / 9227 representative + color seeds; 9216 symlink convention).
  - The per-section flow scaffolds delegate to the existing detailed
    section templates (30-33, 36) rather than restating them.
  - Pair with `41_figure-first-communication.md` (the load-bearing first
    step) and the universal figure-logic leaf in scitex-dev
    (`scientific/01_figures_02_logic-and-ordering.md`).
  - Awaiting operator iteration on inter-section ordering, decision
    rules for when to switch from one section to another, and the
    concurrent-with-experiments framing detail.
-->

# Paper-writing protocol (umbrella)

The top-level agent ↔ user collaborative protocol for turning an
analysis into a manuscript. Composes the existing scitex-writer skill
set (figure handling, claim registration, in-flight discipline,
per-section templates) into a single driven flow.

## Operator framing — paper-writing is CONCURRENT with experiments

This protocol assumes you draft the paper **while** experiments are
still running, not after. The in-flight discipline in
[26_writing-during-exploration.md](26_writing-during-exploration.md)
is the substrate: `\vclaim{}` fills as runs land, `\placeholder{}`
marks WIP prose, `\hlref{XXX}` marks missing citations, the
pre-submission grep gate is the final readiness check.

The protocol below assumes scitex-writer is the tool and the analysis
has been (or is being) scitexified — claims are registered, figures
are saved via `stx.io.save`, the project layout follows the
`<proj-root>/paper -> .scitex/writer` convention (see
[14_manuscript-workflow.md](14_manuscript-workflow.md) §"Project layout
convention").

## When to load

Load when **any** of the following is true:

- You and the user are starting a paper from existing results (a
  scitexified project, an analysis notebook, a small repo of scripts
  + data).
- You are mid-paper and need to switch sections; this leaf gives the
  hand-off rules.
- You are about to compile the manuscript for an internal draft
  review and want the cross-section checklist.

Do NOT load this skill when you are:

- Translating an analysis into SciTeX form — that's
  [`scientific/06_scitexification/`](../../scientific/06_scitexification/).
- Designing one specific figure without the broader paper flow —
  load [41_figure-first-communication.md](41_figure-first-communication.md)
  alone.
- Auditing or building a SciTeX package — that's the general/
  layer.

## The flow (cross-section ordering)

The protocol prescribes a section-traversal order that minimises
rewrites. The recommended order is NOT the order the reader sees in
the published paper.

| Order | Section | Why this order |
|---|---|---|
| 1 | **Figures** (figure-first agreement; figure list + per-figure panels) | Lock the paper's evidence structure first. Drives the results-section paragraph order (see `scientific/01_figures_02_logic-and-ordering.md` §3). |
| 2 | **Results** | Composes from the agreed figure list. Each `Fig N` gets a paragraph; each paragraph references `\vclaim{}` IDs for its numbers. |
| 3 | **Methods** | Reproducibility doc for what the results came from. Cites `@stx.session` entry points + CONFIG keys. |
| 4 | **Introduction** | Gap → hypothesis spine. Now that the results are known, the intro can promise *exactly* what the discussion will fulfil. |
| 5 | **Abstract** | Distilled from results + introduction. Numbers are the agreed-on `\vclaim{}` IDs from step 2. |
| 6 | **Discussion** | "Fulfils the promise made in introduction" (per [33_writing-discussion.md](33_writing-discussion.md)). |
| 7 | **Tables** | Often parallel to figures; table-list agreement (operator second-wave; deferred). |
| 8 | **Supplementary** | In-vs-out decision; SI methods overflow (operator second-wave; deferred). |

This order is a default — for some papers (highly methods-driven,
revisions of a prior submission, etc.) the order shifts. The protocol
states the default and surfaces the trade-offs.

## Step-by-step

### 1. Figures — figure-first agreement loop

See [41_figure-first-communication.md](41_figure-first-communication.md)
for the full agreement protocol. Output artefact: the agreed figure
list (`Fig 1`–`Fig N`) and each figure's panel breakdown
(`a./b./c.`).

This step also fixes:
- The **paper-wide colour scheme** (group → colour). Document in
  `config/COLORS.yaml` or equivalent. (See
  [`scientific/01_figures_02_logic-and-ordering.md` §6](../../scientific/01_figures_02_logic-and-ordering.md).)
- The **fixed representative subject** for representative-subject
  panels (same subject across all such panels unless stated reason
  switches). (See
  [`scientific/01_figures_02_logic-and-ordering.md` §5](../../scientific/01_figures_02_logic-and-ordering.md).)

### 2. Results — per-figure paragraph drafting

Hand off to [36_writing-results.md](36_writing-results.md) for the
per-section flow. Each agreed `Fig N` gets a paragraph; each
paragraph's claim sentence references a `\vclaim{}` ID.

Concurrent-with-experiments framing: numbers that haven't landed yet
use `\placeholder{}` until the run finishes and the `\vclaim{}` is
registered.

### 3. Methods — reproducibility-focused

Hand off to [32_writing-methods.md](32_writing-methods.md) for the
section template (AP10/AP11 anti-patterns; methodology over
motivation). Methods cites the scitexified analysis's
`@stx.session` entry points and CONFIG keys directly; for the
discipline, see
[`scientific/06_scitexification/00_playbook.md`](../../scientific/06_scitexification/00_playbook.md).

### 4. Introduction — gap → hypothesis spine

Hand off to [31_writing-introduction.md](31_writing-introduction.md)
for the 8-section template. Hypotheses inherited from
[`scientific/00_planning_01_hypotheses-agreement.md`](../../scientific/00_planning_01_hypotheses-agreement.md)
— the introduction sets them up; the discussion closes them out.

### 5. Abstract — distilled last

Hand off to [30_writing-abstract.md](30_writing-abstract.md) for the
7-section template. Drafted LAST because the abstract's claim
sentences quote results-section `\vclaim{}` IDs verbatim — those have
to exist first.

### 6. Discussion — fulfils the introduction's promise

Hand off to [33_writing-discussion.md](33_writing-discussion.md) for
the 5-section template. The (A) conclusion → (B) results → (C)
literature flow rule from that template is canonical.

### 7. Tables — table-first agreement loop (operator second-wave)

Deferred. To-be-landed as `42_table-first-communication.md` — the
parallel to figure-first, with table-list agreement → per-table column
agreement → table generation → results-section table call-out.

### 8. Supplementary — in-vs-out decision (operator second-wave)

Deferred. To-be-landed as `43_supplementary-materials-flow.md` — the
in-vs-out rule (main-paper iff referenced in abstract / introduction /
discussion), SI index conventions (`Fig S1` / `Tab S1` parallel),
methods overflow.

## scitex.stats mandate (cross-section)

All statistical tests in a paper-writing flow MUST use
**`scitex.stats`**, not raw `scipy.stats` / `statsmodels` ad-hoc.
This parallels the FigRecipe mandate above and makes the
`requires: [scitex-stats]` declaration on this leaf load-bearing.

`scitex.stats` provides **PRESETS** that emit the full statistical
anchor (n / dof / effect size / p / stars / test name / H0) in the
canonical reporting form. Raw `scipy.stats.ttest_ind(...)` returns
just a statistic and a p-value; the author must then assemble the
anchor by hand and is likely to miss a field. Presets close that
gap by construction — the in-line `\vclaim{}` reference in the
results prose then resolves to a numerically complete anchor.

See [22_writing-figures-stats.md § "scitex.stats mandate"](22_writing-figures-stats.md)
for the per-preset pointer and the worked DO / DO NOT comparison
of preset use vs raw scipy.

### Detail-location for stats (extension of the detail-location rule)

The detail-location rule above gives results-prose / figure-caption
/ methods as the three depth levels. For statistical anchors
specifically, **a fourth location** exists for overflow: the
**footnote**.

| Location | Stats content |
|---|---|
| **Results prose** | brief — test name + p-value + stars (`paired t-test, p < 0.001, ***`). |
| **Figure caption** | figure-specific minimum — n + key effect. |
| **Methods section** | full procedure + test choice + justification. |
| **Footnote** | overflow when a single value or expression would otherwise span >1.5 lines or interrupt the prose flow (multi-clause CI, multi-group anchor). |

The footnote keeps the prose readable AND lets the value stay on
the same page for a reviewer who wants to verify. See
[22_writing-figures-stats.md § "Long-value footnote rule"](22_writing-figures-stats.md)
for the worked example + threshold guidance.

## Manuscript-scripts layout (cross-section)

Scripts that **generate figures, tables, or claims for the paper**
live under a dedicated directory in the scitexified analysis:

```
<proj-root>/
├── scripts/
│   ├── 01_extract.py          # general analysis scripts
│   ├── 02_features.py
│   ├── ...
│   └── for_paper/             # MANUSCRIPT-specific scripts only
│       ├── plot_fig1_cohort.py
│       ├── plot_fig2_features.py
│       ├── plot_fig3_classifier.py
│       ├── ...
│       └── render_table1.py
├── data/results/              # outputs land here, picked up via stx.io.save
├── config/
│   ├── COLORS.yaml            # paper-wide colour scheme (§7 above)
│   └── REPRESENTATIVE.yaml    # fixed representative subject (§7 above)
└── .scitex/writer/            # writer-side artefacts; symlinked from
                               # paper/ at <proj-root>/paper -> .scitex/writer
```

### Primary rule — figures AND tables live next to their analysis script

A figure (or panel) AND a table (as CSV) is generated as CLOSE as
possible to the analysis script that produces its data. The analysis
script owns its artefact as a side-output via `stx.io.save(fig, ...)`
(figures) or `stx.io.save(df, ...)` (tables, saved as CSV); the
session out/run dir is the source of truth, and the artefact enters
the canonical symlink chain from there (see
[14 § Per-artefact symlink chain](14_manuscript-workflow.md)). This
is the default — do NOT centralise figure or table generation away
from the analysis.

### Fallback — `./scripts/for_paper/` is the aggregation COMPROMISE

`./scripts/for_paper/` is NOT the primary figure home. Two scoped
reasons for it: **composition** (pull existing panels from `./data`
and assemble multi-panel composites via `figrecipe.compose` —
load via `stx.io.load(eval(CONFIG.PATH.FIG_X))`, never re-plot),
and **centralisation** (single discoverable directory for the
figure-list-to-script mapping at LaTeX build time). A plot-centric
`scripts/for_paper/` would carry two-versions-drift between
analysis and manuscript; compose-centric guarantees one version per
panel and the symlink chain propagates re-renders automatically.
Plotting NEW in `scripts/for_paper/` is a last resort — only when
a paper-specific aggregation genuinely cannot move to the analysis
pipeline. Output still flows through the canonical chain.

Why a dedicated directory:

- **Discoverability.** A reviewer or co-author looking for "the
  script that produced `Fig 3`" finds it under
  `scripts/for_paper/plot_fig3_*` without searching the whole
  analysis tree.
- **Lifecycle separation.** Analysis scripts may evolve through
  the project lifetime; manuscript scripts crystallise at submission.
  Keeping them in a dedicated dir makes the "freeze for submission"
  step clean (snapshot `scripts/for_paper/` + outputs + config).
- **Reproducibility audit.** The pre-submission checklist (item 4
  below) can scope its figure-script audit to
  `scripts/for_paper/`.

This pairs with [14_manuscript-workflow.md](14_manuscript-workflow.md)
§"Project layout convention" — the `<proj-root>/paper ->
.scitex/writer` symlink plus the `scripts/for_paper/` directory are
the two project-layout conventions for a scitexified manuscript.

## Pre-submission checklist (cross-section)

Before any submission:

1. **Figure-list integrity.** Diff the current figure list against
   the step-1 agreed list. Any silent drops? Either reinstate or
   document the removal explicitly (see honest-grounding below).
2. **Color-scheme consistency.** Every group/condition uses the same
   colour in every figure it appears in. Check
   [`scientific/01_figures_02_logic-and-ordering.md` §6](../../scientific/01_figures_02_logic-and-ordering.md).
3. **Representative-subject consistency.** Every representative-subject
   panel uses the same subject (unless a stated reason switches).
4. **Results-order = figure-order.** Read the results section
   top-to-bottom; the figures referenced should be sequential.
5. **Hypothesis ↔ discussion mapping.** Every hypothesis from
   `HYPOTHESES.md` is addressed in the discussion (supported /
   refuted / inconclusive).
6. **`\vclaim{}` resolution.** Every `\vclaim{}` in the manuscript
   resolves; no `[claim:<id>]` survivors. (Pre-submission grep gate
   from [26_writing-during-exploration.md](26_writing-during-exploration.md).)
7. **`\placeholder{}` cleared.** Zero `\placeholder{}` / `\ph{}` in
   the source (or only inside literal example blocks).
8. **`\hlref{}` resolved.** Zero unresolved citation placeholders.
9. **v0 / honor-system / pilot disclosure.** Any v0 numbers carry
   their transparency paragraph (see
   [26_writing-during-exploration.md](26_writing-during-exploration.md)).

## Figure vs table — when to use which (cross-section)

A paper-writing decision rule that applies BEFORE the figure-first
agreement protocol kicks in: if the data should be a **table**, the
figure-first loop doesn't engage at all (the table-first loop does
— see the deferred `42_table-first-communication.md`).

### The rule

| Use a **table** when | Use a **figure** when |
|---|---|
| The data is **exact numerics** that the reader is meant to look up. | The data shows a **trend** (monotonic, exponential, saturating, ...). |
| There are **many discrete values** (group means × many groups, parameter sweep cells). | There is a **relationship** between two or more continuous variables that's most readable as a shape (a scatter, a line). |
| The values are **the point** — sample sizes, demographic summaries, hyperparameter values, statistical-test results that the reviewer must verify. | The values are **in service of a comparison** — same-axis pre/post, condition A vs condition B, where the reader cares about ordering / magnitude / overlap, not the digit-by-digit numbers. |
| Comparing requires the reader to read individual cell values. | Comparing requires the reader to see structure. |

Equivalently: **table = exact numerics / many values; figure =
trends, relationships, comparisons.**

### Why this decision goes here (cross-section)

It precedes the figure-first agreement loop (`41_*`) because the loop
only applies once you've decided the artefact is a figure. The same
data can be EITHER a table OR a figure depending on what the paper
wants the reader to do with it — the decision is at the paper-writing
layer, not the rendering layer.

For data the reader is meant to **look up**, fight the urge to
"figure-ify" it (e.g. a 12-row demographic summary as a bar chart
where the reader has to read off heights). Keep it as a table.

For data the reader is meant to **see**, fight the urge to
"tabulate" it (e.g. a parameter sweep across 50 conditions as a
giant table the reader can't scan). Render the trend.

### Borderline cases

- **Small comparison with three numbers** ("treatment 0.85, control
  0.72, baseline 0.51"): table if those are the result the paper
  rests on, figure-with-error-bars if the comparison is what the
  paper rests on.
- **Statistical-test outputs** (test name, t-value, df, p-value):
  always table. Figures show the effect; tables document the test.
- **Confusion matrices**: table when the cell values matter
  individually; figure (heatmap) when overall pattern matters more
  than individual values. A 10×10 confusion matrix is almost always
  a heatmap.

### Integration with the rest of the protocol

- If the artefact is a **figure**: enter the figure-first agreement
  loop ([41_figure-first-communication.md](41_figure-first-communication.md)).
- If the artefact is a **table**: enter the table-first agreement
  loop (`42_table-first-communication.md`, deferred to a future PR).
  The same shape applies — agree on table list (`Tab 1` … `Tab M`)
  with working titles, then agree per-table on columns + row
  groupings, BEFORE the table code is written.

The Universal-layer rule about
[results-order = figure-order](../../scientific/01_figures_02_logic-and-ordering.md)
applies to figures specifically; tables are typically interleaved
with figures in the results section using parallel numbering
(`Fig 1`, `Tab 1`, `Fig 2`, `Tab 2`, ...) or grouped at the end
(per journal style).

## Detail-location rule (cross-section)

The same content appears at **different depth in different sections**.
Specifically: acquisition rules, parameters, and procedural detail
are **BRIEF in the results section and figure captions** (just enough
for the reader to interpret the figure), **FULL in the methods
section**.

| Where | What goes there |
|---|---|
| **Results section** | One-clause summary of how the number was produced ("…with FDR-corrected paired t-test, \vclaim{...}") — enough to read the figure. |
| **Figure captions** | The figure-specific minimum ("n = 9 patients, mean ± SEM") — enough to interpret the figure without page-flipping. |
| **Methods section** | The full procedure — equipment, software versions, parameters, exact statistical-test choice and justification. The reproducibility doc. |

Why: duplicating the full procedural detail across results, captions,
AND methods makes results unreadable (the figure narrative gets buried)
and makes maintenance fragile (a parameter change has to be reflected
in three places). The rule is **brief at the point of reading,
full at the point of reproduction**.

This pairs with the section-traversal order above: methods is drafted
AFTER results (step 3), so the methods author already knows what level
of detail the results section carried, and writes the methods to fill
the gap — not to duplicate.

For the rendering / figure-caption discipline that operationalises
this, see
[22_writing-figures-stats.md](22_writing-figures-stats.md) §
"Statistical Reporting" (full stats reporting form for methods) and
[32_writing-methods.md](32_writing-methods.md) (the methods template
itself).

## FigRecipe mandate (cross-section)

All paper figures MUST be authored with **FigRecipe**, not raw
`matplotlib` ad-hoc code. This is what makes the `requires:
[figrecipe]` declaration on this leaf load-bearing rather than
informational.

The mandate has three layers, each enforced at a different step:

1. **Per-panel** — every panel `a./b./c.` in the figure-first
   agreement (`41_figure-first-communication.md`) is a FigRecipe
   plot using the publication-quality primitives. Raw `matplotlib`
   in a panel script is a violation.
2. **Composite** — the multi-panel figure is assembled via
   FigRecipe's compose API (the bridge between the
   `## Fig N.` + `a./b./c.` agreement format and the rendered
   composite). External stitching (imagemagick, gridspec) is a
   violation.
3. **Provenance** — the composite is saved via `stx.io.save(fig,
   ...)` so the DAG carries it. Direct `matplotlib.pyplot.savefig`
   is a violation.

Why: FigRecipe enforces the rendering rules from
[`scientific/01_figures_01_standards.md`](../../scientific/01_figures_01_standards.md)
(shared colour scale, aligned axes, no `jet`, etc.) by
construction; the agent doesn't have to re-check them per panel.
The compose layer preserves the panel-by-panel DAG provenance
chain end-to-end.

See `41_figure-first-communication.md` steps 3.a / 3.b / 3.c for
the per-step detail.

## Config-driven figure parameters (cross-section)

Per-paper figure parameters that recur across figures — the colour
assignment, the fixed representative subject, group → label mappings —
**live in project config** (`~/proj/<project>/configs/*.yaml` or
`<proj-root>/config/*.yaml` per the scitexified-project structure),
NOT hardcoded in plot scripts. See
[`scientific/01_figures_02_logic-and-ordering.md` §7](../../scientific/01_figures_02_logic-and-ordering.md)
for the full discipline.

Practical consequence at protocol step 1: when the figure list is
agreed, also commit the per-paper config decisions (`config/COLORS.yaml`,
`config/REPRESENTATIVE.yaml`, etc.) to the project. Every figure
script reads from these; no per-script search-and-replace, no
inconsistency between `Fig 1`'s "treatment is blue" and `Fig 3`'s
"treatment is orange because orange looks nicer here."

## Honest grounding (carryover from scitexification)

Every manuscript claim ladders back to a scitex-clew-registered claim
(`\vclaim{<id>}`), whose value is either a grounded answer with
evidence or `null` + explicit reason. **Silent rephrasing of a number
without provenance is the same silent-attrition antipattern at the
manuscript layer** (see
[`scientific/06_scitexification/00_playbook.md`](../../scientific/06_scitexification/00_playbook.md)).

The figure-list integrity rule (step 1, pre-submission item 1) is the
figure-layer specialisation: silent omission of a planned figure is
forbidden — it either lives in the main paper with reduced claims, or
moves to SI with explicit text.

## Pitfalls (v0 — operator iteration to refine)

- **"Let me draft the abstract first to anchor the paper."** Don't —
  the abstract is downstream of results. Drafting it first is a
  structural commitment to numbers that haven't landed.
- **Drafting methods before figures are agreed.** Methods is downstream
  of results (it documents how results came about). Tempting to draft
  early because it's "factual", but the order is load-bearing.
- **Operator-iteration placeholder** — refine the inter-section
  hand-off rules, decision points for when to revisit step 1, and any
  additional cross-section pitfalls here.

## Forbidden

- Silent removal of a planned figure from the agreed list (see Honest
  Grounding).
- Writing the abstract before the results section has its
  `\vclaim{}` IDs settled.
- Drafting prose that uses a term before the term is defined upstream
  (see
  [`scientific/01_figures_02_logic-and-ordering.md` §4](../../scientific/01_figures_02_logic-and-ordering.md)).
- Generating plot code before per-figure panel agreement (step 1
  violation).
- Submitting with unresolved `\vclaim{}` / `\placeholder{}` /
  `\hlref{}` survivors (pre-submission grep gate, item 6-8).

## Related

- [41_figure-first-communication.md](41_figure-first-communication.md)
  — the load-bearing first step.
- [14_manuscript-workflow.md](14_manuscript-workflow.md) — CLI
  workflow + project layout convention (`<proj-root>/paper ->
  .scitex/writer` symlink).
- [26_writing-during-exploration.md](26_writing-during-exploration.md)
  — in-flight discipline (`\vclaim{}` / `\placeholder{}` /
  `\hlref{}` / pre-submission grep gate).
- [30_writing-abstract.md](30_writing-abstract.md) /
  [31_writing-introduction.md](31_writing-introduction.md) /
  [32_writing-methods.md](32_writing-methods.md) /
  [33_writing-discussion.md](33_writing-discussion.md) /
  [36_writing-results.md](36_writing-results.md) — per-section
  templates that this protocol hands off to.
- [22_writing-figures-stats.md](22_writing-figures-stats.md) —
  per-figure rendering rules + stats reporting.
- [13_claims.md](13_claims.md) — `\vclaim{}` registration mechanism.
- `~/.claude/skills/scitex/scientific/01_figures_02_logic-and-ordering.md`
  — universal figure-logic rules (the WHY for the figure-first
  protocol).
- `~/.claude/skills/scitex/scientific/06_scitexification/00_playbook.md`
  — universal honest-grounding norm.
- `~/.claude/skills/scitex/scientific/00_planning_01_hypotheses-agreement.md`
  — hypothesis-list agreement BEFORE the analysis.
