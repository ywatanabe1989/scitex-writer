---
description: |
  [TOPIC] Paper-writing umbrella protocol — agent ↔ user collaborative flow for turning a (typically scitexified) analysis into a manuscript.
  [DETAILS] The top-level scaffold that composes the existing scitex-writer skill set into a single agent-driven flow: figure-first communication (`41_*`) → results-section drafting (anchored to the agreed figure list) → methods (reproducibility) → introduction (gap → hypothesis spine) → abstract (last, distilled from the rest) → discussion (fulfils the introduction's promise). Reuses the existing per-section templates verbatim — `30_writing-abstract`, `31_writing-introduction`, `32_writing-methods`, `33_writing-discussion`, `36_writing-results` (v0 skeleton; operator iteration to refine) — and the in-flight discipline in `26_writing-during-exploration` (`\vclaim{}`, `\placeholder{}`, `\hlref{XXX}`, pre-submission grep gate). Bakes in the operator's framing: paper-writing is CONCURRENT with experiments, not sequential after them. V0 SKELETON awaiting operator iteration on the inter-section flow specifics.
tags: [scitex-writer-paper-writing-protocol]
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
