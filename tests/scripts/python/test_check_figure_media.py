#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_figure_media.py
#
# Reproduces the silent "Missing Figure" placeholder condition: a figure
# declared by a caption .tex with NO rendered media asset must now FAIL LOUD
# (gate names the figure and exits non-zero) instead of degrading to a
# placeholder.

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_figure_media import resolve_level  # noqa: E402

_SCRIPT = ROOT_DIR / "scripts" / "python" / "check_figure_media.py"

_FIG_MEDIA = "01_manuscript/contents/figures/caption_and_media"


# ============================================================================
# helpers / fixtures
# ============================================================================


def _write(tmp_path, rel, content):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _declare_figure(tmp_path, stem):
    """Declare a figure: drop its caption .tex under the figure media dir."""
    return _write(tmp_path, f"{_FIG_MEDIA}/{stem}.tex", f"\\textbf{{Figure}} {stem}.\n")


def _add_media(tmp_path, name):
    """Drop a (byte) media asset under the figure media dir."""
    return _write(tmp_path, f"{_FIG_MEDIA}/{name}", "x")


def _run(project, *extra):
    env = dict(os.environ)
    env.pop("SCITEX_WRITER_FIGURE_MEDIA", None)
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(project), *extra],
        capture_output=True,
        text=True,
        env=env,
    )


@pytest.fixture
def clean_env():
    saved = {k: os.environ.get(k) for k in ("SCITEX_WRITER_FIGURE_MEDIA", "HOME")}
    os.environ.pop("SCITEX_WRITER_FIGURE_MEDIA", None)
    with tempfile.TemporaryDirectory() as home:
        os.environ["HOME"] = home
        yield home
    for key, val in saved.items():
        if val is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = val


# ============================================================================
# resolve_level
# ============================================================================


def test_resolve_level_defaults_to_error_for_research(tmp_path, clean_env):
    """A research project defaults the figure-media gate to error."""
    # Arrange
    check = "figure_media"
    # Act
    level = resolve_level(
        check,
        None,
        str(tmp_path),
        default="error",
        env_var="SCITEX_WRITER_FIGURE_MEDIA",
    )
    # Assert
    assert level == "error"


# ============================================================================
# End-to-end (no LaTeX toolchain needed)
# ============================================================================


def test_declared_figure_without_media_errors(tmp_path, clean_env):
    """A figure declared with no media asset blocks the compile (exit 1)."""
    # Arrange
    _declare_figure(tmp_path, "01_overview")
    # Act
    proc = _run(tmp_path, "--level", "error")
    # Assert
    assert proc.returncode == 1


def test_missing_figure_is_named_in_report(tmp_path, clean_env):
    """The failure names the declared-but-missing figure caption."""
    # Arrange
    _declare_figure(tmp_path, "01_overview")
    # Act
    proc = _run(tmp_path, "--level", "error")
    # Assert
    assert "01_overview.tex" in proc.stdout


def test_declared_figure_with_media_passes(tmp_path, clean_env):
    """A figure whose media asset exists resolves cleanly (exit 0)."""
    # Arrange
    _declare_figure(tmp_path, "01_overview")
    _add_media(tmp_path, "01_overview.jpg")
    # Act
    proc = _run(tmp_path, "--level", "error")
    # Assert
    assert proc.returncode == 0


def test_figure_resolved_by_panels_passes(tmp_path, clean_env):
    """A figure with only NN{a,b} panel media (no direct asset) resolves."""
    # Arrange
    _declare_figure(tmp_path, "02_panels")
    _add_media(tmp_path, "02a_left.png")
    _add_media(tmp_path, "02b_right.png")
    # Act
    proc = _run(tmp_path, "--level", "error")
    # Assert
    assert proc.returncode == 0


def test_panel_caption_not_treated_as_declared_figure(tmp_path, clean_env):
    """A panel caption (NNa_) is not itself a declared figure (exit 0)."""
    # Arrange
    _declare_figure(tmp_path, "03a_only_a_panel")
    # Act
    proc = _run(tmp_path, "--level", "error")
    # Assert
    assert proc.returncode == 0


def test_reports_all_missing_figures_at_once(tmp_path, clean_env):
    """One run surfaces every missing figure together, not one-at-a-time."""
    # Arrange
    _declare_figure(tmp_path, "01_overview")
    _declare_figure(tmp_path, "02_results")
    # Act
    proc = _run(tmp_path, "--level", "error")
    # Assert
    assert "2 errors" in proc.stdout


def test_off_level_skips(tmp_path, clean_env):
    """--level off disables the gate even with a missing figure (exit 0)."""
    # Arrange
    _declare_figure(tmp_path, "01_overview")
    # Act
    proc = _run(tmp_path, "--level", "off")
    # Assert
    assert proc.returncode == 0


def test_warn_level_does_not_block(tmp_path, clean_env):
    """--level warn reports but exits 0 (the draft placeholder opt-in)."""
    # Arrange
    _declare_figure(tmp_path, "01_overview")
    # Act
    proc = _run(tmp_path, "--level", "warn")
    # Assert
    assert proc.returncode == 0


def test_prefix_collision_does_not_false_pass(tmp_path, clean_env):
    """Media for figure 10 must not satisfy figure 1 (prefix-boundary)."""
    # Arrange
    _declare_figure(tmp_path, "1_first")
    _add_media(tmp_path, "10_tenth.jpg")
    # Act
    proc = _run(tmp_path, "--level", "error")
    # Assert
    assert proc.returncode == 1
