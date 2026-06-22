#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: _csv_latex.py (table width-fit / overflow-prevention behaviour)

import pytest

from scitex_writer._utils._csv_latex import _fit_tabular, csv2latex

_TABULAR = "\\begin{tabular}{l}\nx \\\\\n\\end{tabular}"


def test_fit_tabular_wraps_tabular_in_shrink_only_resizebox():
    # Arrange
    latex = _TABULAR
    # Act
    wrapped = _fit_tabular(latex)
    # Assert
    assert "\\resizebox" in wrapped and "\\ifdim\\width>\\linewidth" in wrapped


def test_fit_tabular_is_idempotent_on_second_call():
    # Arrange
    once = _fit_tabular(_TABULAR)
    # Act
    twice = _fit_tabular(once)
    # Assert
    assert twice.count("\\resizebox") == 1


def test_fit_tabular_leaves_content_without_tabular_untouched():
    # Arrange
    latex = "\\section{No table here}"
    # Act
    result = _fit_tabular(latex)
    # Assert
    assert result == latex


def _write_csv(tmp_path):
    csv = tmp_path / "d.csv"
    csv.write_text("a,b,c\n1,2,3\n4,5,6\n")
    return csv


def test_csv2latex_auto_fit_wraps_table_by_default(tmp_path):
    # Arrange
    pytest.importorskip("pandas")
    csv = _write_csv(tmp_path)
    # Act
    latex = csv2latex(csv, caption="Cap", label="tab:x")
    # Assert
    assert "\\resizebox" in latex


def test_csv2latex_auto_fit_false_leaves_table_unwrapped(tmp_path):
    # Arrange
    pytest.importorskip("pandas")
    csv = _write_csv(tmp_path)
    # Act
    latex = csv2latex(csv, auto_fit=False)
    # Assert
    assert "\\resizebox" not in latex


def test_csv2latex_longtable_is_not_wrapped(tmp_path):
    # Arrange
    pytest.importorskip("pandas")
    csv = _write_csv(tmp_path)
    # Act
    latex = csv2latex(csv, longtable=True)
    # Assert
    assert "\\resizebox" not in latex
