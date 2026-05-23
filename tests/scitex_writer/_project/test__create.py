#!/usr/bin/env python3
"""Tests for scitex_writer._project._create.ensure_project_exists.

ensure_project_exists forwards (dir, git_strategy, branch, tag) to a
clone function and raises if it fails or doesn't create the directory.
Tests inject a real recording clone via the clone_fn= seam — no patching
of clone_writer_project, no network.
"""

import pytest

from scitex_writer._project._create import ensure_project_exists


class _RecordingClone:
    """Real clone stand-in: records call args, optionally creates the dir."""

    def __init__(self, create_dir=True, result=True):
        self.calls = []
        self.create_dir = create_dir
        self.result = result

    def __call__(self, project_dir, git_strategy, branch, tag):
        self.calls.append((project_dir, git_strategy, branch, tag))
        if self.create_dir:
            from pathlib import Path

            Path(project_dir).mkdir(parents=True, exist_ok=True)
        return self.result


class TestEnsureProjectExistsExisting:
    """When the project directory already exists."""

    def test_returns_existing_directory(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "my_paper"
        project_dir.mkdir()
        # Act
        result = ensure_project_exists(project_dir, "my_paper")
        # Assert
        assert result == project_dir

    def test_does_not_invoke_clone_for_existing_project(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "my_paper"
        project_dir.mkdir()
        clone = _RecordingClone()
        # Act
        ensure_project_exists(project_dir, "my_paper", clone_fn=clone)
        # Assert
        assert clone.calls == []

    def test_existing_directory_contents_are_preserved(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "my_paper"
        project_dir.mkdir()
        (project_dir / "01_manuscript").mkdir()
        # Act
        result = ensure_project_exists(project_dir, "my_paper")
        # Assert
        assert (result / "01_manuscript").exists()


class TestEnsureProjectExistsNew:
    """When the project directory must be created."""

    def test_forwards_default_args_to_clone(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "new_paper"
        clone = _RecordingClone()
        # Act
        ensure_project_exists(project_dir, "new_paper", clone_fn=clone)
        # Assert
        assert clone.calls == [(str(project_dir), "child", None, None)]

    def test_forwards_custom_git_strategy(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "new_paper"
        clone = _RecordingClone()
        # Act
        ensure_project_exists(
            project_dir, "new_paper", git_strategy="standalone", clone_fn=clone
        )
        # Assert
        assert clone.calls[0][1] == "standalone"

    def test_forwards_branch_argument_to_clone(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "new_paper"
        clone = _RecordingClone()
        # Act
        ensure_project_exists(
            project_dir, "new_paper", branch="develop", clone_fn=clone
        )
        # Assert
        assert clone.calls[0][2] == "develop"

    def test_forwards_tag_argument_to_clone(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "new_paper"
        clone = _RecordingClone()
        # Act
        ensure_project_exists(project_dir, "new_paper", tag="v1.0.0", clone_fn=clone)
        # Assert
        assert clone.calls[0][3] == "v1.0.0"

    def test_forwards_none_git_strategy(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "new_paper"
        clone = _RecordingClone()
        # Act
        ensure_project_exists(
            project_dir, "new_paper", git_strategy=None, clone_fn=clone
        )
        # Assert
        assert clone.calls[0][1] is None

    def test_returns_the_created_directory(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "new_paper"
        clone = _RecordingClone()
        # Act
        result = ensure_project_exists(project_dir, "new_paper", clone_fn=clone)
        # Assert
        assert result == project_dir


class TestEnsureProjectExistsFailure:
    """Failure cases."""

    def test_raises_when_clone_returns_false(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "new_paper"
        clone = _RecordingClone(create_dir=False, result=False)
        # Act
        # Assert
        with pytest.raises(RuntimeError, match="Could not create"):
            ensure_project_exists(project_dir, "new_paper", clone_fn=clone)

    def test_raises_when_directory_not_created_despite_success(self, tmp_path):
        # Arrange
        project_dir = tmp_path / "new_paper"
        clone = _RecordingClone(create_dir=False, result=True)
        # Act
        # Assert
        with pytest.raises(RuntimeError, match="was not created"):
            ensure_project_exists(project_dir, "new_paper", clone_fn=clone)


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
