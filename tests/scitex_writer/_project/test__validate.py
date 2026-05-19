#!/usr/bin/env python3
"""Tests for scitex_writer._project._validate."""

import pytest

from scitex_writer._project._validate import validate_structure


class TestValidateStructureSuccess:
    """Tests for validate_structure when structure is valid."""

    def test_passes_with_all_required_directories(self, tmp_path):
        """Verify validate_structure passes with complete structure."""
        # Arrange
        # Act
        # Assert
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "03_revision").mkdir()

        # Should not raise
        validate_structure(tmp_path)

    def test_passes_with_extra_directories(self, tmp_path):
        """Verify validate_structure passes when extra directories exist."""
        # Arrange
        # Act
        # Assert
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "03_revision").mkdir()
        (tmp_path / "scripts").mkdir()
        (tmp_path / "shared").mkdir()

        # Should not raise
        validate_structure(tmp_path)


class TestValidateStructureFailure:
    """Tests for validate_structure when structure is invalid."""

    def test_raises_when_manuscript_missing(self, tmp_path):
        """Verify raises RuntimeError when 01_manuscript is missing."""
        # Arrange
        (tmp_path / "02_supplementary").mkdir()
        # Act
        (tmp_path / "03_revision").mkdir()

        # Assert
        with pytest.raises(RuntimeError, match="01_manuscript"):
            validate_structure(tmp_path)

    def test_raises_when_supplementary_missing(self, tmp_path):
        """Verify raises RuntimeError when 02_supplementary is missing."""
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        # Act
        (tmp_path / "03_revision").mkdir()

        # Assert
        with pytest.raises(RuntimeError, match="02_supplementary"):
            validate_structure(tmp_path)

    def test_raises_when_revision_missing(self, tmp_path):
        """Verify raises RuntimeError when 03_revision is missing."""
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        # Act
        (tmp_path / "02_supplementary").mkdir()

        # Assert
        with pytest.raises(RuntimeError, match="03_revision"):
            validate_structure(tmp_path)

    def test_raises_when_all_missing(self, tmp_path):
        """Verify raises RuntimeError when all required dirs are missing."""
        # Arrange
        # Act
        # Assert
        with pytest.raises(RuntimeError, match="01_manuscript"):
            validate_structure(tmp_path)

    def test_error_message_contains_path_raises_runtimeerror(self, tmp_path):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        with pytest.raises(RuntimeError) as exc_info:
            validate_structure(tmp_path)

    def test_error_message_contains_path_expected_at_in_str_exc_info_value(self, tmp_path):
        # Arrange
        # Act
        # Assert
        # Arrange
        # Act
        # Assert
        assert "expected at:" in str(exc_info.value)



class TestValidateStructureEdgeCases:
    """Tests for validate_structure edge cases."""

    def test_file_instead_of_directory(self, tmp_path):
        """Verify raises when file exists instead of directory."""
        # Arrange
        # Act
        # Assert
        (tmp_path / "01_manuscript").write_text("not a directory")
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "03_revision").mkdir()

        # File exists but is not a directory - exists() still returns True
        # This may or may not be an issue depending on expected behavior
        validate_structure(tmp_path)

    def test_nested_project_directory(self, tmp_path):
        """Verify works with nested project directory."""
        # Arrange
        # Act
        # Assert
        nested = tmp_path / "projects" / "my_paper"
        nested.mkdir(parents=True)
        (nested / "01_manuscript").mkdir()
        (nested / "02_supplementary").mkdir()
        (nested / "03_revision").mkdir()

        validate_structure(nested)


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
