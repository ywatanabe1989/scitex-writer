# ADR 0001 — SSOT interactive research-paper editor (pen-tablet annotation + interactive clew provenance)

- **Status:** Proposed (hub-approved 2026-07-08; figrecipe + clew seam inputs pending their return)
- **Date:** 2026-07-08
- **Deciders:** operator, scitex-writer (lead/author), scitex-hub, figrecipe, scitex-clew, scitex-dev, scitex-ui
- **Affects:** scitex-hub, figrecipe, scitex-clew, scitex-ui, scitex-live-paper
- **Supersedes/builds on:** card `live-paper-viewer-component` (operator decisions, Telegram 553–571)

## Context

The operator wants ONE interactive research-paper PDF viewer/editor, reused across the ecosystem (Writer authoring, hub project view, Journal reading, Live Paper published), not duplicated. Three capabilities:

1. **Pen-tablet annotation → agent-feedback loop.** The operator annotates the compiled PDF with a pen (Wacom / iPad / finger); marks become structured requests routed to the responsible agent.
2. **Interactive clew provenance on the paper.** Hover a claim to light its claim → computed-output → source chain; lineage between claims; each claim colored by its source-gate verdict.
3. **Inline source-reachability feedback.** "This claim doesn't reach a source; fix + re-verify," surfaced inline as you edit.

"Live paper" is a document **state/capability**, not a destination app (operator, msgs 566–568); the interim live-paper hub tile dissolves once the capability is embedded.

## Decision

### 1. Where it lives — scitex-ui App tier, two layers

Precedent exists: **scitex-ui (`@scitex/ui`)** is the shared TS+CSS component library already consumed by scitex-hub, figrecipe, and scitex-writer (Django `INSTALLED_APPS` + `@scitex/ui`). The editor is a reusable App-tier component and belongs there — **not** a new package (fragments the shared-UI home) and **not** embedded in writer (would invert the dependency and couple hub to writer's release cadence).

- **Layer 1 — framework-neutral PDF renderer (scitex-ui).** A vanilla-TS class wrapping PDF.js that takes a container element, plus a thin React adapter. Exposes an **action-hook API**: `page`, `coords`, `region-select`, `pen-input` events (operator-specified, msgs 561–563). Used by hub's project/file view for *any* PDF. Framework-neutral is mandatory — hub's shell is vanilla-TS + Django templates; React only via adapters; no Electron.
  - **Packaging (hub flag 4):** L1 is exported from scitex-ui as a first-class **library entry at a named `exports` subpath — `@scitex/ui/pdf-viewer`** — reachable directly, NOT only through the app/shell bundle. (A missing/implicit subpath is exactly the class of mistake behind the figrecipe bridge-init break; hub's Vite bridge pins this subpath.)
- **Layer 2 — claim-aware viewer (scitex-live-paper).** Claim anchors, provenance panel + DAG, verdict coloring, re-verify — built strictly on Layer 1's event/anchor API, depending on the clew model.
- **Auto-upgrade detection (hub flag 3):** a consumer picks L1 vs L2 **without downloading/parsing the whole bundle**. The bundle spec exposes a **cheap marker** — a claims sidecar file whose *presence in the bundle listing* (or a single manifest field) signals L2 — so hub's project file view decides from the listing alone: plain PDF → L1; claims-bundle marker present → L2.

**First consumer (concrete first step):** swap Writer's existing Overleaf-style right-hand PDF pane to the shared component (Layer 1 + claim layer + hooks). (operator, msg 571)

### 2. Pen-tablet loop — generic hooks, agent-routed

- Pen input rides **Pointer Events** (covers Wacom, iPad, finger) → responsive + touch mandatory (hub mobile is an operator priority; a desktop-only viewer is rejected).
- Marks are captured by Layer 1's hook API and dispatched by the **consuming app** to the **workspace/project agent** (NOT live-paper — keep the hook surface generic).
- **Routing by target:** a mark on a **figure** = a figure-change request → **figrecipe** (its lane). A mark on a **claim / prose** = feedback into the writer/clew hints loop. (figrecipe seam contract pending figrecipe's input — see Open Questions.)
- Handwriting: pen = marks (circle/underline/arrow/box/region); text = OS dictation (voice), not an in-app OCR engine (operator's earlier steer). OCR of handwriting is out of scope for v1.

### 3. Provenance layer — join by claim_id, verdict-colored

- **Coordinate map:** PDF ↔ claim join by `claim_id`, using the same sanitize as `render_clew`. Needs per-claim PDF anchors (`\hypertarget{clew-<id>}`) — tracked in card `writer-clew-macros-hypertarget-anchors`; the web overlay locates claims by these anchors.
- **Verdict palette (hub flag 2):** the component does NOT hardcode hex. It exposes **CSS custom properties** — `--clew-verdict-verified` / `--clew-verdict-suspect` / `--clew-verdict-failed` / `--clew-verdict-exception` — with the SciTeX standard values as *defaults* (verified `#14B414` / suspect `#E6A014` / failed `#FF4632` / exception `#C832FF`), themable via scitex-ui's theme variables so the palette adapts to hub's dark/light themes. (Aesthetics are the operator-delegated province of hub; hardcoded hex would force forks.)
- **Chain data:** from clew (claims.json "1.6-unified" and/or a live query) — exact source pending clew's input.

### 4. Inline engine — two surfaces, clew/scitex-dev SoC preserved

- **Real-time inline (per-claim, as you annotate):** query **clew's per-claim grounding** directly — clew to expose `is_grounded` as `scitex-clew grounding <claim> --json` and/or `is_claim_grounded()`, returning `{grounded, matched_source, missing_reason, fix_hint}`. This is the design's **one true external dependency**. Status: durably carded as `clew-per-claim-grounding-query-api-20260708` (full ask + internal ref + verdict shape + SoC); **clew is offline — not yet acked**; scitex-dev retries the direct request when clew returns. Do NOT call the whole-workdir gate per keystroke.
- **Publish boundary (aggregate authority):** `scitex-dev gate <workdir> --stage pre-submission --json` → `GateReport.blocking` + per-Finding `{check_id, message, severity, fix_hint, claim location}`; the editor renders inline by filtering Findings on `claim.location`.
- SoC: rule + DB stay in **clew** (`clew-source-reachability` check under `scitex_dev.gate.checks`); aggregation + contract stay in **scitex-dev**.

### 5. Permission modes — one vocabulary with the gate

Map editor modes onto gate stages (`.scitex/dev/config.yaml gate.enforce`), not a parallel vocab. **Separation of mode vs identity (hub flag 1):** the **consumer passes `mode` explicitly** (`compose` / `review` / `published`); the component **never infers mode from a session role.** Each consumer owns the role→mode mapping in its own domain:

- **compose** — free editing; the gate runs **advisory** inline (findings shown, nothing blocks). *Hub maps* write-capable identities (a `user`, or a writable `visitor` in their own workspace) → compose.
- **review** — the pre-submission gate boundary evaluated as **blocking**. *Journal* owns reviewer identity/grants (venue ops) and maps them → review. **Hub has no reviewer role and will not grow one** — reviewer identity is not the component's concern.
- **published** — crossing a passed pre-submission gate; public read. *Hub maps* everyone (incl. `readonly_visitor` and anonymous) → published.

Hub doctrine (mandatory): **viewing is never blocked** for any role; write/annotate actions **fail loud** with a structured 403 + actionable toast (Sign up / Log in). Expose annotation affordances conditionally on mode — never hide the document. Re-verify on published bundles is a write-class action (costs compute) → the consumer gates it to authenticated users.

### 6. Distribution / boundaries

- Today: pip sibling install with built assets. **Dependency:** scitex-ui npm publication (card `scitex-ui-npm-publication`) for clean cross-package consumption.
- **Caution:** define the `package.json` `exports` map carefully — a missing specifier currently breaks hub's Vite build (card `hub-npm-build-figrecipe-bridge-broken`).
- live-paper repo keeps: (1) bundle spec + static-site exporter (distribution artifact rendered outside hub), (2) the Layer-2 claim-viewer component, (3) clew re-verify on pinned bundles. Journal stays independent (venue operations), using the same component in review mode.

## Consequences

- One viewer implementation across Writer / hub / Journal / Live Paper; no duplicate PDF viewers.
- Writer's authoring loop and the published reading experience share a single component at different permission modes — parity by construction.
- Hard dependency on clew exposing a per-claim grounding query (in clew's queue) for the inline engine; until then, compose mode falls back to the compile-time gate feed (advisory, non-live).
- scitex-ui npm publication becomes a shared-infra dependency for clean distribution.

## Open questions (for co-owner input)

1. **clew:** confirm the per-claim grounding query signature + whether the hover-chain data is static (claims.json) or live-queryable; confirm the pdf_anchor id scheme. Status: enabler carded (`clew-per-claim-grounding-query-api-20260708`) but clew is offline and has NOT yet acked — awaiting clew's return.
2. **figrecipe:** the mark→figure-change request payload (figure id/save-path, mark geometry, requested-change text), the dispatch channel (a2a / hints-feed / file drop), and figure-quality signals surfaced back inline. (figrecipe currently down.)
3. **scitex-ui / hub:** confirm the App-tier home + the `exports` map contract; sequence against npm publication.
4. **ADR numbering:** confirm this is `0001` in scitex-writer (no existing adr dir) vs. aligning with the mirrored lead-repo `0002-scitex-django-app-standard`.
5. **Handwriting:** confirm pen=marks / voice=OS-dictation for v1 (no in-app OCR).
