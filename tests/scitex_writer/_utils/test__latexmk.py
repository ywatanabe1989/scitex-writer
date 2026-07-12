#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_utils/test__latexmk.py

"""Tests for the ONE LaTeX compile backend behind the diff pipeline.

Real ``latexmk`` runs on real ``.tex`` sources under ``tmp_path``; a source with a
real LaTeX error really fails. No mocks.
"""

import os
import shutil

import pytest

from scitex_writer._utils import _latexmk

_GOOD = "\\documentclass{article}\n\\begin{document}\nHello.\n\\end{document}\n"
_BROKEN = "\\documentclass{article}\n\\begin{document}\n\\undefinedmacro\n"

needs_latexmk = pytest.mark.skipif(
    shutil.which("latexmk") is None, reason="latexmk not installed"
)


@pytest.fixture
def empty_path(tmp_path):
    """Point PATH at an EMPTY directory, so no binary resolves (real env seam)."""
    previous = os.environ.get("PATH", "")
    (tmp_path / "empty-bin").mkdir()
    os.environ["PATH"] = str(tmp_path / "empty-bin")
    try:
        yield os.environ["PATH"]
    finally:
        os.environ["PATH"] = previous


@needs_latexmk
class TestCompileTex:
    def test_valid_source_produces_pdf_in_output_dir(self, tmp_path):
        # Arrange
        tex = tmp_path / "doc.tex"
        tex.write_text(_GOOD, encoding="utf-8")
        # Act
        pdf = _latexmk.compile_tex(tex, tmp_path / "logs", project_root=tmp_path)
        # Assert
        assert pdf == tmp_path / "logs" / "doc.pdf"

    def test_pdf_is_written_and_non_empty(self, tmp_path):
        # Arrange
        tex = tmp_path / "doc.tex"
        tex.write_text(_GOOD, encoding="utf-8")
        # Act
        pdf = _latexmk.compile_tex(tex, tmp_path / "logs", project_root=tmp_path)
        # Assert
        assert pdf.stat().st_size > 0

    def test_nothing_is_written_beside_the_source(self, tmp_path):
        # Arrange
        tex = tmp_path / "doc.tex"
        tex.write_text(_GOOD, encoding="utf-8")
        # Act
        _latexmk.compile_tex(tex, tmp_path / "logs", project_root=tmp_path)
        # Assert
        assert not (tmp_path / "doc.pdf").exists()

    def test_broken_source_fails_loud(self, tmp_path):
        # Arrange
        tex = tmp_path / "doc.tex"
        tex.write_text(_BROKEN, encoding="utf-8")
        # Act
        # Assert
        with pytest.raises(_latexmk.LatexmkFailedError, match="latexmk exited"):
            _latexmk.compile_tex(tex, tmp_path / "logs", project_root=tmp_path)

    def test_absent_source_fails_loud(self, tmp_path):
        # Arrange
        tex = tmp_path / "absent.tex"
        # Act
        # Assert
        with pytest.raises(_latexmk.LatexmkFailedError, match="TeX source not found"):
            _latexmk.compile_tex(tex, tmp_path / "logs", project_root=tmp_path)


class TestFailLoud:
    def test_missing_latexmk_raises_install_hint(self, empty_path):
        # Arrange
        # (``empty_path`` points PATH at an empty dir for the duration.)
        # Act
        # Assert
        with pytest.raises(_latexmk.LatexmkUnavailableError, match="apt-get install"):
            _latexmk.require_latexmk()

    def test_default_timeout_is_the_shell_default(self):
        # Arrange
        expected = 120
        # Act
        actual = _latexmk.DEFAULT_TIMEOUT_SEC
        # Assert
        assert actual == expected
