#!/usr/bin/env python3
"""Tests for scitex_writer._utils._parse_latex_logs."""

from pathlib import Path

import pytest

from scitex_writer._dataclasses import LaTeXIssue
from scitex_writer._utils._parse_latex_logs import parse_compilation_output


class TestParseCompilationOutputErrors:
    """Tests for parse_compilation_output error detection."""

    def test_parses_error_with_exclamation(self):
        """Verify errors starting with '!' are detected."""
        # Arrange
        output = "! Undefined control sequence."
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert (len(errors) == 1) and (errors[0].type == 'error') and ('Undefined control sequence' in errors[0].message)

    def test_parses_multiple_errors(self):
        """Verify multiple errors are detected."""
        # Arrange
        output = """! First error
Some other text
! Second error
! Third error"""
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert len(errors) == 3

    def test_skips_empty_error_lines(self):
        """Verify empty error lines are skipped."""
        # Arrange
        output = "!\n! Actual error"
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert (len(errors) == 1) and (errors[0].message == 'Actual error')

    def test_error_type_is_error(self):
        """Verify error issues have type='error'."""
        # Arrange
        output = "! LaTeX Error: Something went wrong."
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert errors[0].type == "error"


class TestParseCompilationOutputWarnings:
    """Tests for parse_compilation_output warning detection."""

    def test_parses_lowercase_warning(self):
        """Verify lowercase 'warning' is detected."""
        # Arrange
        output = "Package natbib warning: Citation undefined."
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert (len(warnings) == 1) and (warnings[0].type == 'warning')

    def test_parses_uppercase_warning(self):
        """Verify uppercase 'Warning' is detected."""
        # Arrange
        output = "LaTeX Warning: Reference undefined."
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert len(warnings) == 1

    def test_parses_mixed_case_warning(self):
        """Verify mixed case 'WARNING' is detected."""
        # Arrange
        output = "PACKAGE WARNING: Something not quite right."
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert len(warnings) == 1

    def test_parses_multiple_warnings(self):
        """Verify multiple warnings are detected."""
        # Arrange
        output = """LaTeX Warning: First warning
Some text
Package warning: Second warning"""
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert len(warnings) == 2


class TestParseCompilationOutputMixed:
    """Tests for parse_compilation_output with mixed errors and warnings."""

    def test_separates_errors_and_warnings(self):
        """Verify errors and warnings are separated correctly."""
        # Arrange
        output = """! Error happened
LaTeX Warning: Warning happened
! Another error
Package warning: Another warning"""
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert (len(errors) == 2) and (len(warnings) == 2)

    def test_empty_output_returns_empty_lists(self):
        """Verify empty output returns empty lists."""
        # Arrange
        output = ""
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert (errors == []) and (warnings == [])

    def test_no_issues_returns_empty_lists(self):
        """Verify output without issues returns empty lists."""
        # Arrange
        output = """Processing document.tex
Running pdflatex...
Output written to document.pdf"""
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert (errors == []) and (warnings == [])


class TestParseCompilationOutputLogFile:
    """Tests for parse_compilation_output log_file parameter."""

    def test_log_file_parameter_is_optional(self):
        """Verify log_file parameter is optional."""
        # Arrange
        output = "! Error"
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert len(errors) == 1

    def test_log_file_parameter_is_ignored(self):
        """Verify log_file parameter is ignored (for compatibility)."""
        # Arrange
        output = "! Error"
        log_file = Path("/some/path/document.log")
        # Act
        errors, warnings = parse_compilation_output(output, log_file)

        # Assert
        assert len(errors) == 1


class TestParseCompilationOutputIssueObjects:
    """Tests for LaTeXIssue objects returned by parse_compilation_output."""

    def test_returns_latex_issue_for_errors(self):
        """Verify errors are LaTeXIssue objects."""
        # Arrange
        output = "! Test error"
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert isinstance(errors[0], LaTeXIssue)

    def test_returns_latex_issue_for_warnings(self):
        """Verify warnings are LaTeXIssue objects."""
        # Arrange
        output = "Package warning: Test warning"
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert isinstance(warnings[0], LaTeXIssue)

    def test_error_message_strips_exclamation(self):
        """Verify error message has exclamation stripped."""
        # Arrange
        output = "! Test error message"
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert (errors[0].message == 'Test error message') and (not errors[0].message.startswith('!'))

    def test_warning_message_includes_full_line(self):
        """Verify warning message includes full line."""
        # Arrange
        output = "LaTeX Warning: Reference 'fig:test' on page 1 undefined."
        # Act
        errors, warnings = parse_compilation_output(output)

        # Assert
        assert ('LaTeX Warning' in warnings[0].message) and ('fig:test' in warnings[0].message)


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
