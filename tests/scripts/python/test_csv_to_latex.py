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

pytest.importorskip("pandas")

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
        # Arrange
        # Act
        result = escape_latex("A & B")
        # Assert
        assert result == r"A \& B"

    def test_escape_latex_percent(self):
        """Should escape percent sign."""
        # Arrange
        # Act
        result = escape_latex("50%")
        # Assert
        assert result == r"50\%"

    def test_escape_latex_underscore(self):
        """Should escape underscore."""
        # Arrange
        # Act
        result = escape_latex("a_b")
        # Assert
        assert result == r"a\_b"

    def test_escape_latex_hash(self):
        """Should escape hash/pound sign."""
        # Arrange
        # Act
        result = escape_latex("#1")
        # Assert
        assert result == r"\#1"

    def test_escape_latex_dollar(self):
        """Should escape dollar sign."""
        # Arrange
        # Act
        result = escape_latex("$100")
        # Assert
        assert result == r"\$100"

    def test_escape_latex_backslash(self):
        """Should escape backslash."""
        # Arrange
        # Act
        result = escape_latex("a\\b")
        # Braces in \textbackslash{} also get escaped
        # Assert
        assert result == r"a\textbackslash\{\}b"

    def test_escape_latex_braces(self):
        """Should escape curly braces."""
        # Arrange
        # Act
        result = escape_latex("a{b}c")
        # Assert
        assert result == r"a\{b\}c"

    def test_escape_latex_tilde(self):
        """Should escape tilde."""
        # Arrange
        # Act
        result = escape_latex("a~b")
        # Assert
        assert result == r"a\textasciitilde{}b"

    def test_escape_latex_caret(self):
        """Should escape caret."""
        # Arrange
        # Act
        result = escape_latex("a^b")
        # Assert
        assert result == r"a\textasciicircum{}b"

    def test_escape_latex_nan(self):
        """Should handle pandas NaN values."""
        # Arrange
        # Act
        result = escape_latex(float("nan"))
        # Assert
        assert result == ""

    def test_escape_latex_none(self):
        """Should handle None values."""
        # Arrange
        # Act
        result = escape_latex(None)
        # Assert
        assert result == ""

    def test_escape_latex_multiple_chars(self):
        """Should escape multiple special characters."""
        # Arrange
        # Act
        result = escape_latex("A & B: 50% #1")
        # Assert
        assert result == r"A \& B: 50\% \#1"

    def test_escape_latex_numeric_input(self):
        """Should convert numbers to strings and escape."""
        # Arrange
        # Act
        result = escape_latex(42)
        # Assert
        assert result == "42"

    def test_escape_latex_empty_string(self):
        """Should handle empty strings."""
        # Arrange
        # Act
        result = escape_latex("")
        # Assert
        assert result == ""


class TestFormatNumber:
    """Test number formatting."""

    def test_format_number_integer(self):
        """Should format integers without decimals."""
        # Arrange
        # Act
        result = format_number("42.0")
        # Assert
        assert result == "42"

    def test_format_number_decimal(self):
        """Should format decimals with up to 3 places."""
        # Arrange
        # Act
        result = format_number("3.14159")
        # Assert
        assert result == "3.142"

    def test_format_number_small_scientific(self):
        """Should use scientific notation for very small numbers."""
        # Arrange
        # Act
        result = format_number("0.001")
        # Should be in scientific notation
        # Assert
        assert "e" in result.lower()

    def test_format_number_zero(self):
        """Should format zero correctly."""
        # Arrange
        # Act
        result = format_number("0.0")
        # Assert
        assert result == "0"

    def test_format_number_negative(self):
        """Should handle negative numbers."""
        # Arrange
        # Act
        result = format_number("-3.14")
        # Assert
        assert result == "-3.14"

    def test_format_number_text(self):
        """Should return non-numeric text as-is."""
        # Arrange
        # Act
        result = format_number("hello")
        # Assert
        assert result == "hello"

    def test_format_number_strips_trailing_zeros(self):
        """Should strip trailing zeros."""
        # Arrange
        # Act
        result = format_number("3.100")
        # Assert
        assert result == "3.1"

    def test_format_number_strips_trailing_dot(self):
        """Should strip trailing decimal point."""
        # Arrange
        # Act
        result = format_number("3.000")
        # Assert
        assert result == "3"

    def test_format_number_large_number(self):
        """Should format large numbers correctly."""
        # Arrange
        # Act
        result = format_number("123456.789")
        # Assert
        assert result == "123456.789"

    def test_format_number_very_small_nonzero(self):
        """Should use scientific notation for numbers < 0.01."""
        # Arrange
        # Act
        result = format_number("0.005")
        # Assert
        assert "e" in result.lower()

    def test_format_number_boundary_0_01(self):
        """Should use scientific notation at 0.01 boundary."""
        # Arrange
        # Act
        result = format_number("0.009")
        # Assert
        assert "e" in result.lower()


class TestCsvToLatex:
    """Test full CSV to LaTeX conversion."""

    def test_csv_to_latex_creates_file(self, tmp_path):
        """Should create output LaTeX file."""
        # Create test CSV
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Age\nAlice,30\nBob,25")

        output_file = tmp_path / "output.tex"

        # Act
        result = csv_to_latex(csv_file, output_file)

        # Assert
        assert (result is True) and (output_file.exists())

    def test_csv_to_latex_contains_tabular(self, tmp_path):
        """Output should contain tabular environment."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A,B\n1,2")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        # Act
        content = output_file.read_text()
        # Assert
        assert ('\\begin{tabular}' in content) and ('\\end{tabular}' in content)

    def test_csv_to_latex_contains_headers(self, tmp_path):
        """Output should contain bold headers."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Age\nAlice,30")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        # Act
        content = output_file.read_text()
        # Headers should be bold and title-cased
        # Assert
        assert ('\\textbf{Name}' in content) and ('\\textbf{Age}' in content)

    def test_csv_to_latex_contains_data(self, tmp_path):
        """Output should contain table data."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Value\nTest,42")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        # Act
        content = output_file.read_text()
        # Assert
        assert ('Test' in content) and ('42' in content)

    def test_csv_to_latex_escapes_special_chars(self, tmp_path):
        """Should escape LaTeX special characters in data."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Text\nA & B")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        # Act
        content = output_file.read_text()
        # Ampersand should be escaped
        # Assert
        assert r"\&" in content

    def test_csv_to_latex_contains_table_env(self, tmp_path):
        """Output should contain table environment."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A\n1")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        # Act
        content = output_file.read_text()
        # Assert
        assert ('\\begin{table}' in content) and ('\\end{table}' in content)

    def test_csv_to_latex_contains_caption(self, tmp_path):
        """Output should contain caption."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A\n1")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        # Act
        content = output_file.read_text()
        # Assert
        assert r"\caption{" in content

    def test_csv_to_latex_custom_caption(self, tmp_path):
        """Should use custom caption if provided."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A\n1")

        output_file = tmp_path / "output.tex"
        custom_caption = "My Custom Caption"
        csv_to_latex(csv_file, output_file, caption=custom_caption)

        # Act
        content = output_file.read_text()
        # Assert
        assert custom_caption in content

    def test_csv_to_latex_custom_label(self, tmp_path):
        """Should use custom label if provided."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A\n1")

        output_file = tmp_path / "output.tex"
        custom_label = "tab:mylabel"
        csv_to_latex(csv_file, output_file, label=custom_label)

        # Act
        content = output_file.read_text()
        # Assert
        assert r"\label{tab:mylabel}" in content

    def test_csv_to_latex_invalid_csv(self, tmp_path):
        """Should return False for invalid CSV."""
        # Arrange
        csv_file = tmp_path / "nonexistent.csv"
        output_file = tmp_path / "output.tex"

        # Act
        result = csv_to_latex(csv_file, output_file)

        # Assert
        assert (result is False) and (not output_file.exists())

    def test_csv_to_latex_contains_booktabs(self, tmp_path):
        """Should use booktabs rules (toprule, midrule, bottomrule)."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A,B\n1,2")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        # Act
        content = output_file.read_text()
        # Assert
        assert ('\\toprule' in content) and ('\\midrule' in content) and ('\\bottomrule' in content)

    def test_csv_to_latex_number_formatting(self, tmp_path):
        """Should format numbers appropriately."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Value\n3.14159\n42.0")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        # Act
        content = output_file.read_text()
        # Float should be formatted
        # Assert
        assert ('3.142' in content) and ('42 ' in content or '42\\\\' in content)

    def test_csv_to_latex_column_alignment(self, tmp_path):
        """Should align numeric columns right."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("Name,Age\nAlice,30")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        # Act
        content = output_file.read_text()
        # Should have tabular with alignment spec (l for text, r for numbers)
        # Assert
        assert r"\begin{tabular}{" in content

    def test_csv_to_latex_handles_missing_values(self, tmp_path):
        """Should handle missing/NaN values."""
        # Arrange
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("A,B\n1,\n,3")

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file)

        # Act
        content = output_file.read_text()
        # Missing values should be represented (as --)
        # Assert
        assert "--" in content

    def test_csv_to_latex_truncation_message(self, tmp_path):
        """Should add truncation message for large tables."""
        # Create CSV with many rows
        # Arrange
        lines = ["Value"] + [str(i) for i in range(50)]
        csv_file = tmp_path / "test.csv"
        csv_file.write_text("\n".join(lines))

        output_file = tmp_path / "output.tex"
        csv_to_latex(csv_file, output_file, max_rows=10)

        # Act
        content = output_file.read_text()
        # Should mention truncation
        # Assert
        assert "truncated" in content.lower() or "omitted" in content.lower()


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
