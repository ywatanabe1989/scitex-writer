#!/usr/bin/env python3
"""Tests for scitex_writer._project._create."""

import pytest

from scitex_writer._project import _create as create_mod
from scitex_writer._project._create import ensure_project_exists


@pytest.fixture
def fake_clone(tmp_path):
    """Provide a real callable that records calls and optionally creates a dir.

    Replaces ``scitex_writer._project._create.clone_writer_project`` on the
    module without using unittest.mock. Cleans up the original attribute
    on teardown.
    """

    class _Recorder:
        def __init__(self):
            self.calls = []
            self.return_value = True
            self.create_target = None

        def __call__(self, *args, **kwargs):
            self.calls.append((args, kwargs))
            if self.create_target is not None:
                self.create_target.mkdir(parents=True, exist_ok=True)
            return self.return_value

    recorder = _Recorder()
    original = create_mod.clone_writer_project
    create_mod.clone_writer_project = recorder
    try:
        yield recorder
    finally:
        create_mod.clone_writer_project = original


class TestEnsureProjectExistsExisting:
    """Tests for ensure_project_exists when project already exists."""

    def test_returns_existing_directory_unchanged(self, tmp_path, fake_clone):
        """Verify returns existing project directory."""
        # Arrange
        project_dir = tmp_path / "my_paper"
        project_dir.mkdir()
        # Act
        result = ensure_project_exists(project_dir, "my_paper")
        # Assert
        assert result == project_dir

    def test_does_not_invoke_clone_when_directory_exists(self, tmp_path, fake_clone):
        """Verify clone is not called when project exists."""
        # Arrange
        project_dir = tmp_path / "my_paper"
        project_dir.mkdir()
        # Act
        ensure_project_exists(project_dir, "my_paper")
        # Assert
        assert fake_clone.calls == []

    def test_existing_directory_with_contents_returns_same_path(
        self, tmp_path, fake_clone
    ):
        """Verify returns existing directory with contents."""
        # Arrange
        project_dir = tmp_path / "my_paper"
        project_dir.mkdir()
        (project_dir / "01_manuscript").mkdir()
        (project_dir / "file.tex").write_text("content")
        # Act
        result = ensure_project_exists(project_dir, "my_paper")
        # Assert
        assert result == project_dir

    def test_existing_directory_contents_remain_intact(self, tmp_path, fake_clone):
        """Verify existing project contents are not modified."""
        # Arrange
        project_dir = tmp_path / "my_paper"
        project_dir.mkdir()
        (project_dir / "01_manuscript").mkdir()
        (project_dir / "file.tex").write_text("content")
        # Act
        result = ensure_project_exists(project_dir, "my_paper")
        # Assert
        assert (result / "01_manuscript").exists()


class TestEnsureProjectExistsNew:
    """Tests for ensure_project_exists when creating new project."""

    def test_clone_called_with_expected_default_arguments(self, tmp_path, fake_clone):
        """Verify clone is called with default child strategy and no branch/tag."""
        # Arrange
        project_dir = tmp_path / "new_paper"
        fake_clone.create_target = project_dir
        # Act
        ensure_project_exists(project_dir, "new_paper")
        # Assert
        assert fake_clone.calls == [((str(project_dir), "child", None, None), {})]

    def test_clone_called_with_custom_git_strategy(self, tmp_path, fake_clone):
        """Verify git_strategy is forwarded verbatim to clone."""
        # Arrange
        project_dir = tmp_path / "new_paper"
        fake_clone.create_target = project_dir
        # Act
        ensure_project_exists(project_dir, "new_paper", git_strategy="standalone")
        # Assert
        assert fake_clone.calls == [((str(project_dir), "standalone", None, None), {})]

    def test_clone_called_with_branch_argument(self, tmp_path, fake_clone):
        """Verify branch parameter is forwarded to clone."""
        # Arrange
        project_dir = tmp_path / "new_paper"
        fake_clone.create_target = project_dir
        # Act
        ensure_project_exists(project_dir, "new_paper", branch="develop")
        # Assert
        assert fake_clone.calls == [((str(project_dir), "child", "develop", None), {})]

    def test_clone_called_with_tag_argument(self, tmp_path, fake_clone):
        """Verify tag parameter is forwarded to clone."""
        # Arrange
        project_dir = tmp_path / "new_paper"
        fake_clone.create_target = project_dir
        # Act
        ensure_project_exists(project_dir, "new_paper", tag="v1.0.0")
        # Assert
        assert fake_clone.calls == [((str(project_dir), "child", None, "v1.0.0"), {})]

    def test_returns_created_directory_path(self, tmp_path, fake_clone):
        """Verify returns the created project directory path."""
        # Arrange
        project_dir = tmp_path / "new_paper"
        fake_clone.create_target = project_dir
        # Act
        result = ensure_project_exists(project_dir, "new_paper")
        # Assert
        assert result == project_dir


class TestEnsureProjectExistsFailure:
    """Tests for ensure_project_exists failure cases."""

    def test_raises_runtime_error_when_clone_returns_false(self, tmp_path, fake_clone):
        """Verify raises RuntimeError when clone returns False."""
        # Arrange
        project_dir = tmp_path / "new_paper"
        fake_clone.return_value = False
        # Act
        ctx = pytest.raises(RuntimeError, match="Could not create")
        # Assert
        with ctx:
            ensure_project_exists(project_dir, "new_paper")

    def test_raises_runtime_error_when_directory_not_created(
        self, tmp_path, fake_clone
    ):
        """Verify raises RuntimeError when directory not created after clone."""
        # Arrange
        project_dir = tmp_path / "new_paper"
        fake_clone.return_value = True
        fake_clone.create_target = None  # do not create the dir
        # Act
        ctx = pytest.raises(RuntimeError, match="was not created")
        # Assert
        with ctx:
            ensure_project_exists(project_dir, "new_paper")


class TestEnsureProjectExistsGitStrategy:
    """Tests for ensure_project_exists git_strategy parameter."""

    def test_git_strategy_none_forwarded_as_none(self, tmp_path, fake_clone):
        """Verify git_strategy=None is forwarded to clone correctly."""
        # Arrange
        project_dir = tmp_path / "new_paper"
        fake_clone.create_target = project_dir
        # Act
        ensure_project_exists(project_dir, "new_paper", git_strategy=None)
        # Assert
        assert fake_clone.calls == [((str(project_dir), None, None, None), {})]

    def test_default_git_strategy_value_is_child(self, tmp_path, fake_clone):
        """Verify default git_strategy is 'child' when omitted."""
        # Arrange
        project_dir = tmp_path / "new_paper"
        fake_clone.create_target = project_dir
        # Act
        ensure_project_exists(project_dir, "new_paper")
        # Assert
        assert fake_clone.calls[0][0][1] == "child"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
