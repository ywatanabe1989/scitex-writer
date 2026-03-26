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

# Legacy engine paths (kept for backwards compat with older projects)
LEGACY_ENGINE_PATHS = [
    Path("00_shared") / "latex_styles",
    Path("01_manuscript") / "base.tex",
    Path("02_supplementary") / "base.tex",
    Path("03_revision") / "base.tex",
    "Makefile",
]

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
