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

    def test_import_callable_validate_before_compile(self):
        """Test that validate_before_compile can be imported."""
        # Arrange
        # Act
        # Assert
        assert callable(validate_before_compile)

    def test_validate_nonexistent_directory(self):
        """Test validation fails for non-existent directory."""
        # Arrange
        # Act
        project_dir = Path("/tmp/nonexistent-project-12345")
        # Assert
        with pytest.raises(Exception):
            validate_before_compile(project_dir)

    def test_validate_accepts_path_object_without_type_error(self):
        """validate_before_compile accepts a Path argument (no TypeError).

        A missing/invalid project may raise validation errors — that's
        fine; the contract under test is that passing a Path is itself
        accepted (no TypeError about the argument type).
        """
        # Arrange
        project_dir = Path("/tmp/test")
        raised_type_error = False
        # Act
        try:
            validate_before_compile(project_dir)
        except TypeError:
            raised_type_error = True
        except Exception:
            # Validation-level errors are acceptable for this contract.
            pass
        # Assert
        assert raised_type_error is False


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
