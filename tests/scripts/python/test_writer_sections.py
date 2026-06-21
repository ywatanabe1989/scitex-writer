#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/python/test_writer_sections.py

"""Tests for Writer section API methods: get_section, read_section, write_section, _list_sections."""

from pathlib import Path

import pytest

from scitex_writer._dataclasses.core._DocumentSection import DocumentSection
from scitex_writer.writer import Writer


# Walk up from this file until we hit the project root (marked by
# pyproject.toml). This survives arbitrary tests/-tree depth changes.
def _find_project_root(start: Path) -> Path:
    p = start.resolve()
    for parent in [p, *p.parents]:
        if (parent / "pyproject.toml").is_file():
            return parent
    raise RuntimeError(f"Could not find pyproject.toml from {start}")


TEMPLATE_DIR = _find_project_root(Path(__file__))


@pytest.fixture
def writer():
    """Provide a Writer instance attached to the actual template project.

    git_strategy=None keeps Writer from initializing/attaching any git
    repository; the template dir is itself a git repo so _find_git_root
    naturally resolves to it without any patching.
    """
    return Writer(TEMPLATE_DIR, git_strategy=None)


# ---------------------------------------------------------------------------
# get_section
# ---------------------------------------------------------------------------


class TestGetSection:
    """Tests for Writer.get_section."""

    def test_get_section_returns_document_section_for_manuscript(self, writer):
        """Verify get_section returns a DocumentSection for a manuscript section."""
        # Arrange
        # Act
        section = writer.get_section("abstract", "manuscript")
        # Assert
        assert isinstance(section, DocumentSection)

    def test_get_section_returns_document_section_for_shared(self, writer):
        """Verify get_section returns a DocumentSection for a shared section."""
        # Arrange
        # Act
        section = writer.get_section("title", "shared")
        # Assert
        assert isinstance(section, DocumentSection)

    def test_get_section_manuscript_section_has_path(self, writer):
        """Verify returned DocumentSection has a .path attribute."""
        # Arrange
        # Act
        section = writer.get_section("introduction", "manuscript")
        # Assert
        assert (hasattr(section, "path")) and (isinstance(section.path, Path))

    def test_get_section_shared_section_has_path(self, writer):
        """Verify shared DocumentSection has a .path attribute."""
        # Arrange
        # Act
        section = writer.get_section("authors", "shared")
        # Assert
        assert (hasattr(section, "path")) and (isinstance(section.path, Path))

    def test_get_section_invalid_doc_type_raises_valueerror_naming_the_bad_type(
        self, writer
    ):
        # Arrange
        # Act
        # Assert
        with pytest.raises(ValueError, match="nonexistent_type"):
            writer.get_section("abstract", "nonexistent_type")

    def test_get_section_invalid_doc_type_error_lists_every_valid_doc_type(
        self, writer
    ):
        # Arrange
        captured = ""
        # Act
        try:
            writer.get_section("abstract", "invalid")
        except ValueError as exc:
            captured = str(exc)
        # Assert
        assert all(
            valid_type in captured
            for valid_type in ("shared", "manuscript", "supplementary", "revision")
        )

    def test_get_section_invalid_manuscript_section_raises_valueerror_naming_the_section(
        self, writer
    ):
        # Arrange
        # Act
        # Assert
        with pytest.raises(ValueError, match="nonexistent_section_xyz"):
            writer.get_section("nonexistent_section_xyz", "manuscript")

    def test_get_section_invalid_manuscript_section_error_lists_available_sections(
        self, writer
    ):
        # Arrange
        captured = ""
        # Act
        try:
            writer.get_section("bogus_section", "manuscript")
        except ValueError as exc:
            captured = str(exc)
        # Assert
        assert "abstract" in captured or "introduction" in captured

    def test_get_section_invalid_shared_section_raises_valueerror_naming_the_section(
        self, writer
    ):
        # Arrange
        # Act
        # Assert
        with pytest.raises(ValueError, match="nonexistent_shared_section"):
            writer.get_section("nonexistent_shared_section", "shared")

    def test_get_section_invalid_shared_section_error_lists_available_sections(
        self, writer
    ):
        # Arrange
        captured = ""
        # Act
        try:
            writer.get_section("bogus_shared_key", "shared")
        except ValueError as exc:
            captured = str(exc)
        # Assert
        assert "title" in captured or "authors" in captured

    def test_get_section_manuscript_routes_via_contents(self, writer):
        """Verify manuscript sections are accessed via .contents attribute."""
        # Arrange
        # Act
        section = writer.get_section("abstract", "manuscript")
        # Path should be inside the manuscript contents directory
        # Assert
        assert ("01_manuscript" in str(section.path)) and (
            "contents" in str(section.path)
        )

    def test_get_section_shared_routes_directly(self, writer):
        """Verify shared sections are accessed directly (not via .contents)."""
        # Arrange
        # Act
        section = writer.get_section("title", "shared")
        # Path should be inside the shared directory
        # Assert
        assert "00_shared" in str(section.path)

    def test_get_section_supplementary_returns_document_section(self, writer):
        """Verify get_section works for supplementary doc_type."""
        # Arrange
        # Act
        section = writer.get_section("methods", "supplementary")
        # Assert
        assert isinstance(section, DocumentSection)

    def test_get_section_revision_returns_document_section(self, writer):
        """Verify get_section works for revision doc_type."""
        # Arrange
        # Act
        section = writer.get_section("introduction", "revision")
        # Assert
        assert isinstance(section, DocumentSection)

    def test_get_section_section_has_read_method(self, writer):
        """Verify returned DocumentSection has a .read() method."""
        # Arrange
        # Act
        section = writer.get_section("abstract", "manuscript")
        # Assert
        assert callable(getattr(section, "read", None))

    def test_get_section_section_has_write_method(self, writer):
        """Verify returned DocumentSection has a .write() method."""
        # Arrange
        # Act
        section = writer.get_section("abstract", "manuscript")
        # Assert
        assert callable(getattr(section, "write", None))


# ---------------------------------------------------------------------------
# read_section
# ---------------------------------------------------------------------------


class TestReadSection:
    """Tests for Writer.read_section."""

    def test_read_section_returns_string(self, writer):
        """Verify read_section returns a string."""
        # Arrange
        # Act
        content = writer.read_section("abstract", "manuscript")
        # Assert
        assert isinstance(content, str)

    def test_read_section_shared_title_returns_string(self, writer):
        """Verify read_section returns a string for shared title."""
        # Arrange
        # Act
        content = writer.read_section("title", "shared")
        # Assert
        assert isinstance(content, str)

    def test_read_section_returns_empty_string_when_section_file_is_absent(
        self, tmp_path
    ):
        """When a section's .tex file is missing, read_section yields ''."""
        # Arrange
        _setup_minimal_project(tmp_path)
        w = Writer(tmp_path, git_strategy=None)
        (tmp_path / "01_manuscript" / "contents" / "abstract.tex").unlink()
        # Act
        content = w.read_section("abstract", "manuscript")
        # Assert
        assert content == ""

    def test_read_section_manuscript_introduction(self, writer):
        """Verify read_section returns a string for manuscript introduction."""
        # Arrange
        # Act
        content = writer.read_section("introduction", "manuscript")
        # Assert
        assert isinstance(content, str)

    def test_read_section_raises_for_invalid_doc_type(self, writer):
        """Verify read_section propagates ValueError for invalid doc_type."""
        # Arrange
        # Act
        # Assert
        with pytest.raises(ValueError):
            writer.read_section("abstract", "bad_doc_type")

    def test_read_section_raises_for_invalid_section_name(self, writer):
        """Verify read_section propagates ValueError for invalid section name."""
        # Arrange
        # Act
        # Assert
        with pytest.raises(ValueError):
            writer.read_section("totally_missing_section", "manuscript")

    def test_read_section_default_doc_type_is_manuscript(self, writer):
        """Verify default doc_type is manuscript when omitted."""
        # Arrange
        content_explicit = writer.read_section("abstract", "manuscript")
        # Act
        content_default = writer.read_section("abstract")
        # Assert
        assert content_explicit == content_default


# ---------------------------------------------------------------------------
# write_section
# ---------------------------------------------------------------------------


class TestWriteSection:
    """Tests for Writer.write_section."""

    def test_write_section_returns_true_on_success(self, tmp_path):
        """Verify write_section returns True when write succeeds."""
        # Arrange
        _setup_minimal_project(tmp_path)
        w = Writer(tmp_path, git_strategy=None)

        # Act
        result = w.write_section("abstract", "Test abstract content.", "manuscript")
        # Assert
        assert result is True

    def test_write_section_content_is_readable_back(self, tmp_path):
        """Verify write_section writes content that read_section can read back."""
        # Arrange
        _setup_minimal_project(tmp_path)
        w = Writer(tmp_path, git_strategy=None)

        test_content = "This is a unique test abstract for round-trip verification."
        w.write_section("abstract", test_content, "manuscript")
        # Act
        result = w.read_section("abstract", "manuscript")
        # Assert
        assert result == test_content

    def test_write_section_overwrites_existing_content(self, tmp_path):
        """Verify write_section overwrites previously written content."""
        # Arrange
        _setup_minimal_project(tmp_path)
        w = Writer(tmp_path, git_strategy=None)

        w.write_section("abstract", "First content.", "manuscript")
        w.write_section("abstract", "Second content.", "manuscript")
        # Act
        result = w.read_section("abstract", "manuscript")
        # Assert
        assert result == "Second content."

    def test_write_section_shared_title(self, tmp_path):
        """Verify write_section works for shared doc_type."""
        # Arrange
        _setup_minimal_project(tmp_path)
        w = Writer(tmp_path, git_strategy=None)

        test_title = "My Test Paper Title"
        # Act
        result = w.write_section("title", test_title, "shared")
        # Assert
        assert (result is True) and (w.read_section("title", "shared") == test_title)

    def test_write_section_default_doc_type_is_manuscript(self, tmp_path):
        """Verify default doc_type is manuscript when omitted."""
        # Arrange
        _setup_minimal_project(tmp_path)
        w = Writer(tmp_path, git_strategy=None)

        test_content = "Abstract written with default doc_type."
        w.write_section("abstract", test_content)
        # Act
        result = w.read_section("abstract", "manuscript")
        # Assert
        assert result == test_content

    def test_write_section_rewrite_reflects_latest_content(self, tmp_path):
        """A second write_section call leaves the latest content readable.

        Uses a throwaway project so the round-trip never mutates the real
        template (the original test wrote into the live template and relied
        on a finally-block to restore it).
        """
        # Arrange
        _setup_minimal_project(tmp_path)
        w = Writer(tmp_path, git_strategy=None)
        w.write_section("abstract", "first pass", "manuscript")
        w.write_section("abstract", "second pass", "manuscript")
        # Act
        result = w.read_section("abstract", "manuscript")
        # Assert
        assert result == "second pass"

    def test_write_section_raises_for_invalid_doc_type(self, writer):
        """Verify write_section propagates ValueError for invalid doc_type."""
        # Arrange
        # Act
        # Assert
        with pytest.raises(ValueError):
            writer.write_section("abstract", "content", "bad_type")

    def test_write_section_raises_for_invalid_section_name(self, writer):
        """Verify write_section propagates ValueError for invalid section name."""
        # Arrange
        # Act
        # Assert
        with pytest.raises(ValueError):
            writer.write_section("nonexistent_section", "content", "manuscript")


# ---------------------------------------------------------------------------
# _list_sections
# ---------------------------------------------------------------------------


class TestListSections:
    """Tests for Writer._list_sections."""

    def test_list_sections_returns_list(self, writer):
        """Verify _list_sections returns a list."""
        # Arrange
        # Act
        result = writer._list_sections(writer.manuscript.contents)
        # Assert
        assert isinstance(result, list)

    def test_list_sections_returns_list_of_strings(self, writer):
        """Verify _list_sections returns a list of strings."""
        # Arrange
        # Act
        result = writer._list_sections(writer.manuscript.contents)
        # Assert
        assert all(isinstance(name, str) for name in result)

    def test_list_sections_manuscript_includes_abstract(self, writer):
        """Verify _list_sections for manuscript contents includes 'abstract'."""
        # Arrange
        # Act
        result = writer._list_sections(writer.manuscript.contents)
        # Assert
        assert "abstract" in result

    def test_list_sections_manuscript_includes_introduction(self, writer):
        """Verify _list_sections for manuscript contents includes 'introduction'."""
        # Arrange
        # Act
        result = writer._list_sections(writer.manuscript.contents)
        # Assert
        assert "introduction" in result

    def test_list_sections_manuscript_includes_methods(self, writer):
        """Verify _list_sections for manuscript contents includes 'methods'."""
        # Arrange
        # Act
        result = writer._list_sections(writer.manuscript.contents)
        # Assert
        assert "methods" in result

    def test_list_sections_manuscript_includes_results(self, writer):
        """Verify _list_sections for manuscript contents includes 'results'."""
        # Arrange
        # Act
        result = writer._list_sections(writer.manuscript.contents)
        # Assert
        assert "results" in result

    def test_list_sections_manuscript_includes_discussion(self, writer):
        """Verify _list_sections for manuscript contents includes 'discussion'."""
        # Arrange
        # Act
        result = writer._list_sections(writer.manuscript.contents)
        # Assert
        assert "discussion" in result

    def test_list_sections_shared_includes_title(self, writer):
        """Verify _list_sections for shared tree includes 'title'."""
        # Arrange
        # Act
        result = writer._list_sections(writer.shared)
        # Assert
        assert "title" in result

    def test_list_sections_shared_includes_authors(self, writer):
        """Verify _list_sections for shared tree includes 'authors'."""
        # Arrange
        # Act
        result = writer._list_sections(writer.shared)
        # Assert
        assert "authors" in result

    def test_list_sections_shared_includes_keywords(self, writer):
        """Verify _list_sections for shared tree includes 'keywords'."""
        # Arrange
        # Act
        result = writer._list_sections(writer.shared)
        # Assert
        assert "keywords" in result

    def test_list_sections_excludes_private_attributes(self, writer):
        """Verify _list_sections does not include names starting with underscore."""
        # Arrange
        # Act
        result = writer._list_sections(writer.manuscript.contents)
        # Assert
        assert all(not name.startswith("_") for name in result)

    def test_list_sections_excludes_path_only_attributes(self, writer):
        """Verify _list_sections excludes plain Path attributes (e.g., figures dir)."""
        # Arrange
        # Act
        result = writer._list_sections(writer.manuscript.contents)
        # 'figures' and 'tables' are plain Paths, not DocumentSections
        # Assert
        assert ("figures" not in result) and ("tables" not in result)

    def test_list_sections_non_empty_for_manuscript(self, writer):
        """Verify _list_sections returns non-empty list for manuscript contents."""
        # Arrange
        # Act
        result = writer._list_sections(writer.manuscript.contents)
        # Assert
        assert len(result) > 0

    def test_list_sections_non_empty_for_shared(self, writer):
        """Verify _list_sections returns non-empty list for shared tree."""
        # Arrange
        # Act
        result = writer._list_sections(writer.shared)
        # Assert
        assert len(result) > 0


# ---------------------------------------------------------------------------
# shared vs manuscript routing
# ---------------------------------------------------------------------------


class TestSharedVsManuscriptRouting:
    """Tests for shared vs manuscript routing difference in get_section."""

    def test_shared_title_path_is_in_shared_dir(self, writer):
        """Verify shared title section path is inside 00_shared."""
        # Arrange
        # Act
        section = writer.get_section("title", "shared")
        # Assert
        assert "00_shared" in str(section.path)

    def test_manuscript_title_path_is_in_manuscript_contents(self, writer):
        """Verify manuscript title section path is inside 01_manuscript/contents."""
        # Arrange
        # Act
        section = writer.get_section("title", "manuscript")
        # Assert
        assert ("01_manuscript" in str(section.path)) and (
            "contents" in str(section.path)
        )

    def test_shared_and_manuscript_title_are_different_paths(self, writer):
        """Verify shared and manuscript title sections point to different files."""
        # Arrange
        shared_section = writer.get_section("title", "shared")
        # Act
        manuscript_section = writer.get_section("title", "manuscript")
        # Assert
        assert shared_section.path != manuscript_section.path

    def test_get_section_manuscript_not_shared(self, writer):
        """Verify manuscript does not have extra shared-only attributes exposed directly."""
        # 'bibliography' exists in manuscript contents but 'bib_files' (a plain Path) does not
        # Arrange
        manuscript_sections = writer._list_sections(writer.manuscript.contents)
        # Act
        shared_sections = writer._list_sections(writer.shared)
        # Both trees expose 'bibliography' as a DocumentSection
        # Assert
        assert ("bibliography" in manuscript_sections) and (
            "bibliography" in shared_sections
        )

    def test_shared_doc_raises_for_manuscript_only_section_section_is_documentsection(
        self, writer
    ):
        # Arrange
        # Act
        section = writer.get_section("introduction", "manuscript")
        # Act
        # Assert
        assert isinstance(section, DocumentSection)

    def test_shared_doc_raises_for_manuscript_only_section_raises_valueerror(
        self, writer
    ):
        # Arrange
        # Act
        section = writer.get_section("introduction", "manuscript")
        # Act
        # Assert
        with pytest.raises(ValueError):
            writer.get_section("introduction", "shared")


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _setup_minimal_project(project_dir: Path) -> None:
    """Create a minimal valid project structure with required section files."""
    (project_dir / "00_shared").mkdir(parents=True, exist_ok=True)
    (project_dir / "01_manuscript" / "contents").mkdir(parents=True, exist_ok=True)
    (project_dir / "02_supplementary" / "contents").mkdir(parents=True, exist_ok=True)
    (project_dir / "03_revision" / "contents").mkdir(parents=True, exist_ok=True)
    (project_dir / "scripts").mkdir(parents=True, exist_ok=True)

    # Shared section files
    shared_dir = project_dir / "00_shared"
    (shared_dir / "title.tex").write_text("Test Title")
    (shared_dir / "authors.tex").write_text("Test Author")
    (shared_dir / "keywords.tex").write_text("test, keywords")
    (shared_dir / "journal_name.tex").write_text("Test Journal")
    bib_dir = shared_dir / "bib_files"
    bib_dir.mkdir(parents=True, exist_ok=True)
    (bib_dir / "bibliography.bib").write_text("")

    # Manuscript section files
    ms_contents = project_dir / "01_manuscript" / "contents"
    for section in (
        "abstract",
        "introduction",
        "methods",
        "results",
        "discussion",
        "title",
        "authors",
        "keywords",
        "journal_name",
        "graphical_abstract",
        "highlights",
        "data_availability",
        "additional_info",
        "wordcount",
    ):
        (ms_contents / f"{section}.tex").write_text(f"Placeholder {section}")
    (ms_contents / "bibliography.bib").write_text("")

    # Supplementary section files
    sup_contents = project_dir / "02_supplementary" / "contents"
    for section in (
        "abstract",
        "introduction",
        "methods",
        "results",
        "discussion",
        "title",
        "authors",
        "keywords",
        "journal_name",
        "graphical_abstract",
        "highlights",
        "data_availability",
        "additional_info",
        "wordcount",
    ):
        (sup_contents / f"{section}.tex").write_text(f"Placeholder {section}")
    (sup_contents / "bibliography.bib").write_text("")

    # Revision section files
    rev_contents = project_dir / "03_revision" / "contents"
    for section in (
        "abstract",
        "introduction",
        "methods",
        "results",
        "discussion",
        "title",
        "authors",
        "keywords",
        "journal_name",
        "graphical_abstract",
        "highlights",
        "data_availability",
        "additional_info",
        "wordcount",
    ):
        (rev_contents / f"{section}.tex").write_text(f"Placeholder {section}")
    (rev_contents / "bibliography.bib").write_text("")


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
