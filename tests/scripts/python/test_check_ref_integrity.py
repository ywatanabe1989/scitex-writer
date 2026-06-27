#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_ref_integrity.py

import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_ref_integrity import resolve_level  # noqa: E402

_SCRIPT = ROOT_DIR / "scripts" / "python" / "check_ref_integrity.py"

_FIG_MEDIA = "01_manuscript/contents/figures/caption_and_media"
_TAB_MEDIA = "01_manuscript/contents/tables/caption_and_media"


# ============================================================================
# helpers / fixtures
# ============================================================================


def _write(tmp_path, rel, content):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _base_project(tmp_path, body):
    """A minimal project: fig:01 + tab:01 auto-labels, one bib key, and a
    results.tex whose body the caller supplies."""
    _write(tmp_path, f"{_FIG_MEDIA}/01.tex", "Figure one.\n")
    _write(tmp_path, f"{_TAB_MEDIA}/01.tex", "Table one.\n")
    _write(tmp_path, "00_shared/bib_files/bibliography.bib", "@article{Known2020, title={x}}\n")
    _write(tmp_path, "01_manuscript/contents/results.tex", body)
    return tmp_path


def _run(project, *extra):
    env = dict(os.environ)
    env.pop("SCITEX_WRITER_REF_INTEGRITY", None)
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(project), *extra],
        capture_output=True,
        text=True,
        env=env,
    )


@pytest.fixture
def clean_env():
    saved = {k: os.environ.get(k) for k in ("SCITEX_WRITER_REF_INTEGRITY", "HOME")}
    os.environ.pop("SCITEX_WRITER_REF_INTEGRITY", None)
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


def test_resolve_level_defaults_to_error(tmp_path, clean_env):
    """With no --level, no env, no config, the default level is error."""
    # Arrange
    # Act
    level = resolve_level(
        "ref_integrity",
        None,
        str(tmp_path),
        default="error",
        env_var="SCITEX_WRITER_REF_INTEGRITY",
    )
    # Assert
    assert level == "error"


# ============================================================================
# End-to-end (no LaTeX toolchain needed)
# ============================================================================


def test_undefined_figure_ref_errors(tmp_path, clean_env):
    """A \\ref to a non-existent figure label blocks (exit 1)."""
    # Arrange
    _base_project(tmp_path, "See \\ref{fig:99}.\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 1


def test_resolved_figure_and_table_refs_pass(tmp_path, clean_env):
    """\\ref to existing fig:/tab: auto-labels resolves (exit 0)."""
    # Arrange
    _base_project(tmp_path, "See \\ref{fig:01} and \\ref{tab:01}.\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 0


def test_undefined_citation_errors(tmp_path, clean_env):
    """A \\cite key absent from the bib blocks (exit 1)."""
    # Arrange
    _base_project(tmp_path, "Cite \\cite{Missing2021}.\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 1


def test_known_citation_passes(tmp_path, clean_env):
    """A \\cite key present in the bib resolves (exit 0)."""
    # Arrange
    _base_project(tmp_path, "Cite \\cite{Known2020}.\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 0


def test_supple_ref_without_aux_errors(tmp_path, clean_env):
    """A supple- xref with no supplement .aux blocks (exit 1)."""
    # Arrange
    _base_project(tmp_path, "See \\ref{supple-fig:S01}.\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 1


def test_supple_ref_without_aux_says_not_compiled(tmp_path, clean_env):
    """The missing-supplement message is explicit, not a generic undefined ref."""
    # Arrange
    _base_project(tmp_path, "See \\ref{supple-fig:S01}.\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert "supplement not compiled" in proc.stdout


def test_supple_ref_resolved_by_aux_passes(tmp_path, clean_env):
    """A supple- xref resolves against the supplement .aux \\newlabel (exit 0)."""
    # Arrange
    _base_project(tmp_path, "See \\ref{supple-fig:S01}.\n")
    _write(tmp_path, "02_supplementary/supplementary.aux", "\\newlabel{fig:S01}{{S1}{1}}\n")
    # Act
    proc = _run(tmp_path)
    # Assert
    assert proc.returncode == 0


def test_reports_all_classes_at_once(tmp_path, clean_env):
    """One run surfaces every broken class together (3 errors), not one-at-a-time."""
    # Arrange
    _base_project(
        tmp_path,
        "See \\ref{fig:99}. Cite \\cite{Missing2021}. See \\ref{supple-fig:S01}.\n",
    )
    # Act
    proc = _run(tmp_path)
    # Assert
    assert "3 errors" in proc.stdout


def test_off_level_skips(tmp_path, clean_env):
    """--level off disables the gate even with violations (exit 0)."""
    # Arrange
    _base_project(tmp_path, "See \\ref{fig:99}.\n")
    # Act
    proc = _run(tmp_path, "--level", "off")
    # Assert
    assert proc.returncode == 0


def test_warn_level_does_not_block(tmp_path, clean_env):
    """--level warn reports but exits 0 (does not block the compile)."""
    # Arrange
    _base_project(tmp_path, "See \\ref{fig:99}.\n")
    # Act
    proc = _run(tmp_path, "--level", "warn")
    # Assert
    assert proc.returncode == 0
