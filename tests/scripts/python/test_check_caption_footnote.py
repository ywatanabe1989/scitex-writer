#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_caption_footnote.py

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_caption_footnote import (  # noqa: E402
    _caption_arg_spans,
    _strip_comments,
    resolve_level,
)

_SCRIPT = ROOT_DIR / "scripts" / "python" / "check_caption_footnote.py"

_CAPTION_MEDIA = "01_manuscript/contents/figures/caption_and_media"


# ============================================================================
# helpers / fixtures
# ============================================================================


def _write(tmp_path, rel, content):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _run(project, *extra):
    env = dict(os.environ)
    env.pop("SCITEX_WRITER_CAPTION_FOOTNOTE", None)
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(project), *extra],
        capture_output=True,
        text=True,
        env=env,
    )


@pytest.fixture
def clean_env():
    """Isolate env + HOME so no stray SCITEX_WRITER_CAPTION_FOOTNOTE or user
    config.yaml leaks into severity resolution."""
    saved = {
        k: os.environ.get(k)
        for k in ("SCITEX_WRITER_CAPTION_FOOTNOTE", "HOME")
    }
    os.environ.pop("SCITEX_WRITER_CAPTION_FOOTNOTE", None)
    with tempfile.TemporaryDirectory() as home:
        os.environ["HOME"] = home
        yield home
    for key, val in saved.items():
        if val is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = val


# ============================================================================
# resolve_level — default severity
# ============================================================================


def test_resolve_level_defaults_to_error(tmp_path, clean_env):
    """With no --level, no env, no config, the default level is error."""
    # Arrange
    # Act
    level = resolve_level(
        "caption_footnote",
        None,
        tmp_path,
        default="error",
        env_var="SCITEX_WRITER_CAPTION_FOOTNOTE",
    )
    # Assert
    assert level == "error"


def test_resolve_level_cli_overrides(tmp_path, clean_env):
    """An explicit --level wins over a config-set level."""
    # Arrange
    pytest.importorskip("yaml")
    _write(tmp_path, "config.yaml", "caption_footnote:\n  level: error\n")
    # Act
    level = resolve_level(
        "caption_footnote",
        "warn",
        tmp_path,
        default="error",
        env_var="SCITEX_WRITER_CAPTION_FOOTNOTE",
    )
    # Assert
    assert level == "warn"


# ============================================================================
# _strip_comments
# ============================================================================


def test_strip_comments_blanks_commented_footnote():
    """A \\footnote after an unescaped % is removed from the scanned text."""
    # Arrange
    text = "good % \\footnote{ignored}\n"
    # Act
    stripped = _strip_comments(text)
    # Assert
    assert "\\footnote" not in stripped


def test_strip_comments_keeps_escaped_percent():
    """An escaped \\% is not treated as a comment start."""
    # Arrange
    text = "50\\% yield \\footnote{kept}\n"
    # Act
    stripped = _strip_comments(text)
    # Assert
    assert "\\footnote{kept}" in stripped


# ============================================================================
# _caption_arg_spans — brace matching
# ============================================================================


def test_caption_arg_spans_matches_nested_braces():
    """The span covers a caption arg containing nested braces."""
    # Arrange
    text = r"\caption{outer {inner} end}"
    # Act
    spans = list(_caption_arg_spans(text))
    # Assert
    assert [text[s:e] for s, e in spans] == ["outer {inner} end"]


def test_caption_arg_spans_skips_optional_short_arg():
    """An optional [short] arg before {...} is skipped, span is the long arg."""
    # Arrange
    text = r"\caption[short]{long body}"
    # Act
    spans = list(_caption_arg_spans(text))
    # Assert
    assert [text[s:e] for s, e in spans] == ["long body"]


# ============================================================================
# End-to-end script behaviour (no LaTeX toolchain needed)
# ============================================================================


def test_footnote_in_caption_media_file_errors(tmp_path, clean_env):
    """\\footnote in a caption_and_media/*.tex (whole-file caption body) errors."""
    # Arrange
    _write(tmp_path, f"{_CAPTION_MEDIA}/01.tex", "Cohort.\\footnote{disclosure}\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 1


def test_footnote_in_inline_caption_errors(tmp_path, clean_env):
    """\\footnote inside an inline \\caption{} in a content .tex errors."""
    # Arrange
    _write(
        tmp_path,
        "01_manuscript/contents/results.tex",
        "\\begin{figure}\\caption{Cap \\footnote{bad}}\\end{figure}\n",
    )
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 1


def test_footnotemark_in_caption_is_allowed(tmp_path, clean_env):
    """\\footnotemark (the blessed pattern) in a caption body does NOT error."""
    # Arrange
    _write(tmp_path, f"{_CAPTION_MEDIA}/01.tex", "Cohort.\\footnotemark\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 0


def test_footnotetext_in_caption_media_errors(tmp_path, clean_env):
    """\\footnotetext used as an in-caption workaround is flagged too."""
    # Arrange
    _write(tmp_path, f"{_CAPTION_MEDIA}/01.tex", "Cohort.\\footnotetext{x}\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 1


def test_commented_footnote_is_ignored(tmp_path, clean_env):
    """A \\footnote inside a LaTeX comment does not trigger the lint."""
    # Arrange
    _write(tmp_path, f"{_CAPTION_MEDIA}/01.tex", "Cohort. % \\footnote{ignored}\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 0


def test_off_level_exits_zero_with_violation(tmp_path, clean_env):
    """--level off disables the check even when a violation is present."""
    # Arrange
    _write(tmp_path, f"{_CAPTION_MEDIA}/01.tex", "Cohort.\\footnote{bad}\n")
    # Act
    proc = _run(tmp_path, "--level", "off")
    # Assert
    assert proc.returncode == 0


def test_warn_level_does_not_block(tmp_path, clean_env):
    """--level warn reports the violation but exits 0 (does not block compile)."""
    # Arrange
    _write(tmp_path, f"{_CAPTION_MEDIA}/01.tex", "Cohort.\\footnote{bad}\n")
    # Act
    proc = _run(tmp_path, "--level", "warn")
    # Assert
    assert proc.returncode == 0


def test_clean_manuscript_passes(tmp_path, clean_env):
    """A caption with no footnote passes (exit 0)."""
    # Arrange
    _write(tmp_path, f"{_CAPTION_MEDIA}/01.tex", "Cohort design overview.\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 0
