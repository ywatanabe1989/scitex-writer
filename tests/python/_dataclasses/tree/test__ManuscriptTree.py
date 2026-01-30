#!/usr/bin/env python3
"""Tests for scitex_writer._dataclasses.tree._ManuscriptTree."""

import pytest

from scitex_writer._dataclasses import ManuscriptTree


class TestManuscriptTreeInitialization:
    """Tests for ManuscriptTree initialization."""

    def test_creates_with_root(self, tmp_path):
        """Verify ManuscriptTree can be created with root path."""
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        assert tree.root == tmp_path / "01_manuscript"

    def test_creates_with_git_root(self, tmp_path):
        """Verify ManuscriptTree can be created with git_root."""
        tree = ManuscriptTree(
            root=tmp_path / "01_manuscript",
            git_root=tmp_path,
        )

        assert tree.git_root == tmp_path

    def test_git_root_defaults_to_none(self, tmp_path):
        """Verify git_root defaults to None."""
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        assert tree.git_root is None


class TestManuscriptTreePaths:
    """Tests for ManuscriptTree path attributes."""

    def test_contents_figures_path(self, tmp_path):
        """Verify figures path is in contents/ subdirectory."""
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        assert (
            tree.contents.figures == tmp_path / "01_manuscript" / "contents" / "figures"
        )

    def test_contents_tables_path(self, tmp_path):
        """Verify tables path is in contents/ subdirectory."""
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        assert (
            tree.contents.tables == tmp_path / "01_manuscript" / "contents" / "tables"
        )

    def test_base_tex_path(self, tmp_path):
        """Verify base.tex path is at root level."""
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        assert tree.base.path == tmp_path / "01_manuscript" / "base.tex"

    def test_archive_path(self, tmp_path):
        """Verify archive path is at root level."""
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        assert tree.archive == tmp_path / "01_manuscript" / "archive"


class TestManuscriptTreeVerifyStructure:
    """Tests for ManuscriptTree.verify_structure method."""

    def test_returns_tuple(self, tmp_path):
        """Verify verify_structure returns (is_valid, issues) tuple."""
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        result = tree.verify_structure()

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_returns_issues_list(self, tmp_path):
        """Verify second element is list of issues."""
        tree = ManuscriptTree(root=tmp_path / "01_manuscript")

        _, issues = tree.verify_structure()

        assert isinstance(issues, list)


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
