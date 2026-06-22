#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_limits.py

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_limits import (  # noqa: E402
    collect_source_tex,
    load_limits,
    unique_cite_keys,
)

_SCRIPT = ROOT_DIR / "scripts" / "python" / "check_limits.py"


# ============================================================================
# load_limits
# ============================================================================


def test_load_limits_reads_block(tmp_path):
    """load_limits returns the limits mapping when the block is present."""
    # Arrange
    cfg = tmp_path / "config_manuscript.yaml"
    cfg.write_text("limits:\n  references: 50\n  words:\n    abstract: 250\n")
    # Act
    limits = load_limits(cfg)
    # Assert
    assert limits["references"] == 50 and limits["words"]["abstract"] == 250


def test_load_limits_missing_file_returns_empty(tmp_path):
    """load_limits returns {} when the config file does not exist."""
    # Arrange
    cfg = tmp_path / "absent.yaml"
    # Act
    limits = load_limits(cfg)
    # Assert
    assert limits == {}


def test_load_limits_no_block_returns_empty(tmp_path):
    """load_limits returns {} when the file has no limits: block."""
    # Arrange
    cfg = tmp_path / "config_manuscript.yaml"
    cfg.write_text("citation:\n  style: unsrtnat\n")
    # Act
    limits = load_limits(cfg)
    # Assert
    assert limits == {}


def test_load_limits_bad_shape_returns_none(tmp_path):
    """load_limits fails loud (None) when limits: is not a mapping."""
    # Arrange
    cfg = tmp_path / "config_manuscript.yaml"
    cfg.write_text("limits:\n  - 1\n  - 2\n")
    # Act
    limits = load_limits(cfg)
    # Assert
    assert limits is None


# ============================================================================
# unique_cite_keys
# ============================================================================


def test_unique_cite_keys_dedupes_and_skips_comments(tmp_path):
    """unique_cite_keys dedupes multi-key cites and ignores commented ones."""
    # Arrange
    tex = tmp_path / "intro.tex"
    tex.write_text(r"\citep{A, B} and \citet{B,C}" "\n" r"% \cite{D_commented}")
    # Act
    keys = unique_cite_keys([tex])
    # Assert
    assert keys == {"A", "B", "C"}


def test_collect_source_tex_skips_generated(tmp_path):
    """collect_source_tex gathers contents/*.tex but skips _diff/_v files."""
    # Arrange
    contents = tmp_path / "contents"
    contents.mkdir()
    (contents / "introduction.tex").write_text("x")
    (contents / "manuscript_diff.tex").write_text("x")
    # Act
    names = {f.name for f in collect_source_tex(tmp_path)}
    # Assert
    assert "introduction.tex" in names and "manuscript_diff.tex" not in names


# ============================================================================
# End-to-end script behaviour (requires texcount)
# ============================================================================


def _make_project(tmp_path, strict, abstract_limit):
    config = tmp_path / "config"
    config.mkdir()
    contents = tmp_path / "01_manuscript" / "contents"
    contents.mkdir(parents=True)
    (contents / "abstract.tex").write_text("one two three four five six seven")
    (config / "config_manuscript.yaml").write_text(
        f"limits:\n  strict: {str(strict).lower()}\n"
        f"  words:\n    abstract: {abstract_limit}\n"
    )
    return tmp_path


@pytest.mark.skipif(shutil.which("texcount") is None, reason="texcount not installed")
def test_check_limits_strict_exits_nonzero_when_over(tmp_path):
    """Strict mode returns a non-zero exit code when a section is over limit."""
    # Arrange
    project = _make_project(tmp_path, strict=True, abstract_limit=2)
    # Act
    proc = subprocess.run(
        [sys.executable, str(_SCRIPT), str(project), "--doc-type", "manuscript"],
        capture_output=True,
        text=True,
    )
    # Assert
    assert proc.returncode == 1


@pytest.mark.skipif(shutil.which("texcount") is None, reason="texcount not installed")
def test_check_limits_nonstrict_exits_zero_when_over(tmp_path):
    """Non-strict mode warns but still exits zero when a section is over limit."""
    # Arrange
    project = _make_project(tmp_path, strict=False, abstract_limit=2)
    # Act
    proc = subprocess.run(
        [sys.executable, str(_SCRIPT), str(project)],
        capture_output=True,
        text=True,
    )
    # Assert
    assert proc.returncode == 0 and "over by" in proc.stdout
