#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: _build_id.py (inject_build_metadata \begin{document} anchoring)

import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from _build_id import inject_build_metadata  # noqa: E402

# A preamble comment whose text contains \begin{document} (e.g. clew's
# "overridable before \begin{document})"), appearing BEFORE the real marker.
_CONTENT = (
    "\\documentclass{article}\n"
    "%% --- signature config (overridable before \\begin{document}) ---\n"
    "\\newcommand{\\foo}{bar}\n"
    "\\begin{document}\n"
    "Hello\n"
    "\\end{document}\n"
)


def test_comment_with_begin_document_is_untouched():
    # Arrange
    original_comment = "%% --- signature config (overridable before \\begin{document}) ---"
    # Act
    out = inject_build_metadata(_CONTENT, "abc123")
    # Assert
    assert original_comment in out.splitlines()


def test_metadata_injected_only_once():
    # Arrange
    # Act
    out = inject_build_metadata(_CONTENT, "abc123")
    # Assert
    assert out.count("scitex-writer build identifier") == 1


def test_metadata_injected_before_real_begin_not_in_comment():
    # Arrange
    out = inject_build_metadata(_CONTENT, "abc123")
    # Act
    block_pos = out.index("scitex-writer build identifier")
    comment_pos = out.index("overridable before")
    # Assert
    assert block_pos > comment_pos


def test_noop_when_only_commented_begin_document():
    # Arrange
    only_comment = "\\documentclass{article}\n% see \\begin{document} note\nno real marker\n"
    # Act
    out = inject_build_metadata(only_comment, "abc123")
    # Assert
    assert out == only_comment
