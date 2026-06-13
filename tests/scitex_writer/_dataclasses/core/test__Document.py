#!/usr/bin/env python3
"""Tests for scitex_writer._dataclasses.core._Document."""

import pytest

from scitex_writer._dataclasses.core import Document


class TestDocumentInitialization:
    """Tests for Document dataclass initialization."""

    def test_creates_document_with_root_path_attribute(self, tmp_path):
        """Verify Document can be created with a root path."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        doc = Document(root=tmp_path)
        # Assert
        assert doc.root == tmp_path

    def test_creates_document_with_explicit_git_root(self, tmp_path):
        """Verify Document can be created with an explicit git_root path."""
        # Arrange
        git_root = tmp_path / ".git"
        # Act
        doc = Document(root=tmp_path, git_root=git_root)
        # Assert
        assert doc.git_root == git_root

    def test_git_root_defaults_to_none_when_not_supplied(self, tmp_path):
        """Verify git_root defaults to None when not supplied."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        doc = Document(root=tmp_path)
        # Assert
        assert doc.git_root is None


class TestDocumentAttributes:
    """Tests for Document computed attributes."""

    def test_name_property_returns_root_directory_name(self, tmp_path):
        """Verify name property returns root directory name."""
        # Arrange
        project_dir = tmp_path / "my_project"
        project_dir.mkdir()
        doc = Document(root=project_dir)
        # Act
        name = doc.name
        # Assert
        assert name == "my_project"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
