# Changelog

All notable changes to SciTeX Writer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/ywatanabe1989/scitex-writer/compare/v2.9.0...HEAD
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
