#!/usr/bin/env python3
"""Tests for scitex_writer._project._validate."""

import pytest

from scitex_writer._project._validate import validate_structure


class TestValidateStructureSuccess:
    """Tests for validate_structure when structure is valid."""

    def test_passes_with_all_required_directories_present(self, tmp_path):
        """Verify validate_structure does not raise with complete structure."""
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "03_revision").mkdir()
        # Act
        result = validate_structure(tmp_path)
        # Assert
        assert result is None

    def test_passes_with_extra_directories_present(self, tmp_path):
        """Verify validate_structure does not raise when extra directories exist."""
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "03_revision").mkdir()
        (tmp_path / "scripts").mkdir()
        (tmp_path / "shared").mkdir()
        # Act
        result = validate_structure(tmp_path)
        # Assert
        assert result is None


class TestValidateStructureFailure:
    """Tests for validate_structure when structure is invalid."""

    def test_raises_runtime_error_when_manuscript_directory_missing(self, tmp_path):
        """Verify raises RuntimeError when 01_manuscript is missing."""
        # Arrange
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "03_revision").mkdir()
        # Act
        ctx = pytest.raises(RuntimeError, match="01_manuscript")
        # Assert
        with ctx:
            validate_structure(tmp_path)

    def test_raises_runtime_error_when_supplementary_directory_missing(self, tmp_path):
        """Verify raises RuntimeError when 02_supplementary is missing."""
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "03_revision").mkdir()
        # Act
        ctx = pytest.raises(RuntimeError, match="02_supplementary")
        # Assert
        with ctx:
            validate_structure(tmp_path)

    def test_raises_runtime_error_when_revision_directory_missing(self, tmp_path):
        """Verify raises RuntimeError when 03_revision is missing."""
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "02_supplementary").mkdir()
        # Act
        ctx = pytest.raises(RuntimeError, match="03_revision")
        # Assert
        with ctx:
            validate_structure(tmp_path)

    def test_raises_runtime_error_when_all_required_directories_missing(self, tmp_path):
        """Verify raises RuntimeError when all required dirs are missing."""
        # Arrange
        # tmp_path is empty
        # Act
        ctx = pytest.raises(RuntimeError, match="01_manuscript")
        # Assert
        with ctx:
            validate_structure(tmp_path)

    def test_error_message_contains_expected_path_phrase(self, tmp_path):
        """Verify error message contains the expected directory path phrase."""
        # Arrange
        # tmp_path has no required dirs
        captured = {}

        # Act
        try:
            validate_structure(tmp_path)
        except RuntimeError as e:
            captured["msg"] = str(e)
        # Assert
        assert "expected at:" in captured.get("msg", "")


class TestValidateStructureEdgeCases:
    """Tests for validate_structure edge cases."""

    def test_file_named_like_required_directory_does_not_raise(self, tmp_path):
        """Verify does not raise when file (not directory) named like required dir exists."""
        # Arrange
        (tmp_path / "01_manuscript").write_text("not a directory")
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "03_revision").mkdir()
        # Act
        result = validate_structure(tmp_path)
        # Assert
        assert result is None

    def test_nested_project_directory_passes_with_required_dirs(self, tmp_path):
        """Verify validate_structure works with nested project directory."""
        # Arrange
        nested = tmp_path / "projects" / "my_paper"
        nested.mkdir(parents=True)
        (nested / "01_manuscript").mkdir()
        (nested / "02_supplementary").mkdir()
        (nested / "03_revision").mkdir()
        # Act
        result = validate_structure(nested)
        # Assert
        assert result is None


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
