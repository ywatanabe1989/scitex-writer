#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for compilation output parser.

Tests parse_output function for extracting errors and warnings.
"""

import pytest

pytest.importorskip("git")
from pathlib import Path

from scitex_writer._compile._parser import parse_output


class TestParseOutput:
    """Test suite for parse_output function."""

    def test_import(self):
        """Test that parse_output can be imported."""
        assert callable(parse_output)

    def test_parse_empty_output(self):
        """Test parsing empty output returns empty lists."""
        errors, warnings = parse_output("", "")
        assert errors == []
        assert warnings == []

    def test_parse_output_with_no_log_file(self):
        """Test parsing without log file."""
        stdout = "Compilation successful"
        stderr = ""
        errors, warnings = parse_output(stdout, stderr, log_file=None)
        assert isinstance(errors, list)
        assert isinstance(warnings, list)

    def test_parse_output_with_log_file(self):
        """Test parsing with log file path."""
        stdout = "Compilation successful"
        stderr = ""
        log_file = Path("/tmp/test.log")
        errors, warnings = parse_output(stdout, stderr, log_file=log_file)
        assert isinstance(errors, list)
        assert isinstance(warnings, list)


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
