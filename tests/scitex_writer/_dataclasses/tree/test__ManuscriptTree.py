#!/usr/bin/env python3
"""Tests for scitex_writer._dataclasses.tree._ManuscriptTree."""

import pytest

from scitex_writer._dataclasses import ManuscriptTree


class TestManuscriptTreeInitialization:
    """Tests for ManuscriptTree initialization."""

    def test_creates_tree_with_root_path_attribute(self, tmp_path):
        """Verify ManuscriptTree can be created with a root path."""
        # Arrange
        root = tmp_path / "01_manuscript"
        # Act
        tree = ManuscriptTree(root=root)
        # Assert
        assert tree.root == root

    def test_creates_tree_with_explicit_git_root(self, tmp_path):
        """Verify ManuscriptTree can be created with an explicit git_root."""
        # Arrange
        root = tmp_path / "01_manuscript"
        # Act
        tree = ManuscriptTree(root=root, git_root=tmp_path)
        # Assert
        assert tree.git_root == tmp_path

    def test_git_root_defaults_to_none_when_not_supplied(self, tmp_path):
        """Verify git_root defaults to None when not supplied."""
        # Arrange
        root = tmp_path / "01_manuscript"
        # Act
        tree = ManuscriptTree(root=root)
        # Assert
        assert tree.git_root is None


class TestManuscriptTreePaths:
    """Tests for ManuscriptTree path attributes."""

    def test_contents_figures_path_under_contents_subdir(self, tmp_path):
        """Verify figures path is in contents/ subdirectory."""
        # Arrange
        root = tmp_path / "01_manuscript"
        # Act
        tree = ManuscriptTree(root=root)
        # Assert
        assert tree.contents.figures == root / "contents" / "figures"

    def test_contents_tables_path_under_contents_subdir(self, tmp_path):
        """Verify tables path is in contents/ subdirectory."""
        # Arrange
        root = tmp_path / "01_manuscript"
        # Act
        tree = ManuscriptTree(root=root)
        # Assert
        assert tree.contents.tables == root / "contents" / "tables"

    def test_base_tex_path_lives_at_root_level(self, tmp_path):
        """Verify base.tex path is at the root level."""
        # Arrange
        root = tmp_path / "01_manuscript"
        # Act
        tree = ManuscriptTree(root=root)
        # Assert
        assert tree.base.path == root / "base.tex"

    def test_archive_path_lives_at_root_level(self, tmp_path):
        """Verify archive path is at the root level."""
        # Arrange
        root = tmp_path / "01_manuscript"
        # Act
        tree = ManuscriptTree(root=root)
        # Assert
        assert tree.archive == root / "archive"


class TestManuscriptTreeVerifyStructure:
    """Tests for ManuscriptTree.verify_structure method."""

    def test_verify_structure_returns_tuple_instance(self, tmp_path):
        """Verify verify_structure returns a tuple."""
        # Arrange
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")
        # Act
        result = tree.verify_structure()
        # Assert
        assert isinstance(result, tuple)

    def test_verify_structure_returns_two_element_tuple(self, tmp_path):
        """Verify verify_structure returns a 2-tuple."""
        # Arrange
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")
        # Act
        result = tree.verify_structure()
        # Assert
        assert len(result) == 2

    def test_verify_structure_second_element_is_issues_list(self, tmp_path):
        """Verify second element is list of issues."""
        # Arrange
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")
        # Act
        _, issues = tree.verify_structure()
        # Assert
        assert isinstance(issues, list)


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
