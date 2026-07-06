# PDF Annotation → Agent Feedback Loop — Design (writer-owned slice)

> **STATUS: DRAFT — for cross-repo sign-off.** This doc scopes the
> **scitex-writer-owned** slice of the operator's vision (scitex-todo card
> `writer-pdf-annotation-feedback-loop`): the operator pen-tablet-annotates the
> compiled manuscript PDF and those marks flow back to the owning agent as a
> channel notification. It is the artifact that opens the writer + live-paper +
> agentic-journal agreement. **No build starts until §5 is signed off.**

## 1. Motivation & scope boundary

The operator now has a pen tablet and wants to close the human↔agent loop over
the **rendered** paper: mark up the compiled PDF (strokes / region boxes / text
comments), and have those marks reach the agent that owns the manuscript as a
notification — exactly how scitex-agent-container / scitex-todo /
claude-code-telegrammer already push user actions to agents.

This is a 3-repo epic. Ownership splits cleanly:

| Concern | Owner | Rationale (grounded in current board + code) |
|---|---|---|
| **The PDF viewer** — render, text-layer, **annotation-capture UI**, find | **scitex-live-paper** | The canonical viewer is being MOVED to live-paper (cards `live-paper-absorb-writer-pdf-viewer-a..d`). Writer's current `pdf-viewer.ts` header already declares itself minimal: *"no text-layer, no annotation-layer, no find."* Writer will **consume** live-paper's viewer via mount/iframe (card `-d-adopt`), NOT grow its own annotation layer. |
| **The channel-notification pattern** — the notification contract/format the agent consumes | **scitex-agentic-journal** | Owns channel-notification patterns fleet-wide. The emit contract (§4) must be agreed with them, not invented here. |
| **(1) Annotation PERSIST model** and **(2) the annotation→notification EMIT bridge**, plus the **Django shell** that mounts live-paper's viewer | **scitex-writer (this repo)** | Writer already owns the Django app (`src/scitex_writer/_django/`) with the `api_dispatch` + `HANDLERS` registry, the `ProjectState` service, and the coords→source domain knowledge (it owns the `.tex` sources, the claim store, and the compile step). |

**Writer's owned piece is NOT a new viewer.** It is a data model + one HTTP
handler group + a thin emit bridge. Everything the operator *sees and draws on*
is live-paper's. Writer receives the posted annotation, maps it to manuscript
source, persists it, and emits the notification.

Dovetails (not in scope here, but the model must not preclude them): live-paper
interactive figures, and the clew provenance overlay
(`writer-clew-provenance-overlay-pdf`) — an annotation may land on a
provenance-overlaid region, so the coords→source mapping (§2) should be able to
resolve to a claim id, not only a `.tex` line.

## 2. Persist model

### 2.1 The annotation record

One posted annotation is one record. Shape (the wire shape and the stored shape
are the same JSON object):

| field | type | meaning |
|---|---|---|
| `annotation_id` | str (uuid4) | server-assigned if absent; stable across edits |
| `doc_type` | str | `manuscript` \| `supplementary` \| `revision` (matches the viewer's doc-type select) |
| `build_id` | str \| null | the compile build the marks were drawn on (from `.scitex/writer/runtime/builds/builds.json`); pins the PDF the coords refer to |
| `page` | int | 1-based PDF page |
| `region` | `{x, y, w, h}` | normalized 0..1 rect in PDF-page space (resolution-independent) |
| `kind` | str | `text_comment` \| `stroke` \| `region_mark` |
| `payload` | object | `text_comment`: `{text}`. `stroke`: `{paths: [[{x,y}, …]], color, width}` (normalized coords). `region_mark`: `{color}`. |
| `source_ref` | object \| null | coords→source mapping (§2.2); the load-bearing field |
| `author` | str | the human who drew it (operator id / user) |
| `created_at` | ISO-8601 str | server timestamp |
| `status` | str | `open` \| `resolved` (lets the agent close the loop) |

### 2.2 The coords→source mapping (`source_ref`)

This is what makes an annotation actionable rather than a floating scribble. It
answers "**which manuscript source does this mark land on?**" Resolution is
best-effort, most-specific-wins, and every level degrades gracefully to the one
below:

1. **claim** — if the region overlaps a `\vclaim` / provenance-overlay hotspot,
   resolve to `{claim_id}`. Reuses the existing claim store
   (`_mcp.handlers._claim`) already surfaced by `handlers/viewer.py`
   (`api/claims-metadata`). Requires live-paper to report which claim/figure a
   viewer-space rect covers (§5).
2. **figure / table** — if over a float, `{float_type, label}`.
3. **tex line** — else, map (page, region) → a `{file, line}` in
   `01_manuscript/contents/`. This needs SyncTeX (latex emits `.synctex.gz`);
   the mapping is `pdf coord → synctex → tex file+line`.
4. **page-only** — if nothing resolves, `{page}` alone. Never fatal.

`source_ref` is stored as-resolved. The resolver lives writer-side because
writer owns the sources, the claim store, and the compile artifacts. **live-paper
supplies the geometry (page + normalized rect + any hotspot hit); writer supplies
the meaning.** This is the single most important cross-repo seam (§5).

### 2.3 Where it persists — recommendation

**Recommendation: a small SQLite DB at
`<proj-root>/.scitex/writer/runtime/writer.db`, path resolved via
`scitex_config.local_state.runtime_path("writer", "writer.db")` — NOT a
hard-coded path, and NOT a JSON sidecar.**

Rationale, grounded in the fleet convention and the existing code:

- **The convention is already canonical and already used here.** The runtime
  layout is specified in
  `scitex/_skills/general/01_arch_06_local-state-directories.md` and
  implemented in `scitex_config/_ecosystem/_local_state.py`:
  `<proj-root>/.scitex/<pkg>/runtime/` for "logs, PID files, caches, ephemeral
  databases" — gitignored, regenerable. scitex-writer **already writes** to
  `.scitex/writer/runtime/` (the build registry `builds/builds.json`, see
  `scripts/python/_build_id.py`), and the dir already exists with its
  `.gitkeep` + `README.md` seeds. A `writer.db` slots in next to `builds/` with
  zero new convention.
- **Why SQLite over the existing JSON-sidecar style:** annotations are
  *appended concurrently* (the Django server is multi-threaded — see
  `ProjectState._lock`) and *queried by predicate* ("all `open` annotations for
  `doc_type=manuscript` on `build_id=X`", "annotations touching `claim_id=Y`").
  A JSON file forces a read-modify-write of the whole document under a lock on
  every POST (the exact corruption/race footgun the scitex-todo skill warns
  about for `tasks.yaml`). SQLite gives atomic single-row inserts, indexed
  predicate queries, and `status` updates without rewriting siblings — for a
  cost of one stdlib `sqlite3` table. The build registry stays JSON (write-once
  per compile, read-rarely); annotations are a different access pattern.
- **Schema:** a single `annotations` table, columns mirroring §2.1 (JSON columns
  for `region`/`payload`/`source_ref`), indexed on `(doc_type, status)` and
  `annotation_id`. First migration is a `CREATE TABLE IF NOT EXISTS`; no ORM,
  no Django models (writer's Django app is model-less by design — it's a thin
  HTTP shell over `scitex_writer` internals).

**Fallback if SQLite is rejected in review:** a JSONL append-log at
`.scitex/writer/runtime/annotations/<doc_type>.jsonl` (append-only sidesteps the
whole-file rewrite race; queries load-and-filter). Lower engineering cost, worse
query story. SQLite is the recommendation; JSONL is the documented alternative.

## 3. The HTTP surface

Slots into the existing `api_dispatch` + `HANDLERS` pattern
(`_django/views.py`, `_django/handlers/__init__.py`) exactly like
`handlers/scholar.py` and `handlers/viewer.py`. New module
`_django/handlers/annotation.py`; new registry rows:

```python
# handlers/__init__.py — HANDLERS additions
"api/annotations":        (None,                    ("GET", "POST")),  # dispatched by method
"api/annotations/render": (handle_annotations_ping, ("GET",)),         # optional health
```

`api/annotations` is a method-dispatched endpoint (same idiom as `api/claims`,
which the dispatcher resolves by method in `views.api_dispatch`). Parameterized
`api/annotations/<id>` (GET one / PATCH status / DELETE) follows the exact
`api/claims/<id>` fallback branch already in `api_dispatch`.

| Method | Endpoint | Handler | Body / query | Response |
|---|---|---|---|---|
| POST | `/api/annotations` | `handle_add_annotation` | annotation JSON minus server fields (§2.1); `source_ref` may be omitted → server resolves | `{ok, annotation_id, source_ref, notified: bool}` |
| GET | `/api/annotations` | `handle_list_annotations` | `?doc_type=&status=&build_id=` | `{annotations: [...], count}` |
| GET | `/api/annotations/<id>` | `handle_get_annotation` | — | the record |
| PATCH | `/api/annotations/<id>` | `handle_update_annotation` | `{status: "resolved"}` | updated record |
| DELETE | `/api/annotations/<id>` | `handle_remove_annotation` | — | `{ok}` |

Handler contract mirrors `scholar.py`'s POST (`handle_scholar_add_to_manuscript`)
precisely: parse `json.loads(request.body)`, validate required fields, do the
work against a writer-side module, return `JsonResponse`. All resolve
`working_dir` via the shared `_get_project` path; all are `@csrf_exempt` through
`api_dispatch`. The persist + resolve + emit logic lives in a framework-agnostic
`scitex_writer._annotations` module (same layering as `_mcp.handlers._claim`
backing `claim.py`); the handler is a thin wrapper — so the same logic is
reusable from CLI/MCP later.

**POST sequence** (`handle_add_annotation`):
1. parse + validate (page, region, kind, payload present).
2. resolve `source_ref` (§2.2) if not client-supplied.
3. insert into `writer.db` (server-assigned `annotation_id`, `created_at`).
4. **emit** the notification (§4); capture success as `notified` in the response
   (fail-soft — a failed emit never fails the persist).

## 4. The emit bridge (the novel part — needs agentic-journal agreement)

An annotation becomes a notification to the owning agent. We surveyed the three
fleet mechanisms (grounded in their source):

| Mechanism | Emit entrypoint a Django handler can call | Caller must be an agent? | Live-target required? |
|---|---|---|---|
| **scitex-todo card events** | `scitex_todo.comment_task(card_id, text=…, by=…)` (public store API / MCP). The mutation auto-emits a `commented` card-event; the C4 dispatcher fans it into the owner's pull-inbox (`_events.py` → `_notify/_dispatch.py` → `_inbox.py`). | **No** — plain lock-guarded YAML write. | **No** — agent pulls at its own cadence via `poll_notifications`. |
| **scitex-agent-container a2a** | HTTP `POST /agents/<target>/message:send` (JSON-RPC `SendMessage`) to the target's `sac listen` server (`_listen/server.py`). | No, but needs the listen endpoint + any ACL token. | **Yes** — send fails (`delivered_subscriber_count==0`) if the agent is down/not-subscribed. |
| **claude-code-telegrammer** | `sendMessage(chat_id, text)` (Telegram Bot API). | No. | Addresses a **Telegram chat**, not an agent — wrong addressing model for "the agent that owns manuscript X". |

**Recommendation: emit via scitex-todo card events as the primary rail; treat
a2a as an optional low-latency accelerator.** Reasoning:

- The writer Django server is a **plain, possibly-non-agent process**. Only the
  scitex-todo rail lets such a process emit with **zero network coupling** and
  **no requirement that the target agent be live** at emit time — the exact
  properties this loop needs (the operator may annotate while the agent is
  asleep/rebooting). It is also already the fleet's single source of truth, so
  the annotation shows up on the operator's board for free.
- **Contract (proposed — for agentic-journal to ratify):** each manuscript maps
  to a **todo card** whose `agent`/`assignee` is the owning agent
  (`project == <manuscript-project>`, a stable `id` like
  `writer-annotations-<project>`, or a per-annotation child card). On POST, the
  handler calls `comment_task(card_id, text=<rendered summary>, by="scitex-writer")`
  where the summary is a one-line human-readable render:
  `"[annotation] p{page} {kind} @ {source_ref} — \"{text|…}\" (id={annotation_id})"`.
  The dispatcher delivers it to the owner's inbox; the agent sees it on its next
  `poll_notifications` and can act (edit the `.tex`/claim, then PATCH the
  annotation `status=resolved` to close the loop).
- **a2a accelerator (optional, phase 2):** when the owning agent's `sac listen`
  is reachable, additionally POST an a2a `SendMessage` for instant push. This is
  strictly additive; the card-event is the durable rail.

Open contract questions for agentic-journal (they own the pattern): the exact
notification body schema, one-card-per-manuscript vs one-card-per-annotation,
and whether `resolved` should reopen/close the card or only PATCH the row. **The
writer side is deliberately kept behind a one-function seam
(`scitex_writer._annotations.emit(annotation)`) so the chosen mechanism is a
config/impl detail, not an API change.**

## 5. Cross-repo agreement points (sign-off needed before build)

1. **live-paper — annotation POST contract.** live-paper's viewer must POST to
   writer's `/api/annotations` with the §2.1 shape: page, **normalized** region
   rect, kind, payload, and (crucially) any **hotspot hit** (claim/figure id the
   viewer knows the rect covers). Agree the exact JSON and the mount mechanism
   (iframe postMessage vs same-origin fetch) per card
   `live-paper-absorb-writer-pdf-viewer-d-adopt`.
2. **live-paper — geometry basis.** Confirm coords are normalized 0..1 in
   **PDF-page** space (not CSS-pixel/zoom-dependent), and that the viewer reports
   the `build_id`/PDF identity the marks were drawn on, so writer's SyncTeX
   resolution is valid.
3. **writer ↔ live-paper — who resolves source.** Proposed: live-paper sends
   geometry + hotspot; **writer** resolves to claim/float/tex-line (§2.2).
   Confirm live-paper is willing to expose hotspot hit-testing (or that writer
   does all resolution from raw geometry via SyncTeX).
4. **agentic-journal — notification rail + body schema.** Ratify scitex-todo
   card events as the rail (vs a2a), the card-per-manuscript vs card-per-mark
   model, the notification body schema, and the resolve/close semantics (§4).
5. **all three — annotation identity & lifecycle.** Who owns `annotation_id`
   allocation (proposed: writer, server-side), and the `open→resolved`
   round-trip (agent resolves → PATCH → does the annotation disappear from the
   viewer? live-paper must re-read).

## 6. Incremental build plan

Smallest useful spike first; each step is independently shippable and CI-gated.

1. **Spike 0 — persist + emit, one text-comment, NO UI.** Add
   `scitex_writer._annotations` (SQLite via
   `local_state.runtime_path("writer","writer.db")`; single `annotations`
   table) and `handlers/annotation.py` with **POST + GET only**, `kind` limited
   to `text_comment`, `source_ref` = page-only (no SyncTeX yet). Emit via
   `comment_task` to a hard-agreed card id. Prove the loop end-to-end with
   `curl`/a test: POST a comment → it lands in the owning agent's
   `poll_notifications`. This validates §2.3 + §3 + §4 with zero live-paper
   dependency.
2. **Spike 1 — coords→source resolution.** Add the §2.2 resolver: SyncTeX
   (page,region)→(file,line), then claim-hotspot and float resolution. Still
   API-only (drive with synthetic geometry).
3. **Spike 2 — live-paper mount + capture.** Once §5.1–5.3 are signed, live-paper
   posts real annotations from its annotation layer through writer's Django shell
   (iframe/mount). Add `region_mark`, then `stroke`, then the
   `open→resolved` PATCH round-trip.
4. **Spike 3 — a2a accelerator + board polish (optional).** Add the low-latency
   a2a push alongside the durable card-event, and surface annotation status on
   the operator's board.

Ship Spike 0 behind the existing Django app with no viewer changes; it is the
concrete proof that unblocks the cross-repo conversation.
