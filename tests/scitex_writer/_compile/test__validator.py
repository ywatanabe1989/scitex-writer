#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for pre-compile validation.

Tests validate_before_compile function for project structure validation.
"""

import pytest

pytest.importorskip("git")
from pathlib import Path

from scitex_writer._compile._validator import (
    _validate_provenance,
    validate_before_compile,
)


class _StubRunner:
    """Real callable returning a canned check-result envelope.

    Injected via the ``runners=`` seam on _validate_provenance so the gate
    logic is exercised with real objects (no patching, no Mock) per the
    repo's no-mocks rule.
    """

    def __init__(self, result: dict):
        self.result = result

    def __call__(self, *args):
        return self.result


class TestValidateProvenance:
    """Test suite for the _validate_provenance compile-gate step."""

    def test_raises_when_check_at_error_with_violation(self):
        """A check returning a non-zero exit_code aborts the compile."""
        # Arrange
        err = {
            "success": True,
            "exit_code": 1,
            "stdout": "media: raw file foo.jpg",
            "summary": {"errors": 1},
        }
        runners = [("media-provenance", _StubRunner(err))]
        # Act
        # Assert
        with pytest.raises(RuntimeError):
            _validate_provenance(Path("/tmp/whatever"), runners=runners)

    def test_passes_when_no_violation(self):
        """A check at exit_code 0 does not raise."""
        # Arrange
        ok = {"success": True, "exit_code": 0, "summary": {}}
        runners = [("media-provenance", _StubRunner(ok))]
        # Act
        result = _validate_provenance(Path("/tmp/whatever"), runners=runners)
        # Assert
        assert result is None

    def test_skips_missing_check_script_without_raising(self):
        """A check whose script is absent (no exit_code) is skipped, not fatal."""
        # Arrange
        missing = {"success": False, "error": "check script not found"}
        runners = [("media-provenance", _StubRunner(missing))]
        # Act
        result = _validate_provenance(Path("/tmp/whatever"), runners=runners)
        # Assert
        assert result is None


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
