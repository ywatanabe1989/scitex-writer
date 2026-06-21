#!/usr/bin/env python3
"""Tests for scitex_writer._dataclasses.core._Document."""

import pytest

from scitex_writer._dataclasses.core import Document


class TestDocumentInitialization:
    """Tests for Document dataclass initialization."""

    def test_creates_with_root_path(self, tmp_path):
        """Verify Document can be created with root path."""
        # Arrange
        # Act
        doc = Document(root=tmp_path)

        # Assert
        assert doc.root == tmp_path

    def test_creates_with_git_root(self, tmp_path):
        """Verify Document can be created with git_root."""
        # Arrange
        git_root = tmp_path / ".git"
        # Act
        doc = Document(root=tmp_path, git_root=git_root)

        # Assert
        assert doc.git_root == git_root

    def test_git_root_defaults_to_none(self, tmp_path):
        """Verify git_root defaults to None."""
        # Arrange
        # Act
        doc = Document(root=tmp_path)

        # Assert
        assert doc.git_root is None


class TestDocumentAttributes:
    """Tests for Document computed attributes."""

    def test_name_returns_root_name(self, tmp_path):
        """Verify name property returns root directory name."""
        # Arrange
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        # Act
        doc = Document(root=project_dir)

        # Assert
        assert doc.name == "my_project"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
