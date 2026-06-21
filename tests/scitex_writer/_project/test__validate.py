#!/usr/bin/env python3
"""Tests for scitex_writer._project._validate."""

import pytest

from scitex_writer._project._validate import validate_structure


class TestValidateStructureSuccess:
    """Tests for validate_structure when structure is valid."""

    def test_returns_none_with_all_required_directories(self, tmp_path):
        """validate_structure returns None (no raise) for a complete structure."""
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "03_revision").mkdir()
        # Act
        result = validate_structure(tmp_path)
        # Assert
        assert result is None

    def test_returns_none_with_extra_directories(self, tmp_path):
        """validate_structure tolerates extra directories and returns None."""
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

    def test_error_message_points_at_the_missing_directory_path(self, tmp_path):
        """The RuntimeError message names the absolute path it expected."""
        # Arrange
        # Act
        # Assert
        with pytest.raises(RuntimeError, match="expected at:"):
            validate_structure(tmp_path)


class TestValidateStructureEdgeCases:
    """Tests for validate_structure edge cases."""

    def test_file_named_like_required_dir_passes_existence_only_check(self, tmp_path):
        """A plain file (not a dir) named 01_manuscript still satisfies the
        existence-only check, so validate_structure returns None.

        This pins the current contract: validate_structure tests `.exists()`,
        not `.is_dir()`. If the check is tightened later, this test should
        flip to `pytest.raises`.
        """
        # Arrange
        (tmp_path / "01_manuscript").write_text("not a directory")
        (tmp_path / "02_supplementary").mkdir()
        (tmp_path / "03_revision").mkdir()
        # Act
        result = validate_structure(tmp_path)
        # Assert
        assert result is None

    def test_returns_none_for_valid_nested_project_directory(self, tmp_path):
        """validate_structure works on a project nested below tmp_path."""
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
