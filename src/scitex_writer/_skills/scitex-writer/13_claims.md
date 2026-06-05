---
description: |
  [TOPIC] Claims
  [DETAILS] Verifiable claims — add, track, render claims linked to evidence..
tags: [scitex-writer-claims]
---

# Claims

Claims are verifiable statements linked to evidence (data, figures, statistics).

## scitex-clew anchoring (load-bearing)

Every `\vclaim{<id>}` in the manuscript is backed by a **scitex-clew
claim record** — a single entry in `claims.json` carrying:

- the **value** (the number, string, or range the manuscript cites);
- the **session hash** (SHA-256 of the run that produced the value);
- the **source file** the value was emitted from;
- the **timestamp** of registration.

At LaTeX compile time the `\vclaim{<id>}` is resolved by looking up
the registered record and substituting its value. A `\vclaim{}` that
fails to resolve renders as `[claim:<id>]` in the PDF (the
pre-submission grep gate in
[26_writing-during-exploration.md](26_writing-during-exploration.md)
catches these).

Why this matters: the registration mechanism IS the honest-grounding
contract at the manuscript layer. Every number's provenance chain is
mechanical (`\vclaim{<id>}` → `claims.json` entry → session hash →
script source → data inputs → all DAG-anchored). The scitexify
silent-attrition antipattern (silent rephrasing of a number without
provenance) is structurally prevented because the manuscript can only
cite numbers that were registered through a script run.

`requires: [scitex-clew]` declared on
[36_writing-results.md](36_writing-results.md) and
[40_paper-writing-protocol.md](40_paper-writing-protocol.md) is
load-bearing on this anchoring mechanism.

## MCP Tools

| Tool | Description |
|------|-------------|
| `writer_claim_add` | Add a verifiable claim |
| `writer_claim_get` | Get claim by ID |
| `writer_claim_list` | List all claims |
| `writer_claim_remove` | Remove a claim |
| `writer_claim_render` | Render claims to LaTeX |
| `writer_claim_format` | Format claim for display |

## Related

- [26_writing-during-exploration.md](26_writing-during-exploration.md)
  — in-flight `\vclaim{}` / `\placeholder{}` / `\hlref{}` discipline,
  pre-submission grep gate, claim-type pitfall (`text` → silently
  dropped; use `value`).
- [36_writing-results.md](36_writing-results.md) — every
  results-section claim sentence is anchored to a `\vclaim{}`.
- [40_paper-writing-protocol.md](40_paper-writing-protocol.md) —
  umbrella protocol that composes the registration mechanism into
  the paper-writing flow.
- `~/.claude/skills/scitex/scientific/06_scitexification/00_playbook.md`
  — the universal honest-grounding norm; the clew registration is
  the mechanism that operationalises it at the manuscript layer.
