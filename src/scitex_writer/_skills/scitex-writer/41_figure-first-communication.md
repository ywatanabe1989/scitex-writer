---
description: |
  [TOPIC] Figure-first communication protocol — agent ↔ user agreement loop for the paper's figure list and per-figure panel breakdown.
  [DETAILS] The load-bearing protocol the operator gave as the seed for scitex-writer's paper-writing flow: agree on the LIST of figures (`Fig 1` / `Fig 2` / ... / `Fig N`) with the user; then for each agreed figure, agree on the PANEL breakdown (`a.` / `b.` / `c.` ...) with a one-sentence intent per panel; THEN write plot code; THEN write prose. Reverse the order and the paper rewrites itself three times. Pairs with `scitex-dev/scientific/01_figures_02_logic-and-ordering.md` (the WHY — the universal logic / dependency-graph rules that determine which figure CAN be `Fig N`); this leaf is the HOW (the agent-user agreement protocol the operator uses in his own collaboration style). V0 SKELETON awaiting operator iteration — the step structure + scaffold are in; the operator's exact phrasing, decision rules, and worked-example detail are seeded and meant to be refined.
tags: [scitex-writer-figure-first-communication]
---

<!--
v0 skeleton status:
  - Protocol structure (steps 1-4 + naming convention) captured from
    operator's seed messages (msg 9220, 9221, 9226, 9227).
  - The figure-list / panel-list agreement format below is the
    operator's own; the surrounding rationale and pitfalls are scaffold
    for operator co-design.
  - Pair with `~/.claude/skills/scitex/scientific/01_figures_02_logic-and-ordering.md`
    (the WHY — universal scientific-reasoning rules that determine
    what figure CAN be `Fig N`). This leaf is the agent ↔ user
    agreement HOW.
  - Awaiting operator iteration on:
      - the worked-example phrasing (NeuroVista cohort overview is the
        operator's; keep his rationale intact)
      - the exact step-1 / step-2 phrasing the operator uses with users
      - any additional pitfalls / "how-do-I-handle-X" exceptions
-->

# Figure-first communication protocol

The agent ↔ user agreement loop for the paper's figure list and per-figure
panel breakdown. **Before writing any prose; before generating any plot
code; before drafting any results paragraph** — agree on the figure list,
then agree on each figure's panel breakdown.

This is the load-bearing pattern for scitex-writer's paper-writing flow.
Reverse the order and the paper rewrites itself three times.

## The rule

> **Agree on the list of figures, then agree on each figure's panel
> breakdown, BEFORE writing any prose or any plot code.** Prose
> follows panels follows figures.

## The protocol — the six-step pattern

The operator's live collaboration on this protocol (the canonical
worked example, see [Worked example](#worked-example-operator-live-transcript))
demonstrates six structural steps:

1. **Overall figure plan.** Agent proposes the high-level shape: how
   many main-text figures, how many supplementary, how many tables,
   what the primary axis / structural decision (ADR) is. Lets the
   user agree on COUNT before drilling in.
2. **Per-figure heading + panels.** Agent expands each figure as
   `## Fig N. <title>` + lowercase `a./b./c.` panels (one
   panel-intent sentence each).
3. **Agent offers a choice with a recommendation.** For each figure,
   the agent explicitly offers the user three options and recommends
   one:
   - **(a) OK — move to next figure.**
   - **(b) panel add / remove** (with the specific delta).
   - **(c) alternative** structure for this figure (with the
     alternative laid out).
   The recommendation is not "what do you think?" but "I recommend
   (a) because …" or "I recommend (c) because …". The user accepts,
   modifies, or rejects.
4. **Operator injects logic rules → dependency-graph re-derivation.**
   The user adds constraints (e.g. "we need to define X before Y").
   The agent then BUILDS AN EXPLICIT DEPENDENCY GRAPH (e.g. *"raw
   iEEG / event def → gPAC → ictal-anchored pool → α/β/γ taxonomy →
   prediction → alarm bounds"*) and re-derives which figure CAN be
   `Fig N` (definitions-only first; no forward references). This is
   where
   [`scientific/01_figures_02_logic-and-ordering.md`](../../scientific/01_figures_02_logic-and-ordering.md)
   principle #4 (no-undefined-before-use) lands operationally.
5. **Iterate ONE figure to convergence BEFORE moving to the next.**
   Do not parallelise. Fig 1 must be agreed end-to-end (heading +
   panels + dependency-graph-checked) before Fig 2 is proposed. This
   prevents the figure list from churning under partial agreement.
6. **Fix the representative subject across panels.** Pick one (e.g.
   `Pat10`) at the start; use it for every representative-subject
   panel across every figure unless a stated scientific reason
   switches it for one specific panel. See
   [`scientific/01_figures_02_logic-and-ordering.md` §5](../../scientific/01_figures_02_logic-and-ordering.md)
   and §7 (the choice lives in `config/REPRESENTATIVE.yaml`, not in
   plot scripts).

## The protocol — step-by-step detail

### Step 1 — figure-list agreement

The agent proposes a numbered figure list, one line per figure, with a
working title. One markdown heading per figure:

```
## Fig 1. <working title>
## Fig 2. <working title>
## Fig 3. <working title>
...
## Fig N. <working title>
```

The user reads, adds, removes, renumbers. Iterate until the list
stabilises.

**Do not move to step 2 until the user confirms the list.**

The figure list IS the table of contents of the paper's evidence — and,
by [results-order = figure-order](#dependency-on-the-logic-leaf), the
table of contents of the results section. The figure-list agreement is
the manuscript's outermost structural commitment.

### Step 2 — panel-list agreement

For each agreed figure, the agent expands into panels, one line per
panel, each with a one-sentence intent. Lowercase panel letters
matching the published-figure convention:

```
## Fig 1. <title>
a. <what comparison / what axes / what message>
b. <what comparison / what axes / what message>
c. <what comparison / what axes / what message>

## Fig 2. <title>
a. <what comparison / what axes / what message>
b. <what comparison / what axes / what message>
```

The user reads, edits, splits, merges. Iterate until each figure's
panel list stabilises.

**Do not move to step 3 until the user confirms each figure's panel
list.**

The panel-list step is where the universal
[figure-logic rules](#dependency-on-the-logic-leaf) bite: a panel
that uses a term `X` before `X` has been defined upstream is an
ordering violation. The agreement step is where the agent catches and
flags those violations before plot code is written.

### Step 3 — plot generation (per panel)

Only NOW does plot code get written. Each agreed panel maps to a
FigRecipe call (or equivalent publication-quality primitive). Because
steps 1+2 fixed the structure, step 3 is mechanical — no scope creep,
no figure rewrites mid-paper.

For per-panel rendering:

- Choose colour from the **paper-wide color scheme** decided at
  paper-start (see
  [`scientific/01_figures_02_logic-and-ordering.md` §6](../../scientific/01_figures_02_logic-and-ordering.md)).
- If the panel needs a representative subject (single-subject example),
  use the **fixed representative subject** decided at paper-start
  (same subject across `Fig 1.a`, `Fig 2.a`, `Fig 3.a` unless a
  stated scientific reason switches it; see
  [`scientific/01_figures_02_logic-and-ordering.md` §5](../../scientific/01_figures_02_logic-and-ordering.md)).
- Save via `stx.io.save(fig, ...)` so the figure enters the DAG as
  data — never `matplotlib.pyplot.savefig` (provenance dropped).
- For rendering rules per individual panel (color scale, aligned
  axes, ticks, ranges, no `jet`), see
  [`scientific/01_figures_01_standards.md`](../../scientific/01_figures_01_standards.md).
- File layout (where in `01_manuscript/contents/figures/`) follows
  [12_figures-and-tables.md](12_figures-and-tables.md)'s
  `caption_and_media/` + `compiled/` + `legacy/` convention.

### Step 4 — prose follows

Results-section prose is drafted with the agreed figures as fixed
anchors. Each manuscript claim sentence references `Fig N.x`, and the
underlying registered claim ID that backs the number in the sentence:

```
"In the seizure condition, the α-band power was elevated relative to
interictal (Fig 1.b; \vclaim{cohort_alpha_sz_vs_ic_p})."
```

This composes with [13_claims.md](13_claims.md) and
[26_writing-during-exploration.md](26_writing-during-exploration.md) —
every reported number is either a resolved `\vclaim{}` or a
`\placeholder{}` awaiting one. (The figure-list agreement loop in step 1
is the outer scaffold; the claim-registration discipline is the inner
scaffold.)

## Naming convention

Use the exact shape `## Fig N. <title>` for figures and lowercase
`a.` `b.` `c.` for panels (lowercase matches the published-figure
convention common in biology and neuroscience journals). The agent's
agreement artefact (the markdown list) is meant to copy-paste into:

- FigRecipe filenames (`fig1_a_cohort_n.png` / `fig1_b_alpha_labels.png`).
- Manuscript LaTeX (`\begin{figure}\caption{...}\label{fig:1}`).
- The supplementary index (`Fig S1` / `Tab S1` parallel).

Keeping a single canonical shape across the agreement, the rendered
files, the LaTeX source, and the SI index removes one translation
step.

## Worked example (operator live transcript)

The canonical worked example for this protocol is the operator's
**live collaboration with `proj-neurovista`** — a real
figure-design session where each of the six steps above is visible
in the transcript: the overall plan (compress N→fewer main + SI,
table count, primary axis / ADR), the per-figure `## Fig N.` +
`a./b./c.` breakdown, the agent's (a)/(b)/(c)-with-recommendation
choice offering, the operator's dependency-graph re-derivation, the
one-figure-to-convergence pacing, and the Pat10 representative-subject
fix.

> **Transcript insertion point** — the live transcript is preserved
> on the operator's side and will be folded in verbatim during his
> iteration pass. Keep this paragraph as the load-bearing pointer to
> where the canonical worked example lives.

### Companion mini-example (the NeuroVista cohort overview)

A small illustration of how steps 1+2 land for a real `Fig 1`:

```
## Fig 1. NeuroVista cohort overview
a. 9 patients: n_sz / n_ic / n_months (post-day-100)
b. α/β/γ pattern-classification labels
c. 16ch grid + Karoly-9 extraction rationale
```

Operator's rationale: you cannot make THIS `Fig 1` unless `n_sz` /
`n_ic` / `IC` and the `α` / `β` / `γ` pathological-channel definitions
are already established. The figure's definitional dependency graph
determines what CAN be `Fig 1`. In this case, `Fig 1` is the
definitional introducer — panel `a.` defines `n_sz` / `n_ic` /
`n_months`, panel `b.` introduces the `α` / `β` / `γ` labelling,
panel `c.` introduces the channel grid and the Karoly-9 extraction.
That is *why* this is `Fig 1`: because if it isn't, every later
figure would reference undefined terms.

Keep his rationale intact when iterating; replace the cohort-specific
numbers if the paper changes, but preserve the
dependency-as-definitional-introducer argument.

## Dependency on the logic leaf

This protocol is the agent ↔ user agreement HOW. The universal WHY —
data progression, representative-before-grouped, results-order =
figure-order, no-undefined-before-use (dependency graph), one fixed
representative subject across panels, consistent color scheme — lives
in
[`~/.claude/skills/scitex/scientific/01_figures_02_logic-and-ordering.md`](../../scientific/01_figures_02_logic-and-ordering.md)
(tool-agnostic). Load both; the agreement protocol is empty if the
agent doesn't know what the constraints are.

## Why this order is load-bearing

If prose is written before panels are agreed, every figure revision
forces a prose rewrite. Conversely, if panels are agreed first, prose
revisions never touch the figures — and the figure code, once written,
is final-for-publication.

The protocol also surfaces **missing figures**: agreeing on the figure
list before drafting forces the agent and user to explicitly ask
"does this manuscript claim need a figure?" — and to add it before
prose locks the structure.

The protocol also surfaces **silent omissions**: if a planned figure
disappears from a later version of the figure list without explicit
discussion, the diff catches it. Composes with the honest-grounding
norm in
[`~/.claude/skills/scitex/scientific/06_scitexification/00_playbook.md`](../../scientific/06_scitexification/00_playbook.md)
— the figure-list-agreement diff is the surface that makes
silent-attrition detectable at the figure layer.

## Pitfalls (v0 — operator iteration to refine)

- **User wants the figure but the term hasn't been defined.** Push
  back: define the term first (in prose or in an earlier figure),
  THEN add the figure. The logic leaf calls this
  *no-undefined-before-use*.
- **Two figures fight for `Fig 1`.** Resolve by the dependency graph:
  whichever figure introduces the most terms used downstream is the
  more natural `Fig 1`.
- **The figure list keeps churning past iteration 5.** Surface the
  loop count to the user ("we've revised the figure list 5 times —
  what's the disagreement?"). Capture the unresolved point as an
  explicit open question; do NOT silently bail to "I'll just draft
  something" — that's the silent-attrition antipattern at the
  flow-layer.
- **Operator-iteration placeholder** — refine the figure-first
  protocol's exact agent prompts, decision rules, and additional
  pitfalls here.

## Forbidden

- Writing results-section prose before the figure list is agreed.
- Generating plot code before per-figure panel agreement.
- Switching the representative subject between panels without an
  explicit stated reason (cherry-picking impression).
- Using different colours for the same group across figures
  (treatment-is-blue-in-Fig-1-orange-in-Fig-3 is forbidden — see
  [`scientific/01_figures_02_logic-and-ordering.md` §6](../../scientific/01_figures_02_logic-and-ordering.md)).
- Calling `matplotlib.pyplot.savefig` for a paper figure — figures
  enter the manuscript via `stx.io.save(fig, ...)` so provenance is
  preserved.

## Related

- [40_paper-writing-protocol.md](40_paper-writing-protocol.md) — the
  umbrella protocol; the figure-first loop is its load-bearing first
  step.
- [12_figures-and-tables.md](12_figures-and-tables.md) — figure-file
  lifecycle (`caption_and_media/`, `compiled/`, `legacy/`).
- [22_writing-figures-stats.md](22_writing-figures-stats.md) —
  figure rendering rules + stats reporting.
- [13_claims.md](13_claims.md) — `\vclaim{}` registration; the
  step-4 prose-anchor mechanism.
- [26_writing-during-exploration.md](26_writing-during-exploration.md)
  — in-flight discipline; the figure-list agreement is the outer
  scaffold around the `\vclaim{}` / `\placeholder{}` / `\hlref{}`
  inner discipline.
- `~/.claude/skills/scitex/scientific/01_figures_02_logic-and-ordering.md`
  — universal figure-logic rules (the WHY). Load alongside this leaf.
- `~/.claude/skills/scitex/scientific/01_figures_01_standards.md` —
  per-figure rendering standards (color scale, aligned axes, layout).
- `~/.claude/skills/scitex/scientific/06_scitexification/00_playbook.md`
  — universal honest-grounding norm; the figure-list integrity rule
  is the figure-layer specialisation.
