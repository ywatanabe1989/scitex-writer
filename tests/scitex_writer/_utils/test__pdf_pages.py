#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: src/scitex_writer/_utils/_pdf_pages.py

"""Page counting is the line between "produced a PDF" and "produced nothing".

The compile path promotes a PDF on a non-zero engine exit ONLY when it has
pages > 0, so these tests use REAL artifacts: a PDF actually compiled by
pdflatex, and a real pdfTeX log, never a stand-in.
"""

import shutil
import subprocess

import pytest

from scitex_writer._utils._pdf_pages import (
    pages_from_latex_log,
    pages_in_pdf,
    produced_page_count,
)


def _compile_pdf(tmp_path, pages: int):
    """Compile a REAL n-page PDF with pdflatex; return (pdf_path, log_path)."""
    body = "\n\\newpage\n".join(f"Page {n}" for n in range(1, pages + 1))
    tex = tmp_path / "doc.tex"
    tex.write_text(
        f"\\documentclass{{article}}\n\\begin{{document}}\n{body}\n\\end{{document}}\n"
    )
    subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "doc.tex"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    return tmp_path / "doc.pdf", tmp_path / "doc.log"


needs_pdflatex = pytest.mark.skipif(
    shutil.which("pdflatex") is None, reason="pdflatex not installed"
)


class TestPagesFromLatexLog:
    """The pdfTeX "Output written on" line is the per-run page-count evidence."""

    @needs_pdflatex
    def test_reads_page_count_from_real_pdflatex_log(self, tmp_path):
        # Arrange
        _pdf, log = _compile_pdf(tmp_path, pages=3)
        # Act
        pages = pages_from_latex_log(log)
        # Assert
        assert pages == 3

    def test_returns_zero_when_log_has_no_output_written_line(self, tmp_path):
        # Arrange
        log = tmp_path / "doc.log"
        log.write_text(
            "! LaTeX Error: File `nope.sty' not found.\nNo pages of output.\n"
        )
        # Act
        pages = pages_from_latex_log(log)
        # Assert
        assert pages == 0

    def test_returns_zero_when_log_is_missing(self, tmp_path):
        # Arrange
        missing = tmp_path / "absent.log"
        # Act
        pages = pages_from_latex_log(missing)
        # Assert
        assert pages == 0


class TestPagesInPdf:
    """Byte-scanning the PDF is the fallback when the log is gone."""

    @needs_pdflatex
    def test_counts_pages_of_a_real_compiled_pdf(self, tmp_path):
        # Arrange
        pdf, _log = _compile_pdf(tmp_path, pages=2)
        # Act
        pages = pages_in_pdf(pdf)
        # Assert
        assert pages == 2

    def test_returns_zero_for_a_missing_pdf(self, tmp_path):
        # Arrange
        missing = tmp_path / "absent.pdf"
        # Act
        pages = pages_in_pdf(missing)
        # Assert
        assert pages == 0

    def test_returns_zero_for_a_truncated_pdf_husk(self, tmp_path):
        # Arrange: an aborted run can leave a header-only file with no page object
        husk = tmp_path / "husk.pdf"
        husk.write_bytes(b"%PDF-1.5\n")
        # Act
        pages = pages_in_pdf(husk)
        # Assert
        assert pages == 0


class TestProducedPageCount:
    """produced_page_count is what the compile path gates promotion on."""

    @needs_pdflatex
    def test_counts_pages_of_a_produced_pdf(self, tmp_path):
        # Arrange
        pdf, log = _compile_pdf(tmp_path, pages=4)
        # Act
        pages = produced_page_count(pdf, log)
        # Assert
        assert pages == 4

    @needs_pdflatex
    def test_falls_back_to_pdf_bytes_when_log_absent(self, tmp_path):
        # Arrange
        pdf, log = _compile_pdf(tmp_path, pages=2)
        log.unlink()
        # Act
        pages = produced_page_count(pdf, log)
        # Assert
        assert pages == 2

    def test_reports_zero_when_no_pdf_was_produced(self, tmp_path):
        # Arrange: the log claims pages, but the artifact does not exist —
        # a missing PDF is ALWAYS zero, so a failed compile cannot be promoted.
        log = tmp_path / "doc.log"
        log.write_text("Output written on doc.pdf (7 pages, 129061 bytes).\n")
        # Act
        pages = produced_page_count(tmp_path / "doc.pdf", log)
        # Assert
        assert pages == 0


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__), "-v"])
