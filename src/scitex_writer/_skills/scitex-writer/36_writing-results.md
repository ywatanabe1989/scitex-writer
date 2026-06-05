---
description: |
  [TOPIC] Scientific Results Writing Guidelines
  [DETAILS] Results section writing template — role, aim, style/volume/miscellaneous rules, and a per-figure paragraph structure that anchors each `Fig N` to a registered `\vclaim{}`. Composes with `41_figure-first-communication.md` (the figure-list and panel-list agreement protocol that determines the results-section paragraph order) and `26_writing-during-exploration.md` (in-flight `\vclaim{}` / `\placeholder{}` / `\hlref{}` discipline). V0 SKELETON matching the 30-33 voice — awaiting operator iteration to refine the substance to the Nature-style detail.
tags: [scitex-writer-writing-results]
requires:
  - scitex-stats
  - figrecipe
  - scitex-io
  - scitex-clew
---

<!--
v0 skeleton status:
  - Structure modelled on the existing 30-33 per-section templates
    (abstract, introduction, methods, discussion).
  - Substance is a scaffold — the operator wrote the existing 30-33 in
    his own Nature-style voice; this leaf is meant to be iterated in
    that same voice. The agent has provided structural placeholders,
    not finalized prose.
  - Composes with 41_figure-first-communication.md (results-section
    paragraph order = agreed figure order) and
    26_writing-during-exploration.md (claim discipline).
-->

# Scientific Results Writing Guidelines

## Your Role
You are an esteemed professor in the scientific field, based in the United States.

## Aim of Results

The results section reports, in figure order, what the analysis
showed. Each paragraph corresponds to one figure (`Fig 1` →
paragraph 1, `Fig 2` → paragraph 2, etc.) and lands one or more
manuscript-claim sentences, each anchored to a registered
`\vclaim{}`. The results section is the **factual record** that the
introduction's hypotheses test against and the discussion
interprets.

## Rules

### Style
- Follow the format of the template provided below
- Your revision should conform to the language style typical of a scholarly article in biology
- Use technical language suitable for neuroscience journals
- Spell out abbreviations and acronyms in their first appearance
  (considering they have been introduced already in introduction and
  methods when possible)
- Include a clear, concise topic sentence in each paragraph — the
  topic sentence states the figure's headline finding
- Use transition phrases between paragraphs to make the results
  section coherent and cohesive
- The results-section paragraph order MUST equal the figure order
  (see
  [41_figure-first-communication.md](41_figure-first-communication.md)
  and
  [`scientific/01_figures_02_logic-and-ordering.md` §3](../../scientific/01_figures_02_logic-and-ordering.md))

### Volume
- Ensure each results paragraph is dense and number-anchored — typically
  4-8 sentences per figure

### Reproducibility
- Every number cited must reference a registered claim — `\vclaim{<id>}`
- Use past tense (the study has been completed)
- Use passive voice for procedures, active voice for observations
- See [13_claims.md](13_claims.md) for the claim-registration mechanism

### Miscellaneous
- Explicitly indicate species with sample sizes
- Add relevant references when applicable
- Keep existing references as they are
- Maintain quantitative measurements as they are written
- Target audience is neuroscience/psychology specialists
- Pay careful attention to the use of hyphens, en dashes, em dashes, and minus signs
- Avoid unnecessary adjectives for emphasizing like "significantly", "well"
- If tex tags are inserted, please conform to the LaTeX style
- Return as code block: ``` tex YOUR REVISION ```
- Use LaTeX format
- When adding references (to literature, tables, or figures) will
  enhance the quality of the paper, insert a placeholder using this
  LaTeX command `\hlref{XXX}`

## Results Template (per-figure paragraph structure)

One paragraph per agreed `Fig N`. The agreed figure list is fixed
upstream by the figure-first agreement protocol
([41_figure-first-communication.md](41_figure-first-communication.md)).

Each paragraph follows this structure:

### [1. Headline finding (1 sentence — topic sentence)]
State what `Fig N` shows in one sentence. The headline finding is the
single fact the figure is in the paper for. Use past tense.

> *V0 placeholder — operator iteration to refine to Nature-style.*

### [2. Per-panel walk-through (panel-by-panel)]
Walk through each agreed panel (`a.` `b.` `c.` ...) in order, with
one or two sentences per panel. Each sentence references the panel
explicitly (`Fig N.a`) and the number it carries
(`\vclaim{<claim_id>}`):

```
"In `Fig N.a`, the cohort overview shows ... \vclaim{<id>}.
In `Fig N.b`, ...
In `Fig N.c`, ..."
```

The panel order in the paragraph MUST equal the panel order in the
figure (alphabetical, lowercase).

### [3. Statistical anchor (where applicable)]
Where a comparison is shown, report the **brief** statistical
anchor: test name, sample sizes (n), key effect size, p-value with
stars. **The full statistical detail (degrees of freedom, exact
test parameters, justification for choice of test) belongs in the
METHODS section, not here.** See
[22_writing-figures-stats.md](22_writing-figures-stats.md) §
"Statistical Reporting" for the canonical reporting form and
[40_paper-writing-protocol.md § "Detail-location rule"](40_paper-writing-protocol.md)
for the cross-section depth discipline.

The same rule applies to acquisition parameters, equipment
versions, and procedural detail: **BRIEF in results and captions,
FULL in methods.** Duplication across all three is the symptom of
a flow violation.

#### scitex.stats mandate

Use `scitex.stats` (NOT raw `scipy.stats` / `statsmodels` ad-hoc)
for every statistical test in the results section. `scitex.stats`
provides PRESETS that emit the full reporting anchor (n / dof /
effect size / p / stars / test name / H0) in the canonical form
— so the in-line `\vclaim{}` reference in the results prose
resolves to a numerically complete and structurally consistent
anchor. Raw `scipy.stats` calls are a flow violation (parallels
the FigRecipe mandate for figures).

See
[22_writing-figures-stats.md § "scitex.stats mandate"](22_writing-figures-stats.md)
for the rationale and the per-preset pointer; the
`requires: [scitex-stats]` declaration on this leaf makes the
mandate load-bearing.

#### Long-value footnote rule

If a single statistical value or expression in the prose grows
**long enough to disrupt the reader's flow** (multi-clause
parenthetical, four-line expression, multi-group CI), offload the
full value to a **footnote** and keep the in-line citation brief.
The footnote is the third location in the detail-location
discipline (after prose / caption / methods).

See
[22_writing-figures-stats.md § "Long-value footnote rule"](22_writing-figures-stats.md)
for the worked example and the threshold guidance.

### [4. Forward reference to discussion (optional)]
If the finding feeds a discussion point, flag with a one-clause
forward reference. The full interpretation belongs in
[33_writing-discussion.md](33_writing-discussion.md), NOT here.

## Results-section ordering — non-negotiable

**The order of paragraphs in the results section MUST equal the order
of figures in the manuscript.** This is the load-bearing constraint
that the figure-first agreement protocol (step 1 of
[40_paper-writing-protocol.md](40_paper-writing-protocol.md)) is
designed to lock down before any results-section prose is written.

Reverse the order and the paper rewrites itself. See
[`scientific/01_figures_02_logic-and-ordering.md` §3](../../scientific/01_figures_02_logic-and-ordering.md)
for the universal principle.

## Concurrent-with-experiments discipline

The results section is the section MOST coupled to in-flight data
arrival. Use the in-flight discipline from
[26_writing-during-exploration.md](26_writing-during-exploration.md):

- Numbers from registered claims → `\vclaim{<id>}`.
- Prose-not-yet-written → `\placeholder{}` / `\ph{}`.
- Citation-not-yet-added → `\hlref{XXX}`.
- v0 / pilot / honor-system data → explicit transparency paragraph
  per [26_writing-during-exploration.md](26_writing-during-exploration.md)
  § "v0 / pilot vs final / structurally-masked data".

The figure-list-agreement loop (`41_*`) is the OUTER scaffold; the
`\vclaim{}` / `\placeholder{}` discipline is the INNER scaffold. Both
are required.

## Honest grounding (carryover from scitexification)

Every results-section claim sentence is either:

1. Anchored to a resolved `\vclaim{<id>}` with evidence, OR
2. Anchored to a `\vclaim{<id>}` whose value is `null` + reason
   (the number couldn't be extracted; the panel didn't pan out — see
   [`scientific/06_scitexification/00_playbook.md` § "Honest
   source-grounding"](../../scientific/06_scitexification/00_playbook.md)).

A results-section paragraph that drops a planned panel without
explanation is the **silent-attrition antipattern** at the figure
layer — forbidden.

A planned `Fig N` that was agreed in step-1 but doesn't appear in the
final manuscript must be: (a) reinstated; (b) moved to supplementary
with an explicit text marker; OR (c) called out in the paragraph that
WOULD have referenced it ("we attempted to measure X but the panel
was inconclusive — see SI methods §M.4"). Never silently disappear.

## Pitfalls (v0 — operator iteration to refine)

- **Writing the results section before the figure list is agreed.**
  Results-paragraph order equals figure order; without the agreed
  figure list, you're guessing at structure. See
  [40_paper-writing-protocol.md](40_paper-writing-protocol.md) step
  1.
- **Hand-writing a number without `\vclaim{}`.** Reproducibility
  breaks; the pre-submission grep gate can't audit. See
  [13_claims.md](13_claims.md).
- **Drifting into discussion / interpretation.** Results = facts;
  discussion = interpretation. Forward references to discussion are
  one-clause flags, not paragraphs.
- **Operator-iteration placeholder** — refine the per-paragraph
  template, the per-panel walk-through phrasing, and worked
  examples here.

## Usage

Provide your results draft text below. The revision will be returned
in a LaTeX code block.

``` tex
YOUR REVISED RESULTS
```

## Related

- [40_paper-writing-protocol.md](40_paper-writing-protocol.md) — the
  umbrella; results is step 2.
- [41_figure-first-communication.md](41_figure-first-communication.md)
  — figure-first agreement protocol; the agreed figure list fixes
  the results-paragraph order.
- [22_writing-figures-stats.md](22_writing-figures-stats.md) —
  per-figure rendering rules + statistical reporting form.
- [13_claims.md](13_claims.md) — `\vclaim{}` registration.
- [26_writing-during-exploration.md](26_writing-during-exploration.md)
  — in-flight discipline (`\vclaim{}` / `\placeholder{}` / `\hlref{}`
  / pre-submission grep gate).
- [33_writing-discussion.md](33_writing-discussion.md) — where
  forward-referenced results land.
- `~/.claude/skills/scitex/scientific/01_figures_02_logic-and-ordering.md`
  — universal results-order = figure-order rule.
- `~/.claude/skills/scitex/scientific/06_scitexification/00_playbook.md`
  — universal honest-grounding norm; the silent-attrition antipattern
  at the figure layer.
