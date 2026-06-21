#!/usr/bin/env python3
"""Tests for scitex_writer._dataclasses.tree._ManuscriptTree."""

import pytest

from scitex_writer._dataclasses import ManuscriptTree


class TestManuscriptTreeInitialization:
    """Tests for ManuscriptTree initialization."""

    def test_creates_with_root(self, tmp_path):
        """Verify ManuscriptTree can be created with root path."""
        # Arrange
        # Act
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        # Assert
        assert tree.root == tmp_path / "01_manuscript"

    def test_creates_with_git_root(self, tmp_path):
        """Verify ManuscriptTree can be created with git_root."""
        # Arrange
        # Act
        tree = ManuscriptTree(
            root=tmp_path / "01_manuscript",
            git_root=tmp_path,
        )

        # Assert
        assert tree.git_root == tmp_path

    def test_git_root_defaults_to_none(self, tmp_path):
        """Verify git_root defaults to None."""
        # Arrange
        # Act
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        # Assert
        assert tree.git_root is None


class TestManuscriptTreePaths:
    """Tests for ManuscriptTree path attributes."""

    def test_contents_figures_path(self, tmp_path):
        """Verify figures path is in contents/ subdirectory."""
        # Arrange
        # Act
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        # Assert
        assert (
            tree.contents.figures == tmp_path / "01_manuscript" / "contents" / "figures"
        )

    def test_contents_tables_path(self, tmp_path):
        """Verify tables path is in contents/ subdirectory."""
        # Arrange
        # Act
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        # Assert
        assert (
            tree.contents.tables == tmp_path / "01_manuscript" / "contents" / "tables"
        )

    def test_base_tex_path(self, tmp_path):
        """Verify base.tex path is at root level."""
        # Arrange
        # Act
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        # Assert
        assert tree.base.path == tmp_path / "01_manuscript" / "base.tex"

    def test_archive_path_tree_archive_equals_tmp_path_01_manuscri(self, tmp_path):
        """Verify archive path is at root level."""
        # Arrange
        # Act
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        # Assert
        assert tree.archive == tmp_path / "01_manuscript" / "archive"


class TestManuscriptTreeVerifyStructure:
    """Tests for ManuscriptTree.verify_structure method."""

    def test_returns_tuple_result_is_tuple_and_len_r(self, tmp_path):
        """Verify verify_structure returns (is_valid, issues) tuple."""
        # Arrange
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        # Act
        result = tree.verify_structure()

        # Assert
        assert (isinstance(result, tuple)) and (len(result) == 2)

    def test_returns_issues_list(self, tmp_path):
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
