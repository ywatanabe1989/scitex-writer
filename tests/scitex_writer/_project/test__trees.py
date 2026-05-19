#!/usr/bin/env python3
"""Tests for scitex_writer._project._trees."""

import pytest

from scitex_writer._dataclasses import ManuscriptTree, RevisionTree, SupplementaryTree
from scitex_writer._dataclasses.tree import ScriptsTree
from scitex_writer._project._trees import create_document_trees


class TestCreateDocumentTreesReturnTypes:
    """Tests for create_document_trees return types."""

    def test_returns_tuple_of_four(self, tmp_path):
        """Verify returns a tuple of four items."""
        # Arrange
        # Act
        result = create_document_trees(tmp_path, None)

        # Assert
        assert (isinstance(result, tuple)) and (len(result) == 4)

    def test_returns_manuscript_tree(self, tmp_path):
        """Verify first element is ManuscriptTree."""
        # Arrange
        # Act
        manuscript, _, _, _ = create_document_trees(tmp_path, None)

        # Assert
        assert isinstance(manuscript, ManuscriptTree)

    def test_returns_supplementary_tree(self, tmp_path):
        """Verify second element is SupplementaryTree."""
        # Arrange
        # Act
        _, supplementary, _, _ = create_document_trees(tmp_path, None)

        # Assert
        assert isinstance(supplementary, SupplementaryTree)

    def test_returns_revision_tree(self, tmp_path):
        """Verify third element is RevisionTree."""
        # Arrange
        # Act
        _, _, revision, _ = create_document_trees(tmp_path, None)

        # Assert
        assert isinstance(revision, RevisionTree)

    def test_returns_scripts_tree(self, tmp_path):
        """Verify fourth element is ScriptsTree."""
        # Arrange
        # Act
        _, _, _, scripts = create_document_trees(tmp_path, None)

        # Assert
        assert isinstance(scripts, ScriptsTree)


class TestCreateDocumentTreesPaths:
    """Tests for create_document_trees path initialization."""

    def test_manuscript_path_correct(self, tmp_path):
        """Verify manuscript tree has correct root path."""
        # Arrange
        # Act
        manuscript, _, _, _ = create_document_trees(tmp_path, None)

        # Assert
        assert manuscript.root == tmp_path / "01_manuscript"

    def test_supplementary_path_correct(self, tmp_path):
        """Verify supplementary tree has correct root path."""
        # Arrange
        # Act
        _, supplementary, _, _ = create_document_trees(tmp_path, None)

        # Assert
        assert supplementary.root == tmp_path / "02_supplementary"

    def test_revision_path_correct(self, tmp_path):
        """Verify revision tree has correct root path."""
        # Arrange
        # Act
        _, _, revision, _ = create_document_trees(tmp_path, None)

        # Assert
        assert revision.root == tmp_path / "03_revision"

    def test_scripts_path_correct(self, tmp_path):
        """Verify scripts tree has correct root path."""
        # Arrange
        # Act
        _, _, _, scripts = create_document_trees(tmp_path, None)

        # Assert
        assert scripts.root == tmp_path / "scripts"


class TestCreateDocumentTreesGitRoot:
    """Tests for create_document_trees git_root propagation."""

    def test_git_root_none_propagated(self, tmp_path):
        """Verify git_root=None is propagated to all trees."""
        # Arrange
        # Act
        manuscript, supplementary, revision, scripts = create_document_trees(
            tmp_path, None
        )

        # Assert
        assert (manuscript.git_root is None) and (supplementary.git_root is None) and (revision.git_root is None) and (scripts.git_root is None)

    def test_git_root_propagated_to_all(self, tmp_path):
        """Verify git_root is propagated to all trees."""
        # Arrange
        git_root = tmp_path / ".git"
        git_root.mkdir()

        # Act
        manuscript, supplementary, revision, scripts = create_document_trees(
            tmp_path, git_root
        )

        # Assert
        assert (manuscript.git_root == git_root) and (supplementary.git_root == git_root) and (revision.git_root == git_root) and (scripts.git_root == git_root)


class TestCreateDocumentTreesNestedProject:
    """Tests for create_document_trees with nested project directory."""

    def test_nested_project_path(self, tmp_path):
        """Verify works with nested project directory."""
        # Arrange
        nested = tmp_path / "papers" / "2024" / "my_paper"

        # Act
        manuscript, supplementary, revision, scripts = create_document_trees(
            nested, None
        )

        # Assert
        assert (manuscript.root == nested / '01_manuscript') and (supplementary.root == nested / '02_supplementary') and (revision.root == nested / '03_revision') and (scripts.root == nested / 'scripts')


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
