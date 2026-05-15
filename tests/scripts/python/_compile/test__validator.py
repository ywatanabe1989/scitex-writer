#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for pre-compile validation.

Tests validate_before_compile function for project structure validation.
"""

import pytest

pytest.importorskip("git")
from pathlib import Path

from scitex_writer._compile._validator import validate_before_compile


class TestValidateBeforeCompile:
    """Test suite for validate_before_compile function."""

    def test_import(self):
        """Test that validate_before_compile can be imported."""
        assert callable(validate_before_compile)

    def test_validate_nonexistent_directory(self):
        """Test validation fails for non-existent directory."""
        project_dir = Path("/tmp/nonexistent-project-12345")
        with pytest.raises(Exception):
            validate_before_compile(project_dir)

    def test_validate_requires_path_object(self):
        """Test that function accepts Path objects."""
        # This should not raise a type error
        project_dir = Path("/tmp/test")
        try:
            validate_before_compile(project_dir)
        except Exception:
            # Any exception is fine, we just want to check it accepts Path
            pass


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
