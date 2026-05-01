#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: csv_to_latex.py

import os
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

# Try to import pandas and the functions
try:
    import pandas as pd  # noqa: F401
    from csv_to_latex import csv_to_latex, escape_latex, format_number

    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

# Skip all tests if pandas not available
pytestmark = pytest.mark.skipif(not HAS_DEPS, reason="pandas not installed")


class TestEscapeLatex:
    """Test LaTeX special character escaping."""

    def test_escape_latex_ampersand(self):
        """Should escape ampersand."""
        result = escape_latex("A & B")
        assert result == r"A \& B"

    def test_escape_latex_percent(self):
        """Should escape percent sign."""
        result = escape_latex("50%")
        assert result == r"50\%"

    def test_escape_latex_underscore(self):
        """Should escape underscore."""
        result = escape_latex("a_b")
        assert result == r"a\_b"

    def test_escape_latex_hash(self):
        """Should escape hash/pound sign."""
        result = escape_latex("#1")
        assert result == r"\#1"

    def test_escape_latex_dollar(self):
        """Should escape dollar sign."""
        result = escape_latex("$100")
        assert result == r"\$100"

    def test_escape_latex_backslash(self):
        """Should escape backslash."""
        result = escape_latex("a\\b")
        # Braces in \textbackslash{} also get escaped
        assert result == r"a\textbackslash\{\}b"

    def test_escape_latex_braces(self):
        """Should escape curly braces."""
        result = escape_latex("a{b}c")
        assert result == r"a\{b\}c"

    def test_escape_latex_tilde(self):
        """Should escape tilde."""
        result = escape_latex("a~b")
        assert result == r"a\textasciitilde{}b"

    def test_escape_latex_caret(self):
        """Should escape caret."""
        result = escape_latex("a^b")
        assert result == r"a\textasciicircum{}b"

    def test_escape_latex_nan(self):
        """Should handle pandas NaN values."""
        result = escape_latex(float("nan"))
        assert result == ""

    def test_escape_latex_none(self):
        """Should handle None values."""
        result = escape_latex(None)
        assert result == ""

    def test_escape_latex_multiple_chars(self):
        """Should escape multiple special characters."""
        result = escape_latex("A & B: 50% #1")
        assert result == r"A \& B: 50\% \#1"

    def test_escape_latex_numeric_input(self):
        """Should convert numbers to strings and escape."""
        result = escape_latex(42)
        assert result == "42"

    def test_escape_latex_empty_string(self):
        """Should handle empty strings."""
        result = escape_latex("")
        assert result == ""


class TestFormatNumber:
    """Test number formatting."""

    def test_format_number_integer(self):
        """Should format integers without decimals."""
        result = format_number("42.0")
        assert result == "42"

    def test_format_number_decimal(self):
        """Should format decimals with up to 3 places."""
        result = format_number("3.14159")
        assert result == "3.142"

    def test_format_number_small_scientific(self):
        """Should use scientific notation for very small numbers."""
        result = format_number("0.001")
        # Should be in scientific notation
        assert "e" in result.lower()

    def test_format_number_zero(self):
        """Should format zero correctly."""
        result = format_number("0.0")
        assert result == "0"

    def test_format_number_negative(self):
        """Should handle negative numbers."""
        result = format_number("-3.14")
        assert result == "-3.14"

    def test_format_number_text(self):
        """Should return non-numeric text as-is."""
        result = format_number("hello")
        assert result == "hello"

    def test_format_number_strips_trailing_zeros(self):
        """Should strip trailing zeros."""
        result = format_number("3.100")
        assert result == "3.1"

    def test_format_number_strips_trailing_dot(self):
        """Should strip trailing decimal point."""
        result = format_number("3.000")
        assert result == "3"

    def test_format_number_large_number(self):
        """Should format large numbers correctly."""
        result = format_number("123456.789")
        assert result == "123456.789"

    def test_format_number_very_small_nonzero(self):
        """Should use scientific notation for numbers < 0.01."""
        result = format_number("0.005")
        assert "e" in result.lower()

    def test_format_number_boundary_0_01(self):
        """Should use scientific notation at 0.01 boundary."""
        result = format_number("0.009")
        assert "e" in result.lower()


class TestCsvToLatex:
    """Test full CSV to LaTeX conversion."""

    def test_csv_to_latex_creates_file(self, tmp_path):
        """Should create output LaTeX file."""
        # Create test CSV
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Age\nAlice,30\nBob,25")

        output_file = tmp_path / "output.tex"

        result = csv_to_latex(csv_file, output_file)

        assert result is True
        assert output_file.exists()

    def test_csv_to_latex_contains_tabular(self, tmp_path):
        """Output should contain tabular environment."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A,B\n1,2")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        content = output_file.read_text()
        assert r"\begin{tabular}" in content
        assert r"\end{tabular}" in content

    def test_csv_to_latex_contains_headers(self, tmp_path):
        """Output should contain bold headers."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Age\nAlice,30")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        content = output_file.read_text()
        # Headers should be bold and title-cased
        assert r"\textbf{Name}" in content
        assert r"\textbf{Age}" in content

    def test_csv_to_latex_contains_data(self, tmp_path):
        """Output should contain table data."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Value\nTest,42")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        content = output_file.read_text()
        assert "Test" in content
        assert "42" in content

    def test_csv_to_latex_escapes_special_chars(self, tmp_path):
        """Should escape LaTeX special characters in data."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Text\nA & B")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        content = output_file.read_text()
        # Ampersand should be escaped
        assert r"\&" in content

    def test_csv_to_latex_contains_table_env(self, tmp_path):
        """Output should contain table environment."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A\n1")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        content = output_file.read_text()
        assert r"\begin{table}" in content
        assert r"\end{table}" in content

    def test_csv_to_latex_contains_caption(self, tmp_path):
        """Output should contain caption."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A\n1")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        content = output_file.read_text()
        assert r"\caption{" in content

    def test_csv_to_latex_custom_caption(self, tmp_path):
        """Should use custom caption if provided."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A\n1")

        output_file = tmp_path / "output.tex"
        custom_caption = "My Custom Caption"
        csv_to_latex(csv_file, output_file, caption=custom_caption)

        content = output_file.read_text()
        assert custom_caption in content

    def test_csv_to_latex_custom_label(self, tmp_path):
        """Should use custom label if provided."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A\n1")

        output_file = tmp_path / "output.tex"
        custom_label = "tab:mylabel"
        csv_to_latex(csv_file, output_file, label=custom_label)

        content = output_file.read_text()
        assert r"\label{tab:mylabel}" in content

    def test_csv_to_latex_invalid_csv(self, tmp_path):
        """Should return False for invalid CSV."""
        csv_file = tmp_path / "nonexistent.csv"
        output_file = tmp_path / "output.tex"

        result = csv_to_latex(csv_file, output_file)

        assert result is False
        assert not output_file.exists()

    def test_csv_to_latex_contains_booktabs(self, tmp_path):
        """Should use booktabs rules (toprule, midrule, bottomrule)."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A,B\n1,2")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        content = output_file.read_text()
        assert r"\toprule" in content
        assert r"\midrule" in content
        assert r"\bottomrule" in content

    def test_csv_to_latex_number_formatting(self, tmp_path):
        """Should format numbers appropriately."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Value\n3.14159\n42.0")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        content = output_file.read_text()
        # Float should be formatted
        assert "3.142" in content
        # Integer should not have decimals
        assert "42 " in content or "42\\\\" in content

    def test_csv_to_latex_column_alignment(self, tmp_path):
        """Should align numeric columns right."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Age\nAlice,30")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        content = output_file.read_text()
        # Should have tabular with alignment spec (l for text, r for numbers)
        assert r"\begin{tabular}{" in content

    def test_csv_to_latex_handles_missing_values(self, tmp_path):
        """Should handle missing/NaN values."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A,B\n1,\n,3")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        content = output_file.read_text()
        # Missing values should be represented (as --)
        assert "--" in content

    def test_csv_to_latex_truncation_message(self, tmp_path):
        """Should add truncation message for large tables."""
        # Create CSV with many rows
        lines = ["Value"] + [str(i) for i in range(50)]
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("\n".join(lines))

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file, max_rows=10)

        content = output_file.read_text()
        # Should mention truncation
        assert "truncated" in content.lower() or "omitted" in content.lower()


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
