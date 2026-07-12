#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_utils/test__latexdiff.py

r"""Tests for the ONE latexdiff backend + the diff-document signature block.

Real ``latexdiff`` runs on real ``.tex`` files under ``tmp_path``, and the signed
diff is compiled by a real ``pdflatex`` -- a diff document that does not compile
is not a diff document. No mocks.
"""

import os
import shutil
import subprocess

import pytest

from scitex_writer._utils import _latexdiff

_OLD = (
    "\\documentclass{article}\n\\begin{document}\nHello old world.\n\\end{document}\n"
)
_NEW = (
    "\\documentclass{article}\n\\begin{document}\n"
    "Hello brand new world.\n\\end{document}\n"
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


@pytest.fixture
def diffed(tmp_path):
    """A real latexdiff output of _OLD -> _NEW; return its path."""
    old = tmp_path / "old.tex"
    new = tmp_path / "new.tex"
    old.write_text(_OLD, encoding="utf-8")
    new.write_text(_NEW, encoding="utf-8")
    return _latexdiff.run_latexdiff(old, new, tmp_path / "diff.tex")


needs_latexdiff = pytest.mark.skipif(
    shutil.which("latexdiff") is None, reason="latexdiff not installed"
)


@needs_latexdiff
class TestRunLatexdiff:
    def test_diff_marks_added_text(self, diffed):
        # Arrange
        text = diffed.read_text(encoding="utf-8")
        # Act
        marked = "\\DIFadd" in text
        # Assert
        assert marked is True

    def test_diff_marks_deleted_text(self, diffed):
        # Arrange
        text = diffed.read_text(encoding="utf-8")
        # Act
        marked = "\\DIFdel" in text
        # Assert
        assert marked is True

    def test_diff_is_a_standalone_document(self, diffed):
        # Arrange
        text = diffed.read_text(encoding="utf-8")
        # Act
        standalone = _latexdiff.BEGIN_DOCUMENT in text
        # Assert
        assert standalone is True

    def test_empty_input_fails_loud(self, tmp_path):
        # Arrange
        old = tmp_path / "old.tex"
        new = tmp_path / "new.tex"
        old.write_text("", encoding="utf-8")
        new.write_text("", encoding="utf-8")
        # Act
        # Assert
        with pytest.raises(_latexdiff.LatexdiffFailedError, match="EMPTY document"):
            _latexdiff.run_latexdiff(old, new, tmp_path / "diff.tex")

    def test_fragment_input_yields_no_compilable_document(self, tmp_path):
        # Arrange -- latexdiff HAPPILY diffs bare fragments; the resulting file is
        # not a document, and the signature stage is what refuses it (below).
        old = tmp_path / "old.tex"
        new = tmp_path / "new.tex"
        old.write_text("just a fragment\n", encoding="utf-8")
        new.write_text("another fragment\n", encoding="utf-8")
        # Act
        diff = _latexdiff.run_latexdiff(old, new, tmp_path / "diff.tex")
        # Assert
        assert _latexdiff.BEGIN_DOCUMENT not in diff.read_text(encoding="utf-8")


@needs_latexdiff
class TestAddSignature:
    def test_signature_records_the_compared_versions(self, diffed):
        # Arrange
        _latexdiff.add_signature(diffed, "aaaaaaa", "bbbbbbb", doc_type="manuscript")
        # Act
        text = diffed.read_text(encoding="utf-8")
        # Assert
        assert "%% Comparison: vaaaaaaa → vbbbbbbb" in text

    def test_signature_lands_before_begin_document(self, diffed):
        # Arrange
        _latexdiff.add_signature(diffed, "aaaaaaa", "bbbbbbb")
        text = diffed.read_text(encoding="utf-8")
        # Act
        signature_first = text.index("\\fancypagestyle{diffstyle}") < text.index(
            _latexdiff.BEGIN_DOCUMENT
        )
        # Assert
        assert signature_first is True

    def test_typeset_header_uses_math_arrow_not_unicode(self, diffed):
        # Arrange
        _latexdiff.add_signature(diffed, "aaaaaaa", "bbbbbbb")
        text = diffed.read_text(encoding="utf-8")
        # Act
        header = [ln for ln in text.splitlines() if "\\fancyhead[L]" in ln][0]
        # Assert
        assert "$\\rightarrow$" in header

    def test_signature_records_the_document_type(self, diffed):
        # Arrange
        _latexdiff.add_signature(diffed, "aaaaaaa", "bbbbbbb", doc_type="supplementary")
        # Act
        text = diffed.read_text(encoding="utf-8")
        # Assert
        assert "%% Document: supplementary" in text

    def test_fragment_without_begin_document_fails_loud(self, tmp_path):
        # Arrange
        fragment = tmp_path / "fragment.tex"
        fragment.write_text("\\section{Nope}\n", encoding="utf-8")
        # Act
        # Assert
        with pytest.raises(_latexdiff.LatexdiffFailedError, match="not a standalone"):
            _latexdiff.add_signature(fragment, "a", "b")


class TestFailLoud:
    def test_missing_latexdiff_raises_install_hint(self, empty_path):
        # Arrange
        # (``empty_path`` points PATH at an empty dir for the duration.)
        # Act
        # Assert
        with pytest.raises(
            _latexdiff.LatexdiffUnavailableError, match="apt-get install latexdiff"
        ):
            _latexdiff.require_latexdiff()


@pytest.mark.skipif(
    shutil.which("latexdiff") is None or shutil.which("pdflatex") is None,
    reason="latexdiff and pdflatex are both required",
)
class TestRealCompile:
    def test_signed_diff_document_compiles_to_pdf(self, tmp_path, diffed):
        # Arrange
        _latexdiff.add_signature(diffed, "aaaaaaa", "bbbbbbb", author="Tester")
        # Act
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", diffed.name],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )
        # Assert
        assert (tmp_path / "diff.pdf").exists()
