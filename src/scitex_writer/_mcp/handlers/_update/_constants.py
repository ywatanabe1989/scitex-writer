#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_update/_constants.py

"""Constants for the update handler."""

from pathlib import Path

TEMPLATE_REPO_URL = "https://github.com/ywatanabe1989/scitex-writer.git"

# Directories to sync (relative to project root)
SYNC_DIRS = [
    "src/scitex_writer",
    "scripts",
]

# Individual files to sync (relative to project root)
SYNC_FILES = [
    "compile.sh",
]

# Engine paths synced at their own location (rel path is the same in template
# and project). latex_styles is handled specially (see ACTIVE_STYLE_DOC_DIRS)
# so drift is detected in the copy the manuscript actually compiles.
LEGACY_ENGINE_PATHS = [
    Path("01_manuscript") / "base.tex",
    Path("02_supplementary") / "base.tex",
    Path("03_revision") / "base.tex",
    "Makefile",
]

# Rendering style files live in the template at 00_shared/latex_styles/ but the
# manuscript compiles them via <doc>/contents/latex_styles/ (normally a symlink
# to 00_shared/latex_styles/). We compare/sync via the ACTIVE compiled path so a
# project whose symlink diverged to a stale copy is still caught — file_hash()
# and copy2() follow the symlink to the real file.
TEMPLATE_STYLE_DIR = Path("00_shared") / "latex_styles"
ACTIVE_STYLE_DOC_DIRS = ["01_manuscript", "02_supplementary", "03_revision"]

# Directory names that must never be synced (build artifacts / caches / vendored
# deps) — they flood the drift report and are regenerable, never edited.
SKIP_DIR_NAMES = {
    "__pycache__",
    "node_modules",
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "_sphinx_html",
    ".update_backup",
}

# User content -- never touch (used for documentation in results only)
PRESERVED_PATHS = [
    Path("00_shared") / "authors.tex",
    Path("00_shared") / "title.tex",
    Path("00_shared") / "keywords.tex",
    Path("00_shared") / "journal_name.tex",
    Path("00_shared") / "bib_files" / "bibliography.bib",
    Path("00_shared") / "claims.json",
    Path("01_manuscript") / "contents",
    Path("02_supplementary") / "contents",
    Path("03_revision") / "contents",
]

# EOF
