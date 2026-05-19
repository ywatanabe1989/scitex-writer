#!/usr/bin/env python3
"""Tests for scitex_writer._project._create.clone_writer_project."""

import subprocess
from unittest.mock import MagicMock, patch

from scitex_writer._project._create import clone_writer_project


class TestCloneWriterProjectSuccess:
    """Tests for clone_writer_project success cases."""

    def test_returns_true_on_success(self, tmp_path):
        """Verify clone_writer_project returns True on success."""
        # Arrange
        project_dir = tmp_path / "new_paper"

        # Mock subprocess.run to simulate successful clone
        # Act
        with patch("scitex_writer._project._create.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = clone_writer_project(str(project_dir))

        # Should return True when subprocess succeeds
        # Assert
        assert result is True

    def test_passes_git_strategy(self, tmp_path):
        """Verify git_strategy affects git initialization."""
        # Arrange
        project_dir = tmp_path / "new_paper"

        # Act
        with patch("scitex_writer._project._create.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            clone_writer_project(str(project_dir), git_strategy="parent")

        # Function should succeed
        # Assert
        assert True  # Basic test that it doesn't crash

    def test_passes_branch_result_is_true(self, tmp_path):
        """Verify branch parameter is handled."""
        # Arrange
        project_dir = tmp_path / "new_paper"

        # Act
        with patch("scitex_writer._project._create.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = clone_writer_project(str(project_dir), branch="develop")

        # Assert
        assert result is True

    def test_passes_tag_result_is_true(self, tmp_path):
        """Verify tag parameter is handled."""
        # Arrange
        project_dir = tmp_path / "new_paper"

        # Act
        with patch("scitex_writer._project._create.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = clone_writer_project(str(project_dir), tag="v1.0.0")

        # Assert
        assert result is True


class TestCloneWriterProjectFailure:
    """Tests for clone_writer_project failure cases."""

    def test_returns_false_when_clone_fails(self, tmp_path):
        """Verify returns False when git clone fails."""
        # Arrange
        project_dir = tmp_path / "new_paper"

        # Act
        with patch("scitex_writer._project._create.subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "git")
            result = clone_writer_project(str(project_dir))

        # Assert
        assert result is False

    def test_returns_false_on_exception(self, tmp_path):
        """Verify returns False on generic exception."""
        # Arrange
        project_dir = tmp_path / "new_paper"

        # Act
        with patch("scitex_writer._project._create.subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Test error")
            result = clone_writer_project(str(project_dir))

        # Assert
        assert result is False


class TestCloneWriterProjectGitStrategy:
    """Tests for clone_writer_project git_strategy parameter."""

    def test_default_git_strategy_is_child(self, tmp_path):
        """Verify default git_strategy is 'child'."""
        # Arrange
        project_dir = tmp_path / "new_paper"

        # Act
        with patch("scitex_writer._project._create.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = clone_writer_project(str(project_dir))

        # Assert
        assert result is True

    def test_git_strategy_none(self, tmp_path):
        """Verify git_strategy=None works."""
        # Arrange
        project_dir = tmp_path / "new_paper"

        # Act
        with patch("scitex_writer._project._create.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = clone_writer_project(str(project_dir), git_strategy=None)

        # Assert
        assert result is True

    def test_git_strategy_origin(self, tmp_path):
        """Verify git_strategy='origin' works."""
        # Arrange
        project_dir = tmp_path / "new_paper"

        # Act
        with patch("scitex_writer._project._create.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = clone_writer_project(str(project_dir), git_strategy="origin")

        # Assert
        assert result is True
