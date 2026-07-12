#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_utils/test__csv_table.py

r"""Tests for the single pandas CSV -> LaTeX table backend.

The verbatim-passthrough cases are the regression guard for card
writer-csv-latex-verbatim-all-backends: with ONE backend there is no longer a
path (csv2latex binary / AWK fallback) that can silently escape an authored
``$p<0.001$`` or ``\textit{r}``.
"""

import shutil
import subprocess

import pytest

from scitex_writer._utils._csv_table import (
    caption_title,
    is_verbatim,
    protect_verbatim,
    render_csv_table,
    split_table_name,
)

_CAPTION_WITH_LABEL = (
    "\\caption{\\textbf{Seizure counts}\\\\ Per-patient totals.}\n"
    "\\label{tab:01_seizure_count}\n"
)
_CAPTION_NO_LABEL = "\\caption{\\textbf{Seizure counts}\\\\ Per-patient totals.}\n"


def _write_csv(tmp_path, text, name="01_seizure_count.csv"):
    csv_file = tmp_path / name
    csv_file.write_text(text, encoding="utf-8")
    return csv_file


class TestVerbatimPassthrough:
    def test_math_cell_passes_through_unescaped(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "metric,value\nsignificance,$p<0.001$\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "$p<0.001$" in latex

    def test_latex_command_cell_passes_through(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "metric,value\ncorrelation,\\textit{r}\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "\\textit{r}" in latex

    def test_math_header_passes_through_unescaped(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "model,$R^2$\nlinear,0.9\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "\\textbf{$R^2$}" in latex

    def test_plain_underscore_cell_is_escaped(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "metric,value\nname,mean_iou\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "mean\\_iou" in latex

    def test_plain_ampersand_cell_is_escaped(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "metric,value\nname,A & B\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "A \\& B" in latex

    def test_is_verbatim_flags_dollar_value(self):
        # Arrange
        value = "$p<0.05$"
        # Act
        flagged = is_verbatim(value)
        # Assert
        assert flagged is True


class TestNumberFormatting:
    def test_integer_column_stays_bare(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "patient,count\nP1,288\nP2,12\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "288.000" not in latex

    def test_decimal_column_pads_to_max_precision(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "model,score\nA,0.333\nB,0.35\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "0.350" in latex

    def test_numeric_column_is_right_aligned(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "model,score\nA,0.5\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "\\begin{tabular}{lr}" in latex


class TestBookmarkAndLabel:
    def test_bookmark_carries_caption_title(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "a,b\n1,2\n")
        # Act
        latex = render_csv_table(csv_file, caption=_CAPTION_NO_LABEL)
        # Assert
        assert "\\pdfbookmark[2]{Table 1 --- Seizure counts}" in latex

    def test_bookmark_bare_number_without_caption(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "a,b\n1,2\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "\\pdfbookmark[2]{Table 1}{table_01_seizure_count}" in latex

    def test_label_omitted_when_caption_has_label(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "a,b\n1,2\n")
        # Act
        latex = render_csv_table(csv_file, caption=_CAPTION_WITH_LABEL)
        # Assert
        assert latex.count("\\label{tab:01_seizure_count}") == 1

    def test_label_emitted_when_caption_lacks_label(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "a,b\n1,2\n")
        # Act
        latex = render_csv_table(csv_file, caption=_CAPTION_NO_LABEL)
        # Assert
        assert "\\label{tab:01_seizure_count}" in latex

    def test_default_caption_generated_without_caption(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "a,b\n1,2\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "\\caption{\\textbf{Table 1: seizure count}" in latex

    def test_caption_title_reads_textbf_block(self):
        # Arrange
        caption = _CAPTION_NO_LABEL
        # Act
        title = caption_title(caption)
        # Assert
        assert title == "Seizure counts"

    def test_split_table_name_strips_leading_zeros(self):
        # Arrange
        base_name = "01_seizure_count"
        # Act
        number, clean = split_table_name(base_name)
        # Assert
        assert (number, clean) == ("1", "seizure count")


class TestTruncation:
    def test_long_table_emits_omitted_rows_marker(self, tmp_path):
        # Arrange
        rows = "\n".join(f"P{i},{i}" for i in range(40))
        csv_file = _write_csv(tmp_path, f"patient,count\n{rows}\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "rows omitted" in latex

    def test_long_table_notes_truncation_in_caption(self, tmp_path):
        # Arrange
        rows = "\n".join(f"P{i},{i}" for i in range(40))
        csv_file = _write_csv(tmp_path, f"patient,count\n{rows}\n")
        # Act
        latex = render_csv_table(csv_file, caption=_CAPTION_NO_LABEL)
        # Assert
        assert "Note: Table truncated to 30 rows from 40 total rows" in latex


class TestMixedCellProtection:
    r"""A cell mixing prose and math is verbatim, but its ``%`` / ``&`` must
    still be escaped: a bare ``%`` comments out the rest of the LaTeX row
    (swallowing its ``\\`` terminator and the next row with it), and a bare
    ``&`` opens a phantom column. Both corrupt SILENTLY -- the table renders
    wrong rather than failing.
    """

    def test_percent_beside_math_is_escaped(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "metric,value\nrate,5% ($p<0.05$)\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "5\\% ($p<0.05$)" in latex

    def test_math_survives_beside_the_escaped_percent(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "metric,value\nrate,5% ($p<0.05$)\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "$p<0.05$" in latex

    def test_ampersand_beside_math_is_escaped(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "metric,value\ngroups,A & B ($n=3$)\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "A \\& B ($n=3$)" in latex

    def test_already_escaped_percent_is_not_double_escaped(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "metric,value\nrate,5\\% ($p<0.05$)\n")
        # Act
        latex = render_csv_table(csv_file)
        # Assert
        assert "\\\\%" not in latex

    def test_protect_verbatim_leaves_pure_math_untouched(self):
        # Arrange
        cell = "$p<0.001$"
        # Act
        protected = protect_verbatim(cell)
        # Assert
        assert protected == cell

    def test_clew_macro_cell_survives_protection(self):
        # Arrange
        cell = "\\clewval{seizure_rate}"
        # Act
        protected = protect_verbatim(cell)
        # Assert
        assert protected == cell


@pytest.mark.skipif(shutil.which("pdflatex") is None, reason="pdflatex not installed")
class TestRealCompile:
    def test_mixed_percent_math_table_compiles_to_pdf(self, tmp_path):
        # Arrange
        csv_file = _write_csv(tmp_path, "metric,value\nrate,5% ($p<0.05$)\n")
        body = render_csv_table(csv_file, caption=_CAPTION_NO_LABEL)
        doc = tmp_path / "doc.tex"
        # The fragment uses \toprule (booktabs), \resizebox (graphicx),
        # \captionsetup (caption) and \pdfbookmark (hyperref) — the real
        # manuscript loads these via 00_shared/latex_styles/packages.tex.
        doc.write_text(
            "\\documentclass{article}\n"
            "\\usepackage{booktabs}\n"
            "\\usepackage{graphicx}\n"
            "\\usepackage{caption}\n"
            "\\usepackage{hyperref}\n"
            "\\begin{document}\n"
            f"{body}\n\\end{{document}}\n",
            encoding="utf-8",
        )
        # Act
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", doc.name],
            cwd=tmp_path,
            capture_output=True,
            check=True,
        )
        # Assert
        assert (tmp_path / "doc.pdf").exists()


class TestFailLoud:
    def test_missing_csv_raises_file_not_found(self, tmp_path):
        # Arrange
        absent = tmp_path / "99_absent.csv"
        # Act
        render = lambda: render_csv_table(absent)  # noqa: E731
        # Assert
        with pytest.raises(FileNotFoundError, match="CSV file not found"):
            render()


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
