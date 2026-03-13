# Changelog

All notable changes to SciTeX Writer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
