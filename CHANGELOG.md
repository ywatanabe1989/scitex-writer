# Changelog

All notable changes to SciTeX Writer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.33.0] - 2026-07-14

### Fixed
- **The claims pane verified ZERO claims. Not some — all of them.** Writer called `verify_chain(target_file=...)` and `verify_chain(session_id=...)`. Clew's `verify_chain` takes a single positional `target` and has *neither* keyword, so **every** call raised `TypeError`. The exception was logged at **debug** and returned as a per-claim state of `"ERROR"` — so the pane told a researcher "this claim could not be verified" when the truth was "writer called Clew wrong". A wiring bug wearing the costume of a data problem. It shipped in 2.30.2 and had never once been run against a real Clew; **paper-scitex-clew found it in a real manuscript, where all 40 claims came back `ERROR`.**

  It now uses Clew's own per-claim entry point, `verify_claim(claim_id)` — which exists for exactly this, and which writer was reimplementing badly — and carries Clew's `details` through, so the pane can say *why* a claim failed rather than only that it did. A `session_id` alone is reported as `UNVERIFIABLE_NO_TARGET`: neither entry point accepts one, so claiming a verification we never performed was a second lie hiding under the first. A `TypeError` is now **re-raised**, never reported as a claim state — it is our call being wrong, not a fact about the claim.

  Also removes `claim.py`'s `except Exception: pass`, which left `clew_available=True` beside a silently empty DAG.

- **`update-project` refuses to vendor a stale engine and call it success.** It vendors from the **installed** scitex-writer, so an agent running an old version would quietly copy an old engine into their project and be told it worked — "fixing" staleness with staleness. Both neurovista and paper-scitex-clew were sent to run it with 2.29.0 installed while 2.32.1 was current; paper-scitex-clew caught it by hand and asked for the guard.

  When the source can be **proven** outdated it now refuses and hands back the command that works (`uv pip install -U 'scitex-writer[all]'`). When PyPI is unreachable it proceeds but **says the check did not happen** — `is_outdated` is `None`, never `False`. Silence must not read as "you are current". `--allow-outdated` overrides; an explicit `--branch`/`--tag` is a deliberate choice and is not second-guessed. Version comparison is numeric, because `"2.9.0" < "2.32.1"` is `False` as strings.

## [2.32.1] - 2026-07-14

### Fixed
- **The editor no longer says "scitex-app is not installed" when scitex-app IS installed.** The guard around `scitex_app.embed` catches two different failures — the package being absent, and the package being present but older than 0.4.0, the release that added `.embed` — and reported the first for both.

  Found by running the real entry point against a real environment that had **scitex-app 0.2.11** sitting right there. The remedy it offers (`uv pip install 'scitex-writer[all]'`) happens to fix either case, which is exactly why this survived: the message *worked*, so nobody checked whether it was *true*. But a user who reads "not installed", runs `pip show scitex-app`, and finds the package present concludes the message is lying and goes to debug something else. A wrong diagnosis costs more than a missing one. It now names the installed version and the version required.

## [2.32.0] - 2026-07-14

### Changed
- **Shell completion is imported from the public `scitex_dev.cli`, and the import is no longer guarded.** It reached into `scitex_dev._cli._completion` — a peer's *private* module, which that peer is free to move without warning. The public name is the promise, and `attach_shell_completion` is in `scitex_dev.cli.__all__` behind a deliberate lazy re-export, so there was never a reason to reach past it.

  The `try/except ImportError` around it is gone too. scitex-dev is a **hard** dependency of scitex-writer, not an optional one: if it cannot be imported, the install is broken and the right outcome is a loud `ImportError` naming the real cause. The guard turned that into a writer with silently missing completion leaves — a degraded CLI presented as a working one, which is the same defect as an extra that installs nothing. Raises the floor to `scitex-dev>=0.30.0`, the first release exposing the public re-export.

## [2.31.0] - 2026-07-13

### Changed
- **BREAKING: extras are ALL OR NOTHING.** The `editor`, `desktop` and `scholar` extras are removed; use `[all]`. There is no compatibility shim — this was an explicit call (near-zero users; fix it now rather than carry the wart).

  Fine-grained extras asked users to predict at install time which features they would later want, and writer got that wrong in the worst possible way: **`editor` was declared EMPTY (`editor = []`)** and scitex-app appeared in no dependency list anywhere — while `_server.py`, `apps.py` and the CLI all told anyone missing scitex-app to run `pip install scitex-writer[editor]`. **That remedy installed NOTHING.** The user ran the fix we handed them, stayed exactly as broken, and the editor kept serving without the workspace shell — while confidently naming the cure. An install instruction that resolves to a no-op is worse than no instruction, because the user believes they have already tried it.

  `[all]` now genuinely provides `pywebview` + `scitex-app>=0.4.0` + `scitex-scholar>=1.5.2`. The scitex-app floor is the first release exposing the public `scitex_app.embed` module; below it the import falls through the guard and the editor degrades. Every message, doc, skill, README — and the GUI Dockerfile, which was installing a retired extra — now names `[all]`. Tests read the real `pyproject.toml` and pin the contract: no extra may be empty, retired names stay gone, `[all]` must provide every feature module, and nothing may tell a user to install an extra that does not exist.

- **The browser tab leads with the brand: `SciTeX Writer`.** Four SciTeX tools open side by side showed four conventions — a version number in one title, a missing favicon, a rogue icon, and writer's `Writer — SciTeX`, the only one with the words backwards. The `(standalone)` marker stays: it is deliberate, since scitex-hub reads the same `SCITEX_APP_MODE` setting so the tab alone distinguishes hub-embedded from standalone.

- **Imports moved to the public `scitex_app.embed` surface** (from the private `_standalone` / `_django` paths).

### Fixed
- **`gui serve --force` now actually forces.** It refused when the port was held by *our own orphaned editor* — one that died without clearing its state file, so `status()` could not see it and `--force`, which only stopped the editor recorded in that file, did nothing. It then printed remedies that ignore `--force` entirely. A flag that names the fix and does not perform it is the same defect as an install hint that installs nothing. It now reclaims a holder it can **prove** is ours, decided from the process's **argv** rather than its name (a `comm` of `python` says nothing; the argv names the module). A process that is not ours is still never touched, and `--force` is only *offered* in a hint when it would actually work.

- **`port_holder` no longer blames the wrong party.** It reported "a process owned by another user" when the real answer was "this `/proc` will not let us look" — our own agent containers deny `/proc/<pid>/fd` even for our own uid. A confident wrong answer is precisely what this module exists to prevent; it now says so plainly.

- **`apps.py` no longer swaps its base class in silence.** Falling back to a plain Django `AppConfig` means losing the workspace shell — a real downgrade that left the editor looking installed and behaving differently, with nothing to explain why. It warns now.

## [2.30.2] - 2026-07-13

### Fixed
- **The live-paper viewer reported `NO_PROVENANCE` for every claim — including claims that had provenance and would have verified.** `list_claims` computed `has_provenance` from a claim's `session_id` / `output_file` and then DROPPED both fields from the projection it returned. `_claim_verification_state` verifies a claim by handing those pointers to `scitex_clew.verify_chain`; with nothing to hand it, it took its `if not (output_file or session_id)` branch every time and `verify_chain` was never reached for any claim. No exception, no log line — a confident wrong answer, the same shape as the port slide and the silent editor downgrade. The projection now carries `session_id` and `output_file`; the boolean stays for callers that only want the flag. (Recovered from a `rescue: pre-stop autosave` on an abandoned worktree branch that never got a PR — that draft patched the viewer to re-read `claims.json` behind `list_claims`' back and swallowed the reread in a bare `except Exception`, so it was rewritten to fix the source instead.)

## [2.30.1] - 2026-07-13

Follow-up to 2.30.0, from the operator using it: when the port collides, the error should tell you what to type.

### Added
- **`gui serve --force`** stops a previous editor **of ours** and takes the port back. It deliberately does **not** kill a process it does not own — that could be the operator's database — so for a foreign holder it prints the `kill` command and lets a human decide. For the same reason `--force` is not offered as a remedy when the holder is foreign: it would not work there, and a hint that does not work is the bug being fixed.

### Fixed
- **The "Held by:" hint silently disappeared in exactly the environment that needs it.** It shelled out to `ss`, which is not installed in a minimal container — so a port collision printed a bare "port in use" with nothing to act on, and the tool looked like it simply had nothing to say. `_gui_runtime.port_holder()` now reads `/proc/net/tcp` and `/proc/<pid>/fd` directly: no external tool, and it reports only processes the caller can actually see (an inode it cannot map to a pid is reported as another user's process rather than guessed at).

- **The remedies were prose, not commands.** Both refusals now print paste-ready lines — the port to retry on, and `kill <pid>` naming the actual holder — instead of describing what you might do.

## [2.30.0] - 2026-07-13

A sweep of one bug family: **a degraded outcome presented as a success.** A broken bibliography that still produced a PDF exited 0 under a green banner; a taken port slid quietly to the next one; a broken Django app downgraded the editor to a shell-less server without saying so. Each now either succeeds honestly or fails loud.

### Changed
- **The editor GUI binds one fixed port — 31298 — or fails.** `gui serve` used to call `_find_available_port()` and quietly bind the next free port when its own was taken, so a second launch left a stack of duplicate editors on drifting ports and no way to tell which one the browser had reached. It now binds exactly the requested port and refuses to start otherwise, naming the port, the process holding it, and the two remedies (`--port <other>`, or `scitex-writer gui stop -y`). Two guards, because they catch different things: the runtime state file catches *our own* server already running (a live pid makes the second `gui serve` refuse and print the running URL and pid instead of starting a rival), and the bind check catches an **orphan or a foreign process** holding the port. Stale state from a dead pid self-heals and serving proceeds. `31298` is writer's slot in the fleet-wide `3129X` scheme; the old `5050`/`5052`/`5057` defaults collided with figrecipe and are retired.

- **`scitex-scholar>=1.5.2`** is now the floor: it requires a real identifier before calling a citation verified, instead of accepting a lucky title match.

### Fixed
- **The editor no longer downgrades itself silently.** `_django/_server.run()` wrapped `django.setup()`, the `migrate` call, and the optional `scitex_app` import in a single `try/except ImportError: pass`. An ImportError from a broken app in `INSTALLED_APPS` was swallowed exactly like a missing optional dependency, and the editor came up as a bare runserver with no workspace shell — silently. The guard now covers only the optional import and announces the downgrade; `django.setup()` and `migrate` run unguarded, so their errors propagate.

- **A non-fatal bibtex error no longer destroys a perfectly good PDF.** One auto-generated scholar stub entry duplicated across two `.bib` files made bibtex report `Repeated entry`, `latexmk` exit 12 — and the compile script then ABORTED and DELETED a valid, complete 25-page manuscript PDF. The PDF stage now distinguishes the two things a non-zero engine exit can mean: **produced a PDF** (pdfTeX wrote `Output written on ... (N pages)` and the file exists with pages > 0) is PROMOTED to the output location with a loud warning; **produced nothing** (no PDF, or a zero-page husk) still FAILS LOUD exactly as before. A promoted-but-warned run is **not** reported as a clean pass: the compile scripts print a yellow `Compilation Complete — WITH WARNINGS` banner and exit **3** (a new, distinct code), and `run_compile()` returns `success=True, exit_code=3` with the warning at the head of `warnings[]` — after independently re-verifying pages > 0 in Python, so a shell claiming exit 3 without an artifact can never become a silent success.

- **Duplicate cite keys are de-duplicated before bibtex ever sees them.** `merge_bibliographies` now (a) runs even when `bibliography.bib` is the only `.bib` file — it used to be skipped entirely in that case, so a duplicate key *inside* it went straight to bibtex — and (b) merges `bibliography.bib` as an INPUT (`--include-output`) instead of regenerating it from the other `.bib` files, which silently DESTROYED every entry that lived only in `bibliography.bib`. Precedence is explicit: **a real entry beats a stub.** A stub is identified by scholar's own stamps (`note` = `Auto-generated stub`, `journal` = `Pending scitex-scholar metadata lookup`), imported from `check_citations.py` so there is one definition, not two. The real entry is the base; the stub may only fill fields the real entry lacks and never donates its stamps (previously "longest value wins" let a stub's 39-character `Pending ...` journal overwrite a real `Nature`). Two stubs merge normally and stay stamped, so the citation gate still catches them.

- **The bibliography merge test suite was silently skipping — all 55 tests.** `ROOT_DIR` was off by one (`tests/`, not the repo root), so `scripts/python` never landed on `sys.path`, the import raised `ImportError`, and a bare `except ImportError` turned the whole file into a skip. It is now imported at module scope: a real breakage FAILS instead of skipping.

## [2.29.0] - 2026-07-12

### Added
- **Citation-trustworthiness check.** Beyond "does the `\cite` key exist in the `.bib`", each citation is now resolved against CrossRef/OpenAlex/ArXiv/SemanticScholar (via `scitex-scholar`) and classified: a fabricated paper is flagged as **hallucinated**, an unresolvable one as **unverified**. Runs on the shared severity framework (`citation_trust`, default `warn` — a network-dependent check must not block a compile by default; override with `SCITEX_WRITER_CITATION_TRUST` or `config.yaml`). Surfaces as `scitex-writer check-citation-trust`, `checks.citation_trust()`, and in the pre-compile provenance stage. Verdicts are cached per cite-key + bib-entry hash, so an edited entry re-verifies but a hundred-citation manuscript does not re-hammer the network on every compile.

  **It never silently passes.** If `scitex-scholar` is absent, the network is down, or the resolver errors, the check says so loudly and reports *zero* passes — an un-runnable check is reported as un-runnable, never as "all good".

  **Scope limit, stated plainly:** a green result means *the citation resolves to a real source whose title and authors match*. It does **not** mean the paper is un-retracted or the venue is reputable — neither is checked. Do not read it as such.

### Changed
- Requires `scitex-scholar>=1.5.0` for the `scholar` extra. Earlier versions could **never** return a `verified` verdict for any citation (an upstream metadata-shape bug, found and fixed while building this check), so every citation — including correct ones — silently degraded to "unverified".

### Known gaps
- **arXiv DOIs (`10.48550/arXiv.*`) do not yet verify** — a correctly-cited arXiv paper currently classifies as `unverified`, so on ML/CS manuscripts the check is noisy where it is most needed. Fix is in flight upstream in `scitex-scholar`.

## [2.28.1] - 2026-07-12

**Upgrade from 2.28.0 and run `scitex-writer update-project`** — without it, 2.28.0's advertised engine fixes do not take effect.

### Fixed
- **The 2.28.0 engine fixes never reached a real compile.** `compile-manuscript` runs the vendored `scripts/shell/compile_manuscript.sh`, which still invoked `modules/process_{figures,tables,diff,archive}.sh` — so the pure-Python pipelines were reachable only through `tables render` / `figures render` / `compile diff` / `compile archive`, which nothing on the compile path calls. Every 2.28.0 user still got backend-dependent math escaping, multi-panel figures shipped as panel-a, no-op cropping, and diff-against-self. All three compile scripts (manuscript / supplementary / revision) now delegate those four stages to the installed Python engine through the new `modules/run_python_pipeline.sh` launcher, which FAILS LOUD (with a `pip install -U scitex-writer` hint) rather than falling back to the shell. Consumer projects pick this up with `scitex-writer update-project`.

### Changed
- A failing diff stage no longer aborts the compile: the Python diff engine refuses to diff a version against itself, so on a project with no previous version the stage now reports the refusal loudly and the manuscript PDF still ships.
- `modules/process_{figures,tables,diff,archive}.sh` are now DEAD (nothing invokes them) but are kept in the tree for one release cycle; they are marked SUPERSEDED in their headers.

## [2.28.0] - 2026-07-12

The compile engine is now **pure Python**. All five shell modules were ported, each verified by *real* `pdflatex`/`latexmk` compiles rather than by inspection. The port surfaced four bugs that had been failing **silently** — every one of them survived because the shell's own tests asserted nothing (one test file printed `TODO` and passed).

### Fixed
- **Tables shipped different output depending on the machine.** The shell picked among four CSV→LaTeX backends (`csv2latex` binary, pandas, bare Python, AWK) by probing the host, but the whole-cell verbatim passthrough existed only in the pandas branch — so on a machine with `csv2latex` installed, an authored `$p<0.001$` was silently escaped. Collapsed to one pandas backend, making the loss structurally impossible. (#296)
- **A cell mixing prose and math silently ate the row.** `5% ($p<0.05$)` is verbatim (it holds `$`), so its `%` passed through bare — and a bare `%` comments out the rest of the LaTeX row, swallowing the row terminator and the next row with it. `%` and `&` are now escaped inside verbatim cells; math characters still pass through. (#297)
- **Multi-panel figures shipped as their first panel — and logged success.** `copy_composed_jpg_files` copied panel *a* as the "composite" under a `# For now, just copy the first panel as placeholder` comment, then printed `Created composed figure`. The real tiler scanned a directory that never holds panels. Panels are now genuinely tiled with Pillow. (#298)
- **Figure cropping silently did nothing.** The shell's `magick`/`convert`/`mogrify` cascade fell through every rung when ImageMagick was absent, with no error. Replaced by Pillow. (#298)
- **The version diff could be taken against itself.** With no previous version in git history the shell diffed the manuscript against its own current text, shipping an unmarked PDF indistinguishable from "nothing changed since the last version". Now a loud, actionable error. (#299)

### Added
- **Pure-Python engine pipelines** with fail-loud result dataclasses, exposed on all three surfaces (Python API / CLI / MCP): tables (#296), figures (#298), diff + archive (#299). Missing binaries (LibreOffice, `mmdc`, `latexdiff`) now fail with install hints instead of leaving an output silently missing.
- `compile diff` / `compile archive` CLI leaves, with matching `writer_compile_diff` / `writer_compile_archive` MCP tools.

### Removed
- Dead shell paths, refused rather than ported: an optimisation stage that invoked a script which does not exist (so it never ran), an unreachable git-identifier branch, and a dead panel-tiling checker.

## [2.27.0] - 2026-07-11

### Added
- **PDF annotation bridge (editor ↔ backend).** Annotations drawn on the PDF pane (pen strokes, rects, comments) now POST to the backend persist+notify rail, so agents can consume spatial feedback ("here, this spot") from the reviewer (ADR 0001). (#286)
- **`gui` command group** per the fleet CLI canon: `gui open` (auto-starts a detached server, then opens the browser), `gui serve` (foreground), `gui status`, `gui stop` (`--dry-run`/`--yes`, refuse-without-yes). Server state persists at `<scope>/.scitex/writer/runtime/gui.json` with stale-state self-heal, so status/stop work from any shell. (#287)
- **`list-engines` verb** — Python port of the LaTeX engine detection (tectonic / latexmk / 3-pass). (#285)

### Changed
- `launch-gui` is deprecated (hidden warn-forward alias for one cycle); use `gui open`.

### Fixed
- **clew provenance wording fails loud when missing** instead of being invented. (#283)

## [2.26.1] - 2026-07-08

### Fixed
- **Broken wheels 2.18.0–2.26.0: `import scitex_writer.writer` failed on clean installs.** The sdist `exclude` pattern `"config"` was unanchored, so hatchling (gitignore semantics) also dropped `src/scitex_writer/_dataclasses/config/` — every published wheel since 2.18.0 shipped without `WriterConfig`, raising `ModuleNotFoundError` on a fresh `pip install`. Anchored all `exclude` patterns to the repo root (`"config"` → `"/config"`, etc.) so they only match the intended top-level scratch dirs. Surfaced during a scitex.ai prod outage (hub visitor-slot clones); reported by scitex-hub.

### Added
- **Release CI gate: wheel-from-sdist import smoke.** The publish workflow now builds the sdist, builds a wheel *from that sdist*, installs it into a clean venv, and asserts `import scitex_writer.writer` — so a wheel missing packaged submodules can never publish again. (The pre-existing `import-smoke` used `pip install -e .`, which installs from the source tree and structurally cannot catch a broken sdist.)

## [2.26.0] - 2026-07-07

### Added
- **Clew provenance overlay (`--clew-overlay`).** New compile toggle (manuscript/revision/supplementary) that colors each claim span by its clew verification verdict (verified/suspect/failed/exception) with a 4-state legend, aliasing onto the `SCITEX_WRITER_CLEW_PRESENTATION` master switch; `\vclaim` marks light up from the clew join with zero author edits, degrading loud-but-graceful when no clew feed is present (#262).

## [2.25.1] - 2026-07-07

### Fixed
- **Breakable placeholder-caption edit-path.** The scaffolded placeholder-caption
  edit-path is now wrapped in a breakable `\url{}` to prevent an Overfull `\hbox`
  off-page overflow (#259).

## [2.25.0] - 2026-07-06

### Added
- **PDF annotation → agent feedback loop (design doc).** Design for a loop
  that turns PDF annotations into actionable agent feedback (#247).
- **Opt-in page-footer signature.** A visible "SciTeX Writer" page-footer
  signature, disabled by default (#248).
- **Annotation persist + emit spike.** The writer-owned slice of the
  annotation→feedback loop: persist annotations and emit them (#249).
- **Self-documenting vendored tree.** The vendored tree now carries role
  hint-comments and is set read-only via `update-project` (#250).
- **`\captionfootnote` helper.** A footnote-in-caption marker that expands to
  `\footnotemark` + `\footnotetext` placed after the float (#251).
- **Combined supplement↔main compile target.** `compile.sh all` / `-a` compiles
  supplement and main together in one pass for cross-ref resolution (#252).
- **Pre-compile reference-integrity gate.** Runs by default at `warn`, escalates
  to `error` in research projects (`project-type: research`); `off` disables —
  an opt-out model (#254).
- **Auto-run overflow check after each compile.** A new post-compile "Overflow
  Check" stage runs automatically (#255).
- **Table-decimal consistency warn-lint.** Covers the non-pandas /
  external-`csv2latex` / hand-authored table paths the auto-pad misses (#256).

### Changed
- **Compiled-PDF signature branding.** The compiled-PDF signature now displays
  "SciTeX Writer" rather than the lowercase form (#253).

## [2.24.9] - 2026-07-06

### Added
- **`list-deps` command.** `scitex-writer list-deps --apt` prints the system
  (apt) packages scitex-writer needs, so an environment can be provisioned from
  a single authoritative list (#244).

### Fixed
- **`scitex-writer --version` prints its own version.** The flag was shadowed by
  scitex-dev and reported the wrong package version; it now reports
  scitex-writer's own version (user-facing regression fix, #243).
- **Fail loud on a missing figure at compile time.** A referenced figure that is
  absent now hard-fails the compile instead of silently producing an incomplete
  PDF (#242).
- **Stale-PDF freshness guard.** The compile step now fails loud when the output
  PDF was not actually (re)created, so a stale PDF can never masquerade as a
  fresh build (#241).
- **`render_clew` resolves the git root correctly.** clew rendering now anchors
  to the repository root regardless of the working directory (#240).

## [2.24.8] - 2026-07-06

### Added
- **Pure-Python `count_words` and `citation_style` (Python + MCP).** The two
  remaining shell-port slices now have native Python implementations exposed as
  MCP tools, and the previously-unregistered `checks.py` MCP tools (slice 3, 6
  tools) are wired into the engine — the manuscript-checks surface is now fully
  callable from Python/MCP without shelling out.
- **Interactive inline manuscript hints.** The Details pane gains click-to-jump
  hint rows: latex-log `\ref`/`\cite` hints carry a resolved `location.line`, so
  a hint links straight to the offending manuscript line. Backed by a
  multi-producer, merge-by-source findings feed (`write_feed`), a compile-stage
  API endpoint, and a Details-pane Notifications section (the dynamic-paper data
  layer).
- **Controlled inline figure placement (`\scitexfig{<number>}`).** Figures
  collect in the end "Figures" section by default; to place one in the main
  text at a controlled spot, drop `\scitexfig{01}` where you want it — it
  renders that figure's float there and flags it so it is not also repeated at
  the end. Figures left unplaced still collect at the end (default behaviour
  unchanged). The assembler now writes per-figure standalone floats to
  `contents/figures/compiled/_placeable/<number>.tex` and guards each end-block
  float with `\ifcsname scitexfigplaced@<number>\endcsname`.
- **Controlled inline table placement (`\scitextab{<number>}`).** Same model
  for tables: `\scitextab{01}` renders that table where dropped and skips it in
  the end "Tables" section; unplaced tables still collect at the end. The table
  assembler writes number-keyed placeable copies and guards the end-block input
  with `\ifcsname scitextabplaced@<number>\endcsname`.
- **clew page-1 legend toggle (`legend_first`).** Opt-in one-key toggle to render
  the clew legend on page 1, wired through env var + `.scitex` config; the
  `render_clew_toggles` step emits `\clewpres*` marks from the config.
- **Citation banner + clew-verified render.** A page-1 red citation banner keyed
  to a configurable citation level, plus inline `\clewcite` (citation) and
  `\clewfig` (figure) marks. The compile step now emits `clew_rendered.tex` from
  the clew runtime `claims.json`, stamps the clew tool version onto the
  provenance attestation (read from `attestation.version`), and aligns the clew
  palette to the SciTeX-standard dark/light colors. `render_clew` tolerates the
  clew 0.2.19 / unified 1.5 / 1.6 schemas.
- **Exact undefined-reference reporting.** The post-compile check now lists the
  precise undefined `\ref`/`\cite` keys instead of a generic warning.

### Changed
- **CLI monolith split.** The `_cli` monolith was refactored into per-command
  modules to clear the line-limit, with backward-compat group re-exports
  preserved.
- **`findings` renamed to `hints`.** Operator naming decision, applied across the
  UI surface.
- **`process_tables.sh` split** — the CSV→LaTeX generation functions
  (`csv2tex`, `csv2tex_single_fallback`, `csv2tex_fallback`) were extracted
  verbatim into `process_tables_modules/03_csv2tex.src` (sourced by the
  orchestrator) to keep the file under the size limit; no behaviour change.

### Fixed
- **latexmk empty-aux / stale-aux handling.** `\readwordcount` now tolerates a
  missing file (no emergency stop), and the build forces a clean `latexmk -gg`
  run so bibtex never reads a stale `.aux`.
- **Word count never emits an empty value** — an empty count made `siunitx`
  fatal; it now always emits a number.
- **Stray "Table 0" / "0tables" artifact suppressed** when a manuscript has no
  tables present.
- **Hard compile-timeout ceiling enforced by default** (fail-fast) so a runaway
  compile can't hang indefinitely.
- **CI / audit gate fixes** — resolved the `--new-only` base-ref mismatch, dropped
  a forbidden monkeypatch in clew-version tests, and moved `_system_deps.py` into
  `_core/` to clear the PS-108b flat-file threshold.

## [2.24.7] - 2026-07-01

### Added
- **Citation gate (`check_citations.py`) — fail the build on unresolved scholar
  stubs.** A new pre-compile check (in the `run_provenance_checks.sh` roster)
  scans the manuscript's `\cite` keys and fails when a cited reference is an
  auto-generated scholar stub (`note` contains "Auto-generated stub" or
  `journal` contains "Pending scitex-scholar metadata lookup"). A stub citation
  can never reach a compiled research manuscript. Defaults to **error** for
  research projects (`.scitex/dev/config.yaml project-type: research`), **warn**
  otherwise; overridable via `citations.level` / `SCITEX_WRITER_CITATIONS` /
  `--level`. It reads the bib that bibtex actually reads: the
  `\bibliography{}`/`\addbibresource{}` target resolved relative to the tex and
  **symlink-followed** (real trees point `contents/bibliography.bib` at a
  possibly-legacy enriched bib, not `00_shared`). "No DOI" is deliberately NOT a
  stub trigger (books/arXiv/conference refs legitimately lack one) — surfaced as
  info only, to avoid false positives. This is the compiler-owns half of the
  citation→clew verification contract; the clew-verified half slots in behind
  the same report once scitex-clew defines its batch lookup.

## [2.24.6] - 2026-07-01

### Fixed
- **Compile no longer discards a valid PDF over a non-fatal bibtex/latexmk
  exit.** `latexmk` returns non-zero (exit 12) on a *non-fatal* bibtex warning
  (e.g. a malformed/stub `.bib` entry → "repeated entry" / "I'm skipping
  whatever remains of this entry") even when pdfTeX finalized a complete PDF.
  `cleanup()` treated any non-zero exit as fatal, deleted the just-produced PDF,
  and aborted — losing a valid multi-page PDF over one stub reference. It now
  promotes a PDF that was *freshly produced this run* (present in `logs/`) with
  pages > 0 — read from pdfTeX's per-run `"Output written on … (N pages"` log
  line (immune to a stale PDF), with a `pdfinfo` fallback — and downgrades to a
  WARN pointing at `logs/*.{log,blg}`. The fail-loud-on-no-PDF guarantee
  (2.23.1) is preserved: a stale PDF can never be mistaken for new output.
- **Bibliography merge now de-dupes by cite key.** `deduplicate_entries`
  matched only on DOI and (title, year); a stub entry duplicated across input
  `.bib` files (same cite key, no DOI, differing/absent title) slipped through
  twice → bibtex "repeated entry" → dropped reference. Cite key (entry `ID`) is
  now the first dedup key, since a repeated cite key is exactly what breaks
  bibtex.
- **Flattener injections are idempotent on reflatten.** A repeated
  `--dark-mode` compile re-runs the flattener on content that already carries
  the injected blocks; the dark-mode and build-id (`_build_id`) injections both
  matched the first real `\begin{document}` every run and stacked a second copy
  (duplicated dark-mode override → `\REDENDS`/`\hlref` undefined + stray
  `\begin{document}`). Both are now guarded by a unique sentinel so a second
  flatten is a no-op.

## [2.24.5] - 2026-07-01

### Fixed
- **Flattener no longer injects before a `\begin{document}` that appears inside
  a comment.** The build-metadata (`_build_id.inject_build_metadata`) and
  dark-mode injections targeted `\begin{document}` with a plain `str.replace`,
  which also matched the literal inside a preamble *comment* (e.g.
  `clew_presentation.tex`'s "overridable before `\begin{document}`"). With the
  clew layer active this injected the dark-mode override block mid-preamble —
  before the base `\newcommand`s (`\REDENDS`/`\hlref` undefined) — and
  de-commented the comment tail (`\begin{document}) ---` emitted as code →
  "Missing \begin{document}"), producing ~25 LaTeX errors + page-1 garbage on a
  reflatten. Both injections now anchor to the real line-start `\begin{document}`
  (first match only), so a `\begin{document}` inside any comment is ignored.
- **Clew colophon/signature no longer crashes the compile when the icon asset
  is absent.** `\clewColophonIcon` guarded `\includegraphics{\clewSigIcon}` with
  `\IfFileExists{\clewSigIcon}{…}{}`, but the bare macro could reach the test
  unexpanded (texlive vintage / flattened context), so the false branch never
  fired and a missing `\clewSigIcon` (default `docs/scitex-icon-navy-inverted.png`,
  not vendored) hard-failed with `File \`\clewSigIcon ' not found` whenever the
  signature/colophon was enabled (`\clewpressignaturetrue`). The path is now
  force-expanded to a literal before `\IfFileExists`, so an absent icon degrades
  to a text-only colophon instead of crashing.

## [2.24.4] - 2026-07-01

### Added
- **Fail-loud guard against compiling on a Spartan HPC login node.** Running
  the TeX toolchain (pdflatex/bibtex/latexmk) on a Spartan login node is
  prohibited heavy compute (admins kill it; the account can be sanctioned).
  `compile_{manuscript,supplementary,revision}.sh` now abort early
  (`check_spartan_login.sh`) when on a `spartan-login*` host with no
  `SLURM_JOB_ID`, printing the `srun … bash scripts/shell/compile_manuscript.sh`
  pattern (and the `spartan-tex` helper) instead of a misleading "pdflatex
  missing"/`127`. The check is hostname-based, so it catches absolute-path
  `pdflatex` invocations that slip past command-name guards; it is a no-op
  everywhere else and adds no SLURM coupling to the portable engine (HPC
  incident 2026-07-01, coordinated with scitex-hpc).

## [2.24.3] - 2026-07-01

### Fixed
- **`claims_rendered.tex` is regenerated fresh on every compile (no stale
  `\vclaim` values).** The shell compile path (`compile_{manuscript,
  supplementary,revision}.sh`) never regenerated `00_shared/claims_rendered.tex`
  from `00_shared/claims.json` (the `\vclaim` value SSoT), so a stale or
  hand-edited file — e.g. a legacy "CLEW PROTOTYPE" block — could ship outdated
  values into the PDF. A new "Claims Render" pre-flight stage (`render_claims.sh`
  / `render_claims.py`) now regenerates it before flattening: a no-op when
  `claims.json` is absent, and **fail-loud** (non-zero) when it exists but
  rendering errors. The MCP compile path's `_auto_render_claims` no longer
  swallows render failures silently — it raises, so a broken `claims.json` can
  never silently produce a stale `claims_rendered.tex` (#205).

## [2.24.2] - 2026-06-30

### Fixed
- **Figure assembler no longer destroys user-placed jpgs.** `init_figures`
  previously ran a blanket `rm -rf jpg_for_compilation/*` at the start of every
  figure run, silently deleting real figures materialized directly in
  `jpg_for_compilation/` that have no `caption_and_media/` source to regenerate
  from (they became 9KB "Missing Figure" placeholders → PDF embedded 0 images).
  The clean step now removes only derived **symlinks** (re-created from
  `caption_and_media/` each run) and preserves real files, warning about any
  orphan jpg so it can be moved to `caption_and_media/` as a tracked source.

## [2.24.1] - 2026-06-30

### Fixed
- **Clew presentation layer was broken in 2.24.0.** 2.24.0 shipped only the
  initial cut of the clew layer; the follow-up fixes were stranded on the
  feature branch (the PR merged at the first commit). 2.24.1 lands the real
  layer: the 4-state taxonomy (verified / suspect / unverified / exception),
  verdict-colored `\uwave` markers (the `soul \hl` that swallowed values +
  dumped raw `@decorate` text is gone), line-breakable `\clewval`, the
  self-demonstrating legend, the attestation + explainer, and — critically — a
  **flattener-safe load** (plain top-level `\input` instead of an
  `\IfFileExists` wrapper, which the flattener inlined as a macro-argument body
  and dumped as raw text).
- **`update-project` re-stamps `00_shared/scitex_writer_version.tex`** to the
  vendored version, so the "Compiled by SciTeX Writer" colophon + PDF Creator
  metadata are correct immediately after a re-vendor (no recompile).

### Added
- **Pre-compile version-freshness gate.** `update-project` stamps the
  vendored-from version into `00_shared/.scitex-writer-vendored-version`;
  `check_version_freshness.py` fails loud when the vendored engine is behind
  the installed scitex-writer. `SCITEX_WRITER_VERSION_FRESHNESS`, default
  error. Prevents the silent stale-engine class of bug.

## [2.24.0] - 2026-06-30

### Added
- **Clew provenance layer (opt-in rendering).** `00_shared/latex_styles/clew_presentation.tex`
  renders clew-registered claims inline: `\clewval{id}` substitutes the
  registered value (SSoT) with a verdict-colored wavy underline, `\clewmark{id}{text}`
  marks prose, plus a "Clew Verified" badge, a "Compiled by SciTeX Writer."
  colophon (snake icon), and a self-demonstrating legend. 4-state palette
  (verified / suspect / unverified / exception); writer owns the *rendering*,
  scitex-clew emits the *data* (`00_shared/clew_rendered.tex`). All four
  features are independent opt-in toggles, default off (#192).
- **Pre-compile clew provenance gate.** `check_clew_verify.py` re-verifies every
  clew-registered claim against its bound source before compiling; default
  `error` for research projects, with a `require_claims` tightening knob
  (`SCITEX_WRITER_CLEW_VERIFY`) (#191).
- **Post-compile verification gate (fail loud on a deficient PDF).** A new
  "Compile Verification" stage fails the compile non-zero when the compiled
  `.tex` references `\includegraphics` (N>0) but the PDF embeds 0 images — a
  silent figure-miss that a clean log would not catch — plus secondary log
  deficiency signals (`SCITEX_WRITER_COMPILE_ARTIFACTS`, default error) (#194).

### Fixed
- **Fresh-checkout compiles no longer silently break.** The flattener now
  resolves preamble style `\input`s against `00_shared/latex_styles` when
  absent from `contents/` (the dev symlink is not committed), and FAILS LOUD if
  a preamble style is still missing — instead of emitting `% SKIPPED` and
  producing a broken PDF on exit 0 (#193).

## [2.23.1] - 2026-06-29

### Fixed
- **Compile now FAILS LOUD when no PDF is produced.** `compile_{manuscript,
  supplementary,revision}.sh` invoked the PDF-generation stage without checking
  its exit code, so a pdfTeX Fatal error that produced no PDF still exited 0
  (only printing an `ERRO:` line). Each now propagates the non-zero result and
  aborts, so a missing/failed PDF can never be mistaken for success (#188).
- **`microtype` no longer breaks elsarticle.** Font expansion is fatal on
  non-scalable fonts ("auto expansion is only possible with scalable fonts" →
  no output PDF); loaded now as `[protrusion=true,expansion=false]` (#188,
  regression from #187).
- **png→jpg figure conversion: Pillow fallback + fail-loud.** When ImageMagick
  is absent the converter now falls back to Pillow, and fails loud if neither
  backend exists, instead of emitting a `.txt` placeholder that broke
  `\includegraphics` (#184).
- **Per-column table decimal alignment.** csv→LaTeX aligns each numeric column
  to a consistent precision (`0.35` → `0.350` alongside `0.333`; integer-valued
  cells pad in a fractional column; all-integer columns stay bare). Default
  caption no longer title-cases the name (acronyms survive) (#185).
- **Supplementary `S`-prefixed numbering by default** (Figure S1, Table S1) via
  the `02_supplementary` template (#186).

### Added / Changed
- **Preamble defaults**: `microtype` (protrusion) + `\emergencystretch` and
  full-width **justified captions** (light + dark mode) in the shared styles;
  CSV table-header convention documented (#187).

## [2.23.0] - 2026-06-29

### Added
- **Unified pre-check severity framework — all 8 checks on one shared resolver.**
  New stdlib-only `scripts/python/_severity.py::resolve_level(...)` is the single
  source of truth for a check's effective level, resolved by the documented
  precedence (CLI `--level` > per-check `SCITEX_WRITER_<CHECK>` env > project
  `./config.yaml` `<check>.level` > user config > per-check default), with two
  tightening-only overlays: the legacy `strict` alias and `SCITEX_WRITER_LINT_STRICT`
  (scoped to `limits`+`overflow`). `repair` is honored only for `paper_symlink`.
  Adopted across `limits`, `overflow`, `paper_symlink`, `media_provenance`,
  `caption_footnote`, `ref_integrity`, `references`, `float_order`. Per-check
  defaults preserved (back-compat exact); see
  `docs/03_DESIGN_SEVERITY_MODEL_CONTRACT.md` (§9 ratified). `references` and
  `float_order` gain an `--level`/env severity knob (default stays `error`); a
  config `level: off` (which YAML coerces to bool) is honored, with a loud hint
  on a genuinely invalid value (never crashes the build).
- **Reference-integrity pre-compile gate** (`scitex-writer check-ref-integrity`,
  `checks.ref_integrity()`): validates figure/table `\ref`, `\cite`-in-bib, and
  `supple-` xrefs (with explicit "supplement not compiled" messaging), reports all
  at once. Default `error`; env `SCITEX_WRITER_REF_INTEGRITY`.
- **`\footnote`-in-`\caption{}` lint** (`check-caption-footnote`,
  `checks.caption_footnote()`) — errors by default on a fatal footnote inside a
  caption argument. Env `SCITEX_WRITER_CAPTION_FOOTNOTE`.
- **Shared-metadata single source of truth.** Title, authors, journal name, and
  keywords are now sourced from `00_shared/` by the manuscript, supplementary,
  AND revision builds (diffs inherit via `latexdiff`), so they can never drift.
  `00_shared/title.tex` exposes `\scitexmanuscripttitle`; the supplementary title
  derives from it (`Supplementary Material for: <title>`). `00_shared/{title,
  authors,...}.tex` are consumer-owned (preserved on re-vendor).

### Fixed
- **`lineno`↔`siunitx` frontmatter error.** Load `lineno` before `siunitx` so a
  `siunitx` "Invalid number" no longer aborts at `\end{frontmatter}`.
- **bibtex not re-run on a `.bib`-only edit (stale `.bbl` → wrong PDF).** The
  bibliography-merge step clears a stale `.bbl`/`.fdb_latexmk` when any source
  `.bib` is newer, forcing bibtex to regenerate.
- **Supplement cross-references rendered as `?`.** The supplement `.aux` is now
  exposed at doc-root (after the cleanup stage) so `xr-hyper` resolves `supple-`
  refs from the main document.
- **Dark-mode table zebra stripe was illegible.** The csv→LaTeX converter emits
  `\rowcolor{lightgray}` (the theme color, dark-aware: gray 0.95 light / 0.2 dark)
  instead of a literal `gray!10`, so striped-row text stays readable in both modes.

## [2.22.0] - 2026-06-26

### Added
- **System-deps provider (SSoT for LaTeX apt packages).**
  `scitex_writer._system_deps:provide()` is registered as a
  `scitex_dev.system_deps` entry-point, so the ecosystem aggregator and
  container image builds install scitex-writer's LaTeX toolchain from a single
  source of truth instead of a hand-maintained list. Declares the texlive set
  (base/recommended/extra, fonts-recommended/-extra, science, pictures,
  publishers, luatex, xetex, bibtex-extra, lang-english, plain-generic) plus
  `latexmk`, `latexdiff`, `chktex`, `texlive-extra-utils`, `parallel`, and
  `biber`. Standalone emit: `python -m scitex_writer._system_deps`.
- **`biber` available alongside bibtex.** bibtex/natbib remains the default
  bibliography path; `biber` is now in the dependency set so biblatex-based
  manuscripts compile out of the box (opt-in per project; not the default).
- **`media-provenance` check** (`scitex-writer check-media-provenance`, also
  `checks.media_provenance()`) — flags figure/table media in
  `caption_and_media/` that are raw files rather than symlinks generated from
  `scripts/`. Severity (`off`/`warn`/`error`) and the `require_under_scripts`
  strict mode are config-driven; default is `off`.

### Changed
- **Provenance/symlink checks are now enforced at compile time.** Both the
  shell compile gate (`compile_{manuscript,supplementary,revision}.sh`) and the
  Python `validate_before_compile()` API path run `paper-symlink` and
  `media-provenance` at their configured severity before any pdflatex work:
  `off`/`warn` never block, `error` aborts the compile (fail-loud). Previously
  setting a check to `error` was a silent no-op at compile time.
- **`paper-symlink` default severity is now `warn`** (was `off`), so a drifted
  `paper` link surfaces by default without blocking.

### Fixed
- **latexmk engine swallowed its real exit code.** `compile_with_latexmk` read
  `$?` after a `latexmk ... | grep` pipe, capturing grep's exit (always 0 when
  there is output) instead of latexmk's. A failed build reported success and
  `cleanup()` kept the stale PDF. It now propagates latexmk's real exit code, so
  broken builds fail loud and the stale PDF is removed.
- **Container/compile honesty + fail-loud.** A missing or broken `yq`, or an
  unavailable pre-built container, now fails loudly with hints instead of
  cascading from empty paths or silently using a stale artifact.
- **csv→LaTeX rendering** preserves acronyms and inline math: dropped forced
  title-casing and passes values containing `$`/`\` through verbatim.

### Docs
- Recorded writer skill learnings (dark-mode caveat, fail-loud compile,
  check-severity env vars) and a shared severity-model contract proposal.

## [2.21.0] - 2026-06-25

### Added
- **`paper` symlink check** (`scitex-writer check-paper-symlink`, also
  `checks.paper_symlink()`) — detects when the top-level `paper` convenience
  link to `.scitex/writer` has drifted into a real directory (two diverging
  manuscript copies). Severity is a user-level knob (`off`/`warn`/`error`/
  `repair`) read from `SCITEX_WRITER_PAPER_SYMLINK` or
  `~/.scitex/writer/config.yaml`. Repair never destroys diverged content — a
  divergent `paper/` directory is preserved (backed up) and only converted with
  an explicit `--force-after-backup`.

### Fixed
- **`update-project` no longer copies the package's own source into your
  project** — it previously vendored the entire `scitex_writer` Python package
  (thousands of files) into every consumer project, which made the updater
  unusable for re-syncing. It now syncs only the engine/template files
  (scripts, build scripts, `base.tex`, styles, `Makefile`).
- **Compile dependency check no longer hangs when a container image cannot be
  downloaded** — in a restricted or offline shell the check used to stall
  forever trying to pull a TeX/Mermaid/ImageMagick container. Pulls are now
  time-boxed (`SCITEX_WRITER_CONTAINER_PULL_TIMEOUT`, default 300s) and fail
  loud with hints (install natively, pre-build the container, or raise the
  timeout) instead of hanging.

## [2.20.0] - 2026-06-23

### Added
- **Drift detection in `update-project`** — the update command now compares a
  project's active, compiled style files
  (`01_manuscript/contents/latex_styles/*.tex`, and the supplementary and
  revision equivalents) against the template and reports any that have drifted,
  so a project whose engine files fell behind can be brought back in line. Safe
  by default: it previews changes unless you pass `--yes`, backs up every file
  it replaces, and refuses to run on a project with uncommitted changes unless
  you pass `--force`.

### Fixed
- **Release automation no longer depends on the `gh` command-line tool** — the
  step that creates the GitHub release page now uses a built-in release action,
  so it succeeds on build servers that do not ship that tool. Previously the
  package published to PyPI but the GitHub release page was silently skipped.

## [2.19.0] - 2026-06-22

### Added
- **Config-driven section/reference limits** with a fast pre-compile gate. New
  `limits:` block in `config/config_manuscript.yaml` (per-IMRD word caps +
  reference cap) enforced by `scripts/python/check_limits.py` inside
  `validate_before_compile` (runs before any pdflatex pass). Warn-by-default;
  `--strict` / `limits.strict` / `SCITEX_WRITER_LINT_STRICT=1` promote breaches
  to errors (non-zero exit). Exposed via `checks.limits()` and the
  `scitex-writer check-limits` CLI.
- **`theme: light|dark` config knob** resolved in `compile_tex_structure.py`
  (precedence: CLI flag > env > config > light; invalid value fails loud).
- **Duplicate-heading detector** (`scitex-writer check-references`): flags a
  `\section` title rendered twice in the compiled manuscript (e.g. "Figures").

### Fixed
- **Wide tables no longer overflow / vanish**: figures cap `\includegraphics`
  height at `figures.max_height_frac` (default `0.78\textheight`,
  `keepaspectratio`) so captions keep their space, and wide tables shrink-to-fit
  via a shrink-only `\resizebox` in the Python/MCP table paths.
- **Duplicate "Figures" heading** when a manuscript has no figures: the
  generated fallback header no longer emits its own `\section*{Figures}`
  (base.tex is the single source).
- **Word-count thousands separator**: counts render as `1,259` (was `1259`).

## [2.18.0] - 2026-06-21

### Changed
- **Reconcile `develop` and `main` into a single 2.18.0 release.** `develop`'s
  single-seam `_compile` design (`run_compile(..., command_runner=...)`) and its
  no-mocks `_compile` test suite are the canonical implementation; `main`'s
  parallel 4-seam rewrite (`runner_fn`/`validator_fn`/`output_finder_fn`/
  `script_resolver_fn`) is dropped. The develop test suite covers every
  behavioral scenario the main suite exercised (renamed/consolidated), minus the
  signature-introspection tests that were specific to the dropped 4-seam design.

### Added (salvaged from `main`)
- **Mermaid crash-early precheck** (`_utils/_mermaid_precheck.py`,
  `check_mmdc_or_raise`): fail loudly with an actionable message when `mmdc`'s
  headless-Chromium dependency is broken (missing `libnspr4` under apptainer)
  instead of SIGSEGV-ing mid-compile (#132).

### Fixed (salvaged from `main`)
- **Packaging:** `[tool.hatch.build.targets.sdist]` now ships only the Python
  package + project metadata and excludes the top-level manuscript scratch
  directories, whose absolute-path symlinks made `hatchling` sdist builds fail
  with `tarfile.AbsoluteLinkError` (#1f4e039).
- **CLA workflow:** `cla.yml` reads `GH_PERSONAL_ACCESS_TOKEN` (PS-168).
- Author metadata email corrected to `ywatanabe@scitex.ai`.

## [2.17.3] - 2026-06-03

### Changed
- **Adopt the per-package `~/.scitex/writer/containers/<tool>.sif` convention
  for SIF paths (#117).** Configs, shell modules, installation scripts, and
  Makefile now point at the canonical per-package containers root (operator
  design 8566 + sac PR #293). `command_switching.src` extracts a shared
  `_writer_resolve_sif(tool, var)` helper that resolves canonical first,
  falls back to the legacy `./.cache/containers/<tool>_container.sif` with a
  `[DEPRECATED]` log line on hit (keeps pre-migration caches working until
  rebuilt via `scitex-writer containers install <tool>`). The canonical
  `~/.scitex/writer/containers/texlive.sif` artifact built earlier today is
  picked up immediately on upgrade — no rebuild required for texlive.
  Mermaid / tectonic / imagemagick still need their builds in a separate
  follow-up (P1.b of the brand-wide ecosystem containers/bin migration).
- 4-way duplication across `setup_latex_container`,
  `setup_tectonic_container`, `setup_mermaid_container`,
  `setup_imagemagick_container` collapsed via the shared resolver helper:
  `command_switching.src` 528 → 507 lines.

## [2.17.2] - 2026-05-26

### Fixed
- **sdist build failure** — absolute symlinks (`00_shared/scholar/library`)
  in the repo root now excluded from the source distribution via
  `[tool.hatch.build.targets.sdist] exclude`. v2.17.1 release aborted at
  the build step; this is the corrected release.

## [2.17.1] - 2026-05-26

### Changed
- **Test suite fully de-mocked.** Every `unittest.mock`/`pytest-mock`/`monkeypatch`
  call replaced with real seams (injectable `clone_fn`, `command_runner`, `handler`
  callables) and hand-rolled fakes (skeleton project directory, fake `Popen` process,
  real filesystem operations on `tmp_path`). 1092→47 PA-307 TQ violations (-95.7%).
  Covers: `compile_content`, `Writer`, `manuscript`/`supplementary`/`revision`,
  `runner`, `checks`, `watch`, `migration`, `scholar_cli`, `thumbnails`,
  `clone_writer_project`, `ensure_project_exists`, `argv`-dependent CLI tests,
  smoke imports.

### Fixed
- **Audit gate PATH resolution** — `test_audit_all_clean` now prepends
  `sys.exec_prefix/bin` to `PATH` so the project venv's `scitex-dev` is resolved
  before any system-installed copy that cannot locate the repo root.

## [2.17.0] - 2026-05-08

### Changed (BREAKING — MCP tool names)
- **MCP tool naming aligned with Python API `<noun>_<verb>` convention.** Resolves the scitex-dev `audit-mcp-tools §6` parity rule. Clients that call MCP tools by name must update; signatures and behaviour are unchanged.
  - `bib`: `add_bibentry`/`get_bibentry`/`list_bibentries`/`list_bibfiles`/`remove_bibentry`/`merge_bibfiles` → `bib_add`/`bib_get`/`bib_list_entries`/`bib_list_files`/`bib_remove`/`bib_merge`
  - `claim`: `add_claim`/`get_claim`/`list_claims`/`remove_claim`/`format_claim`/`render_claims` → `claim_<verb>`
  - `figures`/`tables`: `add_figure`/`list_figures`/`archive_figure`/`convert_figure`/`pdf_to_images` (and table equivalents incl. `csv_to_latex`/`latex_to_csv`) → `figures_<verb>` / `tables_<verb>`
  - `project`: `clone_project`/`get_project_info`/`get_pdf`/`list_document_types` → `project_<verb>`
  - `checks`: `check_float_order`/`check_references` → `checks_<verb>`
  - `guidelines`: `guideline_get`/`guideline_build`/`guideline_list` → `guidelines_<verb>(_sections)`
  - `migration`: `import_overleaf`/`export_overleaf` → `migration_from_overleaf` / `migration_to_overleaf`
  - `prompts`: `prompts_asta` → `prompts_generate_asta`
- All names are still `writer_`-prefixed at the MCP boundary (e.g., `writer_bib_add`).

### Fixed
- `audit-zero` campaign — cleared all `scitex-dev ecosystem audit-all scitex-writer` violations: `PS108b`/`SK109`/`SK302` and the §6 MCP parity gap. Test tree migrated from `tests/python/` to `tests/scitex_writer/` mirroring `src/scitex_writer/`; CI workflow paths updated; `tests/develop/test_audit.py` skip_rules cover the upstream-only `§1` umbrella-bridge rule.
- `figures.archive` and `tables.archive` are now in `__all__` so the public API parity check sees them.

## [2.16.1] - 2026-04-21

### Fixed
- **CI: missing deps.** v2.16.0 green-lit by local tests but failed CI because three dependencies were implicit (worked via `pip install -e` sibling discovery on dev machines, not on CI):
  - `Pillow` — core (thumbnail service); added to `dependencies`.
  - `scitex-ui>=0.1.0` — core (editor + viewer templates extend `scitex_ui/standalone_shell.html`); added to `dependencies`.
  - `scitex-logging` — removed as an implicit dep by switching `_ports/workspace.py` + `_ports/thumbnails.py` to stdlib `logging`.
- **Lint F401.** `handle_citation` is imported for parametric URL dispatch in `views.py` but ruff (correctly) flagged it as unused; added to `__all__`.

No API change — same behaviour as 2.16.0 on machines where the implicit deps happened to be on PATH.

## [2.16.0] - 2026-04-21

Closes scitex-cloud **#133** — Living Paper (interactive claim verification). Writer-side implementation; since 2.15.0 made local and cloud share one editor, the feature lands entirely in writer.

### Added
- **Claims tab in editor's PDF pane** — populates the previously-empty `#claims-view` with the same claim cards the viewer shows. Click a card → inline detail pane + DAG rendering; click "Find in source" → Monaco reveals the `\vclaim{<id>}` line. Lazy-loaded on first tab open; refreshes after each compile.
- **`claims-list.ts`** — shared module for claim cards, verification badges, and DAG rendering. Used by both editor and viewer so they stay consistent.
- **`onAfterCompile(cb)`** hook on `CompileController` — lets downstream UI (currently Claims tab) refresh after a successful or failed compile.

### Changed
- **`\vclaim` macro emits `\hypertarget{vclaim-<id>}{…}`** on first expansion (via a one-shot flag). PDF.js can now locate claim text for future hover-popup work. Subsequent `\vclaim{id}` calls skip the anchor to avoid hyperref's duplicate-destination warning.
- Mermaid CDN script now loaded in `editor.html` alongside `viewer.html`, so DAG rendering works in both contexts.

### Out of scope (per #133)
- PDF text-layer hover popups (needs SyncTeX positional mapping — deferred per the issue body).
- Static `claims_metadata.json` sidecar for external PDF readers — the live `api/claims-metadata` endpoint serves the editor/viewer UX; sidecar is a follow-up portability item.
- Real-time verification re-runs from the popup.

## [2.15.0] - 2026-04-21

Closes issue **#82** — Flask `_editor` app fully ported to Django `_django`, rich cloud-feature parity, optional scholar bridge, and a generic thumbnail service. 28 commits since 2.14.1.

### Added
- **Django editor** (`scitex_writer._django`) — port of the retired Flask `_editor` app with the same API surface and Flask removed entirely. Uses `scitex-ui`'s `standalone_shell.html` for the three-column workspace shell and `scitex-app`'s `run_standalone()` for the dev server. (#84, #85)
- **Monaco LaTeX editor** via Vite bundling, with LaTeX syntax highlighting, section tabs, and automatic layout on shell-pane show/hide. (#86)
- **PDF preview + compile UI** in the editor, including log drawer, lamp status, and Preview / Full compile modes. (#87)
- **Insert icon-bar** (Cite / Fig / Table / Collab / History) + figures & tables API handlers. (#88)
- **Viewer module** (`/viewer/` route) — claims overlay, DAG render, and citation hover. Unblocks Living Paper integration. (#89)
- **Rich citation panel** ported from scitex-cloud — multi-select via Ctrl/Cmd-click, drag into Monaco to insert `\cite{k1,k2}`, Monaco `\cite{}` completion + hover provider that renders scholar metadata. (#90)
- **Scholar bridge** (`scitex_writer._ports.scholar`) — **optional** one-way consumer of `scitex-scholar>=1.2.1`. `SCHOLAR_AVAILABLE` flag; resolves DOIs via `index.db` SELECT when present (fast path), MASTER-scan fallback. `SCHOLAR` extras: `pip install scitex-writer[scholar]`. Writer works without scholar installed — UI degrades to bare bib cards. (#90)
- **Scholar Django endpoints**: `api/scholar/{status,library,enrich,add-to-manuscript}` + `api/bib/entries` now returns nested `scholar` metadata when a DOI matches a MASTER entry. (#90)
- **Workspace port** (`scitex_writer._ports.workspace`) — idempotent `<project>/00_shared/scholar/library → ~/.scitex/scholar/library/` symlink. Called from `get_or_create_project`. (#90)
- **Scholar shell-out** (`scitex_writer._ports.scholar_cli`) — Enrich button always visible; shells out to `scitex-scholar` CLI (or `python -m scitex_scholar`), shows install hint when neither is on PATH. (#90)
- **Generic thumbnail service** (`scitex_writer._ports.thumbnails`) — Pillow-based image thumbs (PNG/JPG/JPEG/JFIF/GIF/WEBP/BMP/TIFF/TIF/ICO/HEIC/AVIF), `pdftoppm` for PDF, `rsvg-convert` for SVG, pandas+matplotlib preview (styled blue header + zebra rows) for CSV/TSV/XLSX/XLS/ODS. Cache-keyed by `sha1(abs_path + mtime)` under `00_shared/thumbnails/{figures,tables}/`. No figrecipe coupling — aggregates any media files discovered under `caption_and_media/`. (#90)
- **`api/thumbnail` handler** + `media_path` / `media_ext` / `thumbnail_url` on figure/table API responses. Insert panel now renders a thumbnail grid when entries have them. (#90)
- **PDF theme toggle** in the PDF pane (auto / light / dark) — cycles through three states persisted in localStorage; independent of the editor UI theme so authors can preview a light PDF while editing in dark mode. (#90)
- **Dark-mode compile wiring** — editor theme drives `compile(..., dark_mode=True/False)`, which injects `00_shared/latex_styles/dark_mode.tex`. Figures explicitly preserved. (#90)
- **Details right panel** — sections for Compilation (Preview / Full), Overleaf, Prism (OpenAI), Project, and Shortcuts. Compilation section shows live status dots from the compile controller. (#90)
- **Favicon set** — 16 / 32 / 64 / 180 / 192 / 512 px PNGs + an SVG wrapper embedding the 512 px source. Tagged with `sizes=` so browsers self-select. (#90)
- **Keyboard-shortcut icon** in toolbar that expands the Shortcuts section in Details. (#90)
- **Download-PDF button** in the PDF toolbar. (#90)
- **Section dropdown** next to the doc-type dropdown; **Collab tab** with self-host hint pointing at scitex-cloud (AGPL-3.0). (#90)
- **`pyproject.toml` optional-dependency** `[scholar]` pinning `scitex-scholar>=1.2.1`. (#90)
- **`_ports/` test suite** — 27 unit tests covering scholar bridge (DB-preferred + MASTER fallback, dangling symlink, case-insensitive DOI lookup), thumbnails (image + CSV + placeholder + cache-key invalidation), scholar_cli shell-out, and workspace symlink semantics. (#90)
- **Ported 9 cleanup/lint commits** from upstream shell-script work (#79 followups). Drops 100% of shellcheck warnings in `scripts/shell/**`.

### Changed
- **Flask removed.** `scitex_writer._editor` is gone; all editor behaviour now lives in `scitex_writer._django`. (#84)
- Editor template now loads Vite-built `assets/index.css` so Monaco styles apply correctly. Previously relied on an inlined CSS block that diverged from the bundled output. (#90)
- `.u-hidden` class now beats panel-specific `display: flex` via `!important` — insert/details panels stay hidden when toggled off regardless of panel-local rules. (#90)
- Standalone shell hides empty shell panes (Console, Files, Viewer) so the writer editor gets the full viewport. Re-shows them in cloud mode where those panes are populated. (#90)
- Compile API request now includes `dark_mode: bool`; `ProjectState.dark_mode` persisted per-project as the fallback.
- Citation cache invalidated after Enrich / Add-to-manuscript — Monaco `\cite{}` autocomplete no longer shows stale entries for up to 60 s after a library update.
- Drag-and-drop uses a custom `application/x-scitex-cite` MIME in addition to text/plain, so arbitrary text drops don't trigger the cite-insert path.
- `claims_rendered.tex` emits portable `\providecommand` + `##` tokens so users can `\input{}` without colliding with existing definitions.
- Renamed `\stxclaim` → `\vclaim` (debrand to "verifiable-claim").
- CLA workflow `issue_comment` trigger now gated on URL shape rather than `issue.pull_request` — fixes spurious CI failures.

### Fixed
- `.u-hidden` specificity on shell-composed panels (#90).
- `lint(F841)`: drop unused `Client` import in `_django` test suite (#84).
- `ensure_workspace()` now creates `.scitex/writer/` as a hidden dotfile dir.
- `merge_bibliographies` output-path handling (absolute paths + subdirs + self-exclusion).
- Word-count formatting: comma separators + per-section breakdown; uses portable `sed` rather than locale-dependent `printf`.
- `find` calls in shell scripts bounded with `-maxdepth 1`; deep walks use explicit `command find` override.
- SPDX license identifier normalized to `AGPL-3.0-only`.



## [2.9.0] - 2026-03-14

### Added
- feat: Wire `docs` subcommand into scitex-writer via scitex_dev mixin

### Fixed
- fix: Use public FastMCP 3.x API instead of removed `_tool_manager`
- fix: Update Result schema docs from `next_steps` to `hints_on_error`

### Changed
- chore: Gitignore pre-built `_docs/` directory

## [2.8.1] - 2026-03-12

### Added
- feat: CLA, CONTRIBUTING.md, and CLA Assistant workflow

### Fixed
- fix: Check directory has content before skipping clone in `ensure_workspace()`

### Changed
- refactor: Remove 39 `[writer]` docstring tag prefixes from MCP tools
- chore: Gitignore manuscript PDFs

## [2.8.0] - 2026-03-10

### Added
- feat: Overleaf migration tools (import/export)

### Fixed
- fix: Remove `from __future__ import annotations` from MCP tool files

## [2.7.2] - 2026-03-08

### Added
- feat: Claim feature — traceable scientific assertions
- feat: Update command and version stamps

### Fixed
- fix: Audit fixes — hide internal dataclasses, add claim tests, update docs
- fix: Resolve CI failures — noqa for internal imports, update FastMCP tool API

## [2.7.1] - 2026-03-06

### Fixed
- fix: Remove stale `export.py` and exclude MCP handlers from coverage
- fix: Resolve CI failures — remove unused imports, exclude editor from coverage

## [2.7.0] - 2026-03-04

### Added
- feat: Standalone GUI editor (`scitex-writer gui`, `sw.gui()`)
  - Browser-based LaTeX editor with CodeMirror 5 (syntax highlighting, search, fold)
  - pdf.js PDF preview with page navigation and zoom controls
  - File tree sidebar with project structure
  - One-click compilation (manuscript/supplementary/revision)
  - Bibliography browser with click-to-insert citations
  - Dark/light mode toggle (matches scitex-cloud colors)
  - Resizable panels, file tabs with unsaved indicator
  - Docker support (`Dockerfile.gui`, `docker-compose.gui.yml`)
  - Flask as optional dependency: `pip install scitex-writer[editor]`

### Changed
- refactor: Minimize Python API surface

## [2.6.7] - 2026-03-02

### Added
- feat: DRY dark mode colors via config, add `dark_mode` to all MCP tools

### Fixed
- fix: Audit findings — engine bug, broken examples, coverage threshold

## [2.6.6] - 2026-02-28

### Changed
- refactor: Rename `compile_content_document` → `tex_snippet2full`

### Fixed
- fix: Add `.gitkeep` to `03_revision/contents/tables/` for CI compilation
- ci: Add all three doc types to compilation CI tests

## [2.6.5] - 2026-02-26

### Added
- feat: `ensure_workspace()` for lazy writer workspace creation
- feat: Descriptive titles for PDF bookmarks

### Fixed
- fix: Use project scripts directory for content compilation
- ci: Update actions/setup-python to v5, add Python 3.13 to test matrix
- fix: Resolve CI lint errors and PIL import failure in tests

## [2.6.4] - 2026-02-22

### Added
- feat: Validation checks for pre-compilation
- ci: PyPI publish workflow on GitHub release

### Fixed
- fix: Compilation bugs and template improvements
- fix: Watch mode respects `SCITEX_WRITER_DARK_MODE` env var

## [2.6.2] - 2026-02-18

### Fixed
- fix: Dark mode compilation and env var passthrough (Issue #43)
- fix: Clean compiled figures directory before regeneration (Issue #41)

### Changed
- chore: Parse `pyproject.toml` as single source of truth for version

## [2.6.1] - 2026-02-16

### Fixed
- fix: Update dark mode tests to match Monaco color scheme

## [2.6.0] - 2026-02-14

### Added
- feat: arXiv export feature (`make manuscript-export`)
- feat: `make check` for pre-compilation validation
- feat: Backward-compatible Makefile aliases for README targets

### Fixed
- fix: Audit fixes — add export to `__all__`, help to watch script, update README
- fix: Add timeout to diff compilation to prevent infinite loops

### Changed
- refactor: Prefix pattern for Makefile targets, update DPI to 600

## [2.5.4] - 2026-02-09

### Changed
- refactor: Split monolithic `_mcp/handlers.py` (571 lines) into `handlers/` package
  - `_project.py`: clone, info, PDF paths, document types
  - `_compile.py`: manuscript, supplementary, revision compilation
  - `_tables.py`: CSV/LaTeX table conversions
  - `_figures.py`: pdf_to_images, list_figures, convert_figure
- feat: Default DPI for `pdf_to_images` increased from 150 to 600

## [2.5.3] - 2026-02-08

### Changed
- refactor: Content compilation moved to proper shell/Python API/MCP architecture
  - Business logic in `_compile/content.py`, MCP layer is thin wrapper
  - Shell script `scripts/shell/compile_content.sh` for latexmk invocation
  - Python document builder `scripts/python/tex_snippet2full.py`

### Fixed
- fix: Dark mode PDF uses Monaco colors (#1E1E1E bg, #D4D4D4 text)
- fix: Preview compilation failures due to missing compile API
- fix: Lazy-import MCP server to avoid pydantic/fastmcp conflicts at import time

## [2.2.1] - 2026-01-20

### Added
- Full MCP tool suite migrated from scitex.writer (13 tools total)
  - clone_project, compile_manuscript, compile_supplementary, compile_revision
  - get_project_info, get_pdf, list_document_types
  - csv_to_latex, latex_to_csv, pdf_to_images
  - list_figures, convert_figure, scitex_writer

### Changed
- Python MCP package version: 0.1.2
- Refactored MCP module structure (_server.py, _mcp/handlers.py, _mcp/utils.py)

## [2.2.0] - 2026-01-19

### Added
- Demo examples in `examples/` directory
  - Org-mode session export
  - PDF exports (demo session, manuscript, revision)
  - Video demo with thumbnail
- Improved MCP server instructions for AI agents
  - Absolute path guidance for Claude Code
  - BASH_ENV workaround documentation
  - Figure/table caption format examples

### Fixed
- bibtexparser correctly classified as required dependency (was optional)
- Shellcheck compliance in check_dependancy_commands.sh
  - Proper variable quoting (SC2046/SC2086)
  - Removed unused GIT_ROOT variable (SC2034)
  - Separated local declarations from assignments (SC2155)
- Script portability improvements with $PROJECT_ROOT paths
- Bibliography symlink (00_shared/bibliography.bib) now tracked in git

### Changed
- Python MCP package version: 0.1.1

## [2.1.0] - 2026-01-18

### Added
- Python MCP package published to PyPI (`pip install scitex-writer`)
- CLI commands: `scitex-writer --version`, `scitex-writer mcp start`
- AGPL-3.0 license
- CI workflows for testing and publishing

## [2.0.0-rc4] - 2026-01-09

### Added
- `scripts/maintenance/strip_example_content.sh` - Minimal template creation tool (#14)
- Automatic preprocessing artifact initialization on compile (#12)

### Fixed
- Working directory handling in compile scripts (#13)
  - Scripts now resolve project root from script location
  - Works correctly when invoked from any directory (MCP, CI/CD, IDEs)
  - Auto-initialization of preprocessing artifacts if missing
- Minimal template option for faster project setup (#14)

### Changed
- Project structure reorganization:
  - Moved `Dockerfile` to `scripts/containers/`
  - Moved `requirements/` to `scripts/installation/requirements/`
  - Created `scripts/maintenance/` for maintenance tools
- Updated documentation paths in README and container setup instructions
- Compile scripts now use absolute path resolution for better portability
- Shellcheck compliance improvements

## [2.0.0-rc3] - 2025-11-18

### Added
- AI prompts for scientific writing assistance
  - Abstract writing guidelines
  - Introduction writing guidelines
  - Methods writing guidelines
  - Discussion writing guidelines
  - General proofreading guidelines

## [2.0.0-rc2] - 2025-11-12

### Added
- Three-engine compilation system (Apptainer, Docker, Native)
- Auto-detection of available compilation engines
- Parallel asset processing for faster compilation

### Changed
- Improved compilation logging with stage timestamps
- Streamlined configuration loading

## [2.0.0-rc1] - 2025-11-08

### Added
- Complete LaTeX manuscript compilation system
- Automatic figure/table processing
- Bibliography merging from multiple sources
- Version tracking with diff generation
- Support for manuscript, supplementary, and revision documents

### Changed
- Restructured project for better modularity
- Separated configuration from scripts

[Unreleased]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.17.2...HEAD
[2.17.2]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.17.1...v2.17.2
[2.17.1]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.17.0...v2.17.1
[2.17.0]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.9.0...v2.17.0
[2.9.0]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.8.1...v2.9.0
[2.8.1]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.8.0...v2.8.1
[2.8.0]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.7.2...v2.8.0
[2.7.2]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.7.1...v2.7.2
[2.7.1]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.7.0...v2.7.1
[2.7.0]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.6.7...v2.7.0
[2.6.7]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.6.6...v2.6.7
[2.6.6]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.6.5...v2.6.6
[2.6.5]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.6.4...v2.6.5
[2.6.4]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.6.2...v2.6.4
[2.6.2]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.6.1...v2.6.2
[2.6.1]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.6.0...v2.6.1
[2.6.0]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.5.4...v2.6.0
[2.5.4]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.5.3...v2.5.4
[2.5.3]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.2.1...v2.5.3
[2.2.1]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.2.0...v2.2.1
[2.2.0]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.0.0-rc4...v2.1.0
[2.0.0-rc4]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.0.0-rc3...v2.0.0-rc4
[2.0.0-rc3]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.0.0-rc2...v2.0.0-rc3
[2.0.0-rc2]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.0.0-rc1...v2.0.0-rc2
[2.0.0-rc1]: https://github.com/ywatanabe1989/scitex-writer/releases/tag/v2.0.0-rc1
