#!/usr/bin/env python3
"""Tests for scitex_writer._project._trees."""

import pytest

from scitex_writer._dataclasses import ManuscriptTree, RevisionTree, SupplementaryTree
from scitex_writer._dataclasses.tree import ScriptsTree
from scitex_writer._project._trees import create_document_trees


class TestCreateDocumentTreesReturnTypes:
    """Tests for create_document_trees return types."""

    def test_returns_value_is_tuple_instance(self, tmp_path):
        """Verify returned value is a tuple."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        result = create_document_trees(tmp_path, None)
        # Assert
        assert isinstance(result, tuple)

    def test_returns_tuple_with_exactly_four_elements(self, tmp_path):
        """Verify returned tuple has exactly four elements."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        result = create_document_trees(tmp_path, None)
        # Assert
        assert len(result) == 4

    def test_returns_manuscript_tree_as_first_element(self, tmp_path):
        """Verify first element is ManuscriptTree."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        manuscript, _, _, _ = create_document_trees(tmp_path, None)
        # Assert
        assert isinstance(manuscript, ManuscriptTree)

    def test_returns_supplementary_tree_as_second_element(self, tmp_path):
        """Verify second element is SupplementaryTree."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        _, supplementary, _, _ = create_document_trees(tmp_path, None)
        # Assert
        assert isinstance(supplementary, SupplementaryTree)

    def test_returns_revision_tree_as_third_element(self, tmp_path):
        """Verify third element is RevisionTree."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        _, _, revision, _ = create_document_trees(tmp_path, None)
        # Assert
        assert isinstance(revision, RevisionTree)

    def test_returns_scripts_tree_as_fourth_element(self, tmp_path):
        """Verify fourth element is ScriptsTree."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        _, _, _, scripts = create_document_trees(tmp_path, None)
        # Assert
        assert isinstance(scripts, ScriptsTree)


class TestCreateDocumentTreesPaths:
    """Tests for create_document_trees path initialization."""

    def test_manuscript_tree_root_path_matches_convention(self, tmp_path):
        """Verify manuscript tree has correct root path."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        manuscript, _, _, _ = create_document_trees(tmp_path, None)
        # Assert
        assert manuscript.root == tmp_path / "01_manuscript"

    def test_supplementary_tree_root_path_matches_convention(self, tmp_path):
        """Verify supplementary tree has correct root path."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        _, supplementary, _, _ = create_document_trees(tmp_path, None)
        # Assert
        assert supplementary.root == tmp_path / "02_supplementary"

    def test_revision_tree_root_path_matches_convention(self, tmp_path):
        """Verify revision tree has correct root path."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        _, _, revision, _ = create_document_trees(tmp_path, None)
        # Assert
        assert revision.root == tmp_path / "03_revision"

    def test_scripts_tree_root_path_matches_convention(self, tmp_path):
        """Verify scripts tree has correct root path."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        _, _, _, scripts = create_document_trees(tmp_path, None)
        # Assert
        assert scripts.root == tmp_path / "scripts"


class TestCreateDocumentTreesGitRoot:
    """Tests for create_document_trees git_root propagation."""

    def test_git_root_none_propagated_to_manuscript_tree(self, tmp_path):
        """Verify git_root=None propagates to manuscript tree."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        manuscript, _, _, _ = create_document_trees(tmp_path, None)
        # Assert
        assert manuscript.git_root is None

    def test_git_root_none_propagated_to_supplementary_tree(self, tmp_path):
        """Verify git_root=None propagates to supplementary tree."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        _, supplementary, _, _ = create_document_trees(tmp_path, None)
        # Assert
        assert supplementary.git_root is None

    def test_git_root_none_propagated_to_revision_tree(self, tmp_path):
        """Verify git_root=None propagates to revision tree."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        _, _, revision, _ = create_document_trees(tmp_path, None)
        # Assert
        assert revision.git_root is None

    def test_git_root_none_propagated_to_scripts_tree(self, tmp_path):
        """Verify git_root=None propagates to scripts tree."""
        # Arrange
        # tmp_path provided by fixture
        # Act
        _, _, _, scripts = create_document_trees(tmp_path, None)
        # Assert
        assert scripts.git_root is None

    def test_git_root_path_propagated_to_manuscript_tree(self, tmp_path):
        """Verify supplied git_root path propagates to manuscript tree."""
        # Arrange
        git_root = tmp_path / ".git"
        git_root.mkdir()
        # Act
        manuscript, _, _, _ = create_document_trees(tmp_path, git_root)
        # Assert
        assert manuscript.git_root == git_root

    def test_git_root_path_propagated_to_supplementary_tree(self, tmp_path):
        """Verify supplied git_root path propagates to supplementary tree."""
        # Arrange
        git_root = tmp_path / ".git"
        git_root.mkdir()
        # Act
        _, supplementary, _, _ = create_document_trees(tmp_path, git_root)
        # Assert
        assert supplementary.git_root == git_root

    def test_git_root_path_propagated_to_revision_tree(self, tmp_path):
        """Verify supplied git_root path propagates to revision tree."""
        # Arrange
        git_root = tmp_path / ".git"
        git_root.mkdir()
        # Act
        _, _, revision, _ = create_document_trees(tmp_path, git_root)
        # Assert
        assert revision.git_root == git_root

    def test_git_root_path_propagated_to_scripts_tree(self, tmp_path):
        """Verify supplied git_root path propagates to scripts tree."""
        # Arrange
        git_root = tmp_path / ".git"
        git_root.mkdir()
        # Act
        _, _, _, scripts = create_document_trees(tmp_path, git_root)
        # Assert
        assert scripts.git_root == git_root


class TestCreateDocumentTreesNestedProject:
    """Tests for create_document_trees with nested project directory."""

    def test_nested_manuscript_root_uses_nested_base_path(self, tmp_path):
        """Verify manuscript root respects nested project base path."""
        # Arrange
        nested = tmp_path / "papers" / "2024" / "my_paper"
        # Act
        manuscript, _, _, _ = create_document_trees(nested, None)
        # Assert
        assert manuscript.root == nested / "01_manuscript"

    def test_nested_supplementary_root_uses_nested_base_path(self, tmp_path):
        """Verify supplementary root respects nested project base path."""
        # Arrange
        nested = tmp_path / "papers" / "2024" / "my_paper"
        # Act
        _, supplementary, _, _ = create_document_trees(nested, None)
        # Assert
        assert supplementary.root == nested / "02_supplementary"

    def test_nested_revision_root_uses_nested_base_path(self, tmp_path):
        """Verify revision root respects nested project base path."""
        # Arrange
        nested = tmp_path / "papers" / "2024" / "my_paper"
        # Act
        _, _, revision, _ = create_document_trees(nested, None)
        # Assert
        assert revision.root == nested / "03_revision"

    def test_nested_scripts_root_uses_nested_base_path(self, tmp_path):
        """Verify scripts root respects nested project base path."""
        # Arrange
        nested = tmp_path / "papers" / "2024" / "my_paper"
        # Act
        _, _, _, scripts = create_document_trees(nested, None)
        # Assert
        assert scripts.root == nested / "scripts"


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
