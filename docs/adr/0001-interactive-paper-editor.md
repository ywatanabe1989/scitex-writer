# ADR 0001 — SSOT interactive research-paper editor (pen-tablet annotation + interactive clew provenance)

- **Status:** Proposed (hub-approved 2026-07-08; figrecipe + clew contracts folded; palette-alignment + gate strict-mode are open coordinated items)
- **Date:** 2026-07-08
- **Deciders:** operator, scitex-writer (lead/author), scitex-hub, figrecipe, scitex-clew, scitex-dev, scitex-ui
- **Affects:** scitex-hub, figrecipe, scitex-clew, scitex-ui, scitex-live-paper
- **Builds on:** card `live-paper-viewer-component` (operator decisions, Telegram 553–571) + operator scope refinement (msgs 291–300)

## Context

The operator wants ONE interactive research-paper PDF viewer/editor, reused across the ecosystem (Writer authoring, hub project view, Journal reading, Live Paper published), not duplicated. Three capabilities:

1. **Pen-tablet annotation → agent-feedback loop.** The operator marks the PDF with a pen (Wacom/iPad/finger); marks become structured requests routed to the responsible agent. The pen's job is **spatial "here" communication** to the agent, not handwriting.
2. **Interactive clew provenance on the paper.** Hover a claim to light its claim → computed-output → source chain; lineage arrows between claims; each claim colored by its source-gate verdict.
3. **Inline source-reachability feedback.** "This claim doesn't reach a source; fix + re-verify," surfaced inline as you edit.

"Live paper" is a document **state/capability**, not a destination app (operator, msgs 566–568).

## Integration doctrine (SoC — the load-bearing principle, operator msgs 296–300)

Every seam separates **the neutral side that exposes ports/hooks** from **the side that carries logic and injects signals**, loosely coupled and mutually unaware — third parties plug in identically. Named patterns:

- **Ports & Adapters (Hexagonal).** The neutral provider (here: **writer** + **scitex-ui**) exposes stable *ports* — the viewer hook API, the mark/comment schema, the shared feeds — and depends on none of its producers.
- **Producer / Consumer (Publish–Subscribe) over a neutral feed.** Producers (**clew**, **figrecipe**) write signals into a shared, source-stamped feed; the consumer reads. Merge-by-source: each producer replaces only its own entries. No type-coupling.
- **Plugin / entry-point registry.** Third-party producers register against a stable interface, mutually unaware (e.g. clew's `clew-source-reachability` under `scitex_dev.gate.checks`).
- **Optional (soft) dependency — "connect if present."** scitex-dev's `try_import` idiom: wire the producer iff its package is importable; degrade gracefully otherwise.

**Consequence for this design:** writer owns **neutral ports only** — the PDF-viewer hook API, the `figure-requests` and `hints`/marks feeds, the PDF↔claim coordinate contract. clew and figrecipe are **producers**; the editor consumes their signals through the feeds/ports and never imports their logic. Each repo knows only itself and publishes the ports others need.

## Decision

### 1. Where it lives — scitex-ui App tier, two layers

Precedent exists: **scitex-ui (`@scitex/ui`)** is the shared TS+CSS component library already consumed by scitex-hub, figrecipe, and scitex-writer. The editor is a reusable App-tier component and belongs there — **not** a new package, **not** embedded in writer.

- **Layer 1 — framework-neutral PDF renderer + annotation surface (scitex-ui).** A vanilla-TS class wrapping PDF.js that takes a container element, plus a thin React adapter. Exposes the **action-hook API**: `page`, `coords`, `region-select`, `pen-input` events. **The minimal pen UI is part of L1 and ALWAYS present** wherever a PDF is shown (operator msg 292: "PDF and pen UI must always be together") — it is not an editor-only feature. Framework-neutral is mandatory (hub's shell is vanilla-TS + Django; React only via adapters; no Electron).
  - **Packaging:** L1 exported from scitex-ui as a named `exports` subpath — **`@scitex/ui/pdf-viewer`** — reachable directly, not only through the app/shell bundle (avoids the figrecipe bridge-init class of break; hub's Vite bridge pins this subpath).
- **Layer 2 — claim-aware viewer (scitex-live-paper).** Claim anchors, provenance panel + DAG, verdict coloring, re-verify — built strictly on L1's event/anchor API, depending on the clew model.
- **Auto-upgrade detection:** the bundle spec exposes a **cheap marker** (a claims-sidecar file present in the bundle listing, or a manifest field) so a consumer decides L1-vs-L2 from the listing alone, without parsing the bundle: plain PDF → L1; claims-bundle marker → L2.

**First consumer (concrete first step):** swap Writer's existing Overleaf-style right-hand PDF pane to the shared component. (operator, msg 571)

### 2. Pen UI — minimal, always-on, spatial

- **Always present** in the PDF pane (part of L1). Input rides **Pointer Events** (Wacom + iPad + finger); responsive + touch mandatory (hub mobile priority; desktop-only is rejected).
- **Minimal — shape marks only:** highlight, underline, circle, arrow, box, freehand. **No handwriting text.** Text goes to **OS voice input** (e.g. Win+H) into a text box. (operator msgs 293–294)
- **Purpose:** tell the agent *"here, spatially."* A mark + optional voice/typed note is saved as a **coordinate-tied comment** and dispatched to the responsible agent.
- **Domain buttons (the research-review moat):** Highlight · Claim · Question · Issue · Citation-needed · Figure-check · Method-check · Export. These turn a generic PDF viewer into a research-review environment.
- **Three modes:** **Read** (scroll/zoom/search) · **Markup** (highlight/underline/circle/arrow/erase) · **Review** (comment box + voice + AI clean-up + export). The consumer passes the mode.

### 3. Mark routing — by target (producer-owned logic)

- **Mark on prose / a claim** → feedback into the writer/clew hints loop (a coordinate-tied comment; the workspace/project agent is the feedback consumer, not live-paper).
- **Mark on a figure, intent "change this"** → a **figure-change-request to figrecipe** (its lane). Schema **`figure-requests/1`** — file `.scitex/writer/figure_requests.json` = `{ "requests": [ <request>, … ] }`:
  - `id` (req) — stable, e.g. `figreq:<claim_id>:<uuid>`.
  - `claim_id` (req) — sanitized save-path `re.sub(r'[^a-zA-Z0-9]','',savepath)`; **must match render_clew/hints claim_id exactly** (the cross-feed join).
  - `region` (req) — `{x0,y0,x1,y1}` floats **normalized 0..1 of the rendered-image bbox, TOP-LEFT origin / y-DOWN** (image + hitmap convention — NOT mpl bottom-up), so it maps straight onto the hitmap array (row 0 = top) with no y-flip.
  - `request_text` (req) — OCR'd/typed change; `source` (req) = `"writer"`; `status` (req) = `open` (writer sets) → `addressed`/`rejected` (figrecipe sets); `ts` (req) ISO8601.
  - `panel` — `{row,col}` | `{label}`; `recipe_ref` — `.yaml` path (figrecipe resolves from claim_id if null); `stroke_path` — normalized polyline; `element_ref` — recorded call-id, null → figrecipe's **hitmap resolves it** (`fr.save(save_hitmap=True)`).
  - **Ownership:** writer writes everything except `status` + `response`; figrecipe only flips `status` and appends `response {by:"figrecipe", ts, note, recipe_rev?}`.
  - **Dispatch:** a2a nudge (promptness) + this durable feed (SSoT, merge-by-source). **Reuse figrecipe surfaces** — figure pane = `figrecipe._django` (preview) + `figrecipe._hitmap` (targeting) + `figrecipe._editor`/`_call_overrides` (apply). Writer builds no figure rendering.
- **Mark on a figure, intent "what is this / where from"** → **read-only provenance query to clew** (hitmap element → call-id → clew source), NOT a change request.

### 4. Provenance layer — join by claim_id, verdict from the feed

- **Static marks:** clew's `claims.json` (schema `1.6-unified`: per-claim status + link + source_file + source_session + chain flags).
- **Hover chain:** live clew API — `clew.chain(target_file)`, `clew.dag(targets)`, `clew.mermaid(...)`.
- **Lineage arrows (claim→claim):** clew exports `claim_id → [parent claim_id]` (derived from `source_session` → session DAG) alongside the 1.6 feed (`clew-claim-lineage-edge-export`), so the overlay draws arrows without re-deriving.
- **Coordinate map:** join by `claim_id`; clew emits a per-claim `pdf_anchor` as the **full destination string `clew-<slug>`** (slug `[A-Za-z0-9_-]`) in the 1.6 feed — byte-identical to the LaTeX `\hypertarget{clew-<id>}`, so **neither side re-prefixes** (the macro consumes `pdf_anchor` verbatim). Zero mapping table. Pin the prefix rule with card `writer-clew-macros-hypertarget-anchors`.
- **Palette:** the component is **palette-agnostic** — it reads hexes from the feed's `palette` field into CSS custom properties (`--clew-verdict-verified/-suspect/-failed/-exception`), never hardcodes; themable via scitex-ui theme (dark/light). The **hex source-of-truth is an open coordinated decision** (clew + figrecipe + live-paper + operator), gated on a **CUD-safety check of both palettes** before locking — clew's exported palette (`2da44e/d29922/cf222e/8250df`) and figrecipe's `_PARAMS.py` (`14B414/E6A014/FF4632/C832FF`) differ; "align to figrecipe" must not regress colorblind-safety. Not an ADR blocker (feed-driven → one-place change).

### 5. Inline engine — two surfaces, clew/scitex-dev SoC preserved

- **Real-time per-claim (as you annotate):** query clew directly — `scitex_clew.is_claim_grounded(claim_location, *, workdir=".") → GroundingVerdict {grounded, claim_id, matched_source{path,sha256}|None, reason, fix_hint}`; CLI `scitex-clew grounding <claim-location|claim-id> [--json]`. `reason ∈ {grounded, no_chain_match, no_manifest, manifest_untrusted, claim_not_found}`. **Color map (clew-verified — `grounded` drives it):** **green** = `grounded=True, reason=grounded`; **amber** = `grounded=True, reason=no_manifest` ONLY (defensive-True: no/inactive manifest — passes compose, weak for publish); **red** = `grounded=False, reason ∈ {no_chain_match, manifest_untrusted}`; `claim_not_found` = error. (Note: `manifest_untrusted` is `grounded=False` → **red**, not amber.) **Gate-consistency:** `grounded` mirrors the gate's `is_grounded` exactly, so the inline signal never disagrees with the publish gate. Do NOT call the whole-workdir gate per keystroke. (Co-owned clew + scitex-dev; clew acked + speced the stub — card `clew-per-claim-grounding-api`.)
  - **Consumed via a neutral port — NEVER a hard import (operator msg 305).** The editor calls clew's exposed port: the CLI/JSON `scitex-clew grounding --json` (or, server-side, an **optional** `try_import` of `scitex_clew`). Writer's core does **not** depend on clew being installed; absent clew, grounding degrades gracefully to the compile-time gate feed (advisory, non-live). clew stays an optional **producer**; writer stays the neutral **consumer**. Same rule for every producer signal (claims.json, figure-requests, hints) — connected through feeds/ports, never a hard dependency.
- **Publish boundary (aggregate authority):** `scitex-dev gate <workdir> --stage pre-submission --json` → `GateReport.blocking` + per-Finding `{check_id, message, severity, fix_hint, claim location}`; editor renders inline by filtering Findings on `claim.location`.
- **Gate policy + machine-readable findings:** today "no registered sources → PASS" (defensive). (1) Per-Finding gains a machine-readable **`reason`** field (scitex-dev lands `reason: Optional[str]=None` on `Finding` first — the ordering-first item; clew's `_gate_plugin` then populates it) so the editor branches on `reason`, not message-parsing. (2) When the manifest is absent/inactive, clew emits **one capsule-level ADVISORY finding** (`reason=no_manifest`); `scitex-dev gate --stage publish --strict` **promotes it to blocking** while **compose ignores** it — the escalation hook that keeps the defensive PASS a compose convenience, not a publish loophole.
- SoC: rule + DB in **clew**; aggregation + contract in **scitex-dev**; editor consumes verdicts, owns neither.

### 6. Permission modes — one vocabulary with the gate; mode ≠ identity

Editor modes map onto gate stages (`.scitex/dev/config.yaml gate.enforce`). **The consumer passes `mode` explicitly; the component never infers mode from a session role.**

- **compose** — free editing; gate runs **advisory** inline (findings shown, nothing blocks). *Hub maps* write-capable identities (`user`, or a writable `visitor` in their own workspace).
- **review** — pre-submission gate boundary evaluated as **blocking**. **Journal** owns reviewer identity/grants (venue ops) and maps them → review. Hub has **no** reviewer role and won't grow one.
- **published** — crossing a passed pre-submission gate; public read. *Hub maps* everyone (incl. `readonly_visitor`, anonymous).

Hub doctrine (mandatory): **viewing is never blocked** for any role; write/annotate actions **fail loud** with a structured 403 + actionable toast (Sign up / Log in) — expose affordances conditionally, never hide the document. Re-verify on published bundles is write-class (costs compute) → gated to authenticated users.

### 7. Distribution / boundaries

- Today: pip sibling install with built assets. **Dependency:** scitex-ui npm publication (card `scitex-ui-npm-publication`). **Caution:** define the `package.json` `exports` map carefully (card `hub-npm-build-figrecipe-bridge-broken`).
- live-paper repo keeps: (1) bundle spec + static-site exporter, (2) the L2 claim-viewer component, (3) clew re-verify on pinned bundles. Journal stays independent (venue ops), same component in review mode.

## MVP (start small — operator directive)

Ship the smallest research-useful slice first, then grow:

**MVP:** PDF.js viewer (L1) in Writer's right pane + overlay marks (highlight / rectangle / freehand / circle / arrow) + a comment box + OS voice→text + AI clean-up of the note + coordinate-tied save + markdown export of comments. Domain buttons (Claim / Issue / Citation-needed / Figure-check / Method-check) as the mark's category. Read/Markup/Review modes.

Deferred past MVP: interactive provenance overlay (needs clew `pdf_anchor` + grounding API + lineage edges), figure-change-request round-trip (needs `figure-requests/1` + figrecipe producer), published/review modes, mobile polish.

## Consequences

- One viewer across Writer / hub / Journal / Live Paper; authoring and published reading share one component at different modes — parity by construction.
- Writer stays a **neutral port provider**; clew/figrecipe are optional producers — the editor works with any subset present (`try_import` doctrine).
- Hard dependency: clew's per-claim grounding API (acked + speced; stub-first). Soft dependencies: clew `pdf_anchor` + lineage edges, figrecipe producer, scitex-ui npm publication.

## Open items (coordinated, non-blocking)

1. **Palette hex SoT** — CUD-safety check of clew vs figrecipe palettes before locking; component is feed-driven meanwhile.
2. **Gate strict-mode knob** — so "no registered sources → PASS" can't become a publish loophole.
3. **Sequencing** — clew deliverables land off develop after clew PR #128 (multihost); stub signatures first. Writer ships `hints` merge-by-source before figrecipe wires its producer.
4. **ADR review** — Affects clew + figrecipe: both to confirm field shapes on this draft.
