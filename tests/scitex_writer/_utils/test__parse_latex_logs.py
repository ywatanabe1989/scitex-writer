#!/usr/bin/env python3
"""Tests for scitex_writer._utils._parse_latex_logs."""

from pathlib import Path

import pytest

from scitex_writer._dataclasses import LaTeXIssue
from scitex_writer._utils._parse_latex_logs import parse_compilation_output


class TestParseCompilationOutputErrors:
    """Tests for parse_compilation_output error detection."""

    def test_detects_error_marked_with_exclamation_count(self):
        """Verify errors starting with '!' are detected (count)."""
        # Arrange
        output = "! Undefined control sequence."
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert len(errors) == 1

    def test_detects_error_marked_with_exclamation_type_is_error(self):
        """Verify errors starting with '!' have type='error'."""
        # Arrange
        output = "! Undefined control sequence."
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert errors[0].type == "error"

    def test_detects_error_marked_with_exclamation_message(self):
        """Verify message text is preserved for exclamation-prefixed error."""
        # Arrange
        output = "! Undefined control sequence."
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert "Undefined control sequence" in errors[0].message

    def test_detects_three_distinct_error_lines(self):
        """Verify multiple errors are detected."""
        # Arrange
        output = "\n".join(
            [
                "! First error",
                "Some other text",
                "! Second error",
                "! Third error",
            ]
        )
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert len(errors) == 3

    def test_skips_empty_error_lines_count(self):
        """Verify empty error lines are skipped (count)."""
        # Arrange
        output = "!\n! Actual error"
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert len(errors) == 1

    def test_skips_empty_error_lines_message(self):
        """Verify non-empty error line message is kept after skipping empty."""
        # Arrange
        output = "!\n! Actual error"
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert errors[0].message == "Actual error"

    def test_latex_error_message_type_is_error(self):
        """Verify '! LaTeX Error: ...' yields type='error'."""
        # Arrange
        output = "! LaTeX Error: Something went wrong."
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert errors[0].type == "error"


class TestParseCompilationOutputWarnings:
    """Tests for parse_compilation_output warning detection."""

    def test_detects_lowercase_warning_count(self):
        """Verify lowercase 'warning' is detected."""
        # Arrange
        output = "Package natbib warning: Citation undefined."
        # Act
        _errors, warnings = parse_compilation_output(output)
        # Assert
        assert len(warnings) == 1

    def test_lowercase_warning_type_is_warning(self):
        """Verify lowercase 'warning' yields type='warning'."""
        # Arrange
        output = "Package natbib warning: Citation undefined."
        # Act
        _errors, warnings = parse_compilation_output(output)
        # Assert
        assert warnings[0].type == "warning"

    def test_detects_capitalized_warning_count(self):
        """Verify capitalized 'Warning' is detected."""
        # Arrange
        output = "LaTeX Warning: Reference undefined."
        # Act
        _errors, warnings = parse_compilation_output(output)
        # Assert
        assert len(warnings) == 1

    def test_detects_uppercase_warning_count(self):
        """Verify uppercase 'WARNING' is detected."""
        # Arrange
        output = "PACKAGE WARNING: Something not quite right."
        # Act
        _errors, warnings = parse_compilation_output(output)
        # Assert
        assert len(warnings) == 1

    def test_detects_two_distinct_warning_lines(self):
        """Verify multiple warnings are detected."""
        # Arrange
        output = "\n".join(
            [
                "LaTeX Warning: First warning",
                "Some text",
                "Package warning: Second warning",
            ]
        )
        # Act
        _errors, warnings = parse_compilation_output(output)
        # Assert
        assert len(warnings) == 2


class TestParseCompilationOutputMixed:
    """Tests for parse_compilation_output with mixed errors and warnings."""

    def test_mixed_input_yields_two_errors(self):
        """Verify mixed input is parsed into the expected number of errors."""
        # Arrange
        output = "\n".join(
            [
                "! Error happened",
                "LaTeX Warning: Warning happened",
                "! Another error",
                "Package warning: Another warning",
            ]
        )
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert len(errors) == 2

    def test_mixed_input_yields_two_warnings(self):
        """Verify mixed input is parsed into the expected number of warnings."""
        # Arrange
        output = "\n".join(
            [
                "! Error happened",
                "LaTeX Warning: Warning happened",
                "! Another error",
                "Package warning: Another warning",
            ]
        )
        # Act
        _errors, warnings = parse_compilation_output(output)
        # Assert
        assert len(warnings) == 2

    def test_empty_output_returns_empty_errors_list(self):
        """Verify empty input returns an empty errors list."""
        # Arrange
        output = ""
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert errors == []

    def test_empty_output_returns_empty_warnings_list(self):
        """Verify empty input returns an empty warnings list."""
        # Arrange
        output = ""
        # Act
        _errors, warnings = parse_compilation_output(output)
        # Assert
        assert warnings == []

    def test_clean_output_returns_empty_errors_list(self):
        """Verify output without issues returns empty errors list."""
        # Arrange
        output = "\n".join(
            [
                "Processing document.tex",
                "Running pdflatex...",
                "Output written to document.pdf",
            ]
        )
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert errors == []

    def test_clean_output_returns_empty_warnings_list(self):
        """Verify output without issues returns empty warnings list."""
        # Arrange
        output = "\n".join(
            [
                "Processing document.tex",
                "Running pdflatex...",
                "Output written to document.pdf",
            ]
        )
        # Act
        _errors, warnings = parse_compilation_output(output)
        # Assert
        assert warnings == []


class TestParseCompilationOutputLogFile:
    """Tests for parse_compilation_output log_file parameter."""

    def test_log_file_parameter_is_optional(self):
        """Verify log_file parameter is optional."""
        # Arrange
        output = "! Error"
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert len(errors) == 1

    def test_explicit_log_file_path_does_not_change_count(self):
        """Verify supplying log_file path does not affect parse result."""
        # Arrange
        output = "! Error"
        log_file = Path("/some/path/document.log")
        # Act
        errors, _warnings = parse_compilation_output(output, log_file)
        # Assert
        assert len(errors) == 1


class TestParseCompilationOutputIssueObjects:
    """Tests for LaTeXIssue objects returned by parse_compilation_output."""

    def test_error_entries_are_latex_issue_instances(self):
        """Verify errors are LaTeXIssue objects."""
        # Arrange
        output = "! Test error"
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert isinstance(errors[0], LaTeXIssue)

    def test_warning_entries_are_latex_issue_instances(self):
        """Verify warnings are LaTeXIssue objects."""
        # Arrange
        output = "Package warning: Test warning"
        # Act
        _errors, warnings = parse_compilation_output(output)
        # Assert
        assert isinstance(warnings[0], LaTeXIssue)

    def test_error_message_equals_text_after_exclamation_marker(self):
        """Verify error message has the leading exclamation removed."""
        # Arrange
        output = "! Test error message"
        # Act
        errors, _warnings = parse_compilation_output(output)
        # Assert
        assert errors[0].message == "Test error message"

    def test_warning_message_preserves_phrase_latex_warning(self):
        """Verify warning message preserves the 'LaTeX Warning' phrase."""
        # Arrange
        output = "LaTeX Warning: Reference 'fig:test' on page 1 undefined."
        # Act
        _errors, warnings = parse_compilation_output(output)
        # Assert
        assert "LaTeX Warning" in warnings[0].message

    def test_warning_message_preserves_reference_token(self):
        """Verify warning message preserves the original reference token."""
        # Arrange
        output = "LaTeX Warning: Reference 'fig:test' on page 1 undefined."
        # Act
        _errors, warnings = parse_compilation_output(output)
        # Assert
        assert "fig:test" in warnings[0].message


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
