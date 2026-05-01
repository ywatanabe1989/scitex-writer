#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/python/test_writer_sections.py

"""Tests for Writer section API methods: get_section, read_section, write_section, _list_sections."""

from pathlib import Path
from unittest.mock import patch

import pytest

from scitex_writer._dataclasses.core._DocumentSection import DocumentSection
from scitex_writer.writer import Writer

# Path to the actual template used as the project dir for integration-style tests
TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent


@pytest.fixture
def writer():
    """Provide a Writer instance attached to the actual template project."""
    with patch("scitex_writer.writer._find_git_root", return_value=TEMPLATE_DIR):
        return Writer(TEMPLATE_DIR)


# ---------------------------------------------------------------------------
# get_section
# ---------------------------------------------------------------------------


class TestGetSection:
    """Tests for Writer.get_section."""

    def test_get_section_returns_document_section_for_manuscript(self, writer):
        """Verify get_section returns a DocumentSection for a manuscript section."""
        section = writer.get_section("abstract", "manuscript")
        assert isinstance(section, DocumentSection)

    def test_get_section_returns_document_section_for_shared(self, writer):
        """Verify get_section returns a DocumentSection for a shared section."""
        section = writer.get_section("title", "shared")
        assert isinstance(section, DocumentSection)

    def test_get_section_manuscript_section_has_path(self, writer):
        """Verify returned DocumentSection has a .path attribute."""
        section = writer.get_section("introduction", "manuscript")
        assert hasattr(section, "path")
        assert isinstance(section.path, Path)

    def test_get_section_shared_section_has_path(self, writer):
        """Verify shared DocumentSection has a .path attribute."""
        section = writer.get_section("authors", "shared")
        assert hasattr(section, "path")
        assert isinstance(section.path, Path)

    def test_get_section_raises_value_error_for_invalid_doc_type(self, writer):
        """Verify get_section raises ValueError for an unknown doc_type."""
        with pytest.raises(ValueError) as exc_info:
            writer.get_section("abstract", "nonexistent_type")
        assert "nonexistent_type" in str(exc_info.value)

    def test_get_section_error_message_lists_valid_doc_types(self, writer):
        """Verify ValueError for invalid doc_type includes valid options."""
        with pytest.raises(ValueError) as exc_info:
            writer.get_section("abstract", "invalid")
        error_msg = str(exc_info.value)
        for valid_type in ("shared", "manuscript", "supplementary", "revision"):
            assert valid_type in error_msg

    def test_get_section_raises_value_error_for_invalid_section_name_in_manuscript(
        self, writer
    ):
        """Verify get_section raises ValueError for a nonexistent section in manuscript."""
        with pytest.raises(ValueError) as exc_info:
            writer.get_section("nonexistent_section_xyz", "manuscript")
        assert "nonexistent_section_xyz" in str(exc_info.value)

    def test_get_section_error_message_lists_available_sections_for_manuscript(
        self, writer
    ):
        """Verify ValueError for invalid section name includes available section names."""
        with pytest.raises(ValueError) as exc_info:
            writer.get_section("bogus_section", "manuscript")
        error_msg = str(exc_info.value)
        # The error message should mention at least one known valid section
        assert "abstract" in error_msg or "introduction" in error_msg

    def test_get_section_raises_value_error_for_invalid_section_name_in_shared(
        self, writer
    ):
        """Verify get_section raises ValueError for a nonexistent section in shared."""
        with pytest.raises(ValueError) as exc_info:
            writer.get_section("nonexistent_shared_section", "shared")
        assert "nonexistent_shared_section" in str(exc_info.value)

    def test_get_section_error_message_lists_available_sections_for_shared(
        self, writer
    ):
        """Verify ValueError for invalid shared section name includes available sections."""
        with pytest.raises(ValueError) as exc_info:
            writer.get_section("bogus_shared_key", "shared")
        error_msg = str(exc_info.value)
        assert "title" in error_msg or "authors" in error_msg

    def test_get_section_manuscript_routes_via_contents(self, writer):
        """Verify manuscript sections are accessed via .contents attribute."""
        section = writer.get_section("abstract", "manuscript")
        # Path should be inside the manuscript contents directory
        assert "01_manuscript" in str(section.path)
        assert "contents" in str(section.path)

    def test_get_section_shared_routes_directly(self, writer):
        """Verify shared sections are accessed directly (not via .contents)."""
        section = writer.get_section("title", "shared")
        # Path should be inside the shared directory
        assert "00_shared" in str(section.path)

    def test_get_section_supplementary_returns_document_section(self, writer):
        """Verify get_section works for supplementary doc_type."""
        section = writer.get_section("methods", "supplementary")
        assert isinstance(section, DocumentSection)

    def test_get_section_revision_returns_document_section(self, writer):
        """Verify get_section works for revision doc_type."""
        section = writer.get_section("introduction", "revision")
        assert isinstance(section, DocumentSection)

    def test_get_section_section_has_read_method(self, writer):
        """Verify returned DocumentSection has a .read() method."""
        section = writer.get_section("abstract", "manuscript")
        assert callable(getattr(section, "read", None))

    def test_get_section_section_has_write_method(self, writer):
        """Verify returned DocumentSection has a .write() method."""
        section = writer.get_section("abstract", "manuscript")
        assert callable(getattr(section, "write", None))


# ---------------------------------------------------------------------------
# read_section
# ---------------------------------------------------------------------------


class TestReadSection:
    """Tests for Writer.read_section."""

    def test_read_section_returns_string(self, writer):
        """Verify read_section returns a string."""
        content = writer.read_section("abstract", "manuscript")
        assert isinstance(content, str)

    def test_read_section_shared_title_returns_string(self, writer):
        """Verify read_section returns a string for shared title."""
        content = writer.read_section("title", "shared")
        assert isinstance(content, str)

    def test_read_section_returns_empty_string_for_missing_file(self, writer):
        """Verify read_section returns empty string when section file does not exist."""
        # Use a section that definitely doesn't have a real file in a tmp setup
        # We mock a DocumentSection whose .read() returns None
        with patch.object(writer, "get_section") as mock_get:
            mock_section = DocumentSection(Path("/nonexistent/path.tex"))
            mock_get.return_value = mock_section
            content = writer.read_section("abstract", "manuscript")
        assert content == ""

    def test_read_section_manuscript_introduction(self, writer):
        """Verify read_section returns a string for manuscript introduction."""
        content = writer.read_section("introduction", "manuscript")
        assert isinstance(content, str)

    def test_read_section_joins_list_content(self, writer):
        """Verify read_section joins list content into a single string."""
        with patch.object(writer, "get_section") as mock_get:
            mock_section = DocumentSection.__new__(DocumentSection)
            mock_section.path = Path("/fake/section.tex")
            mock_section.read = lambda: ["line one", "line two"]
            mock_get.return_value = mock_section
            content = writer.read_section("abstract", "manuscript")
        assert content == "line one\nline two"

    def test_read_section_raises_for_invalid_doc_type(self, writer):
        """Verify read_section propagates ValueError for invalid doc_type."""
        with pytest.raises(ValueError):
            writer.read_section("abstract", "bad_doc_type")

    def test_read_section_raises_for_invalid_section_name(self, writer):
        """Verify read_section propagates ValueError for invalid section name."""
        with pytest.raises(ValueError):
            writer.read_section("totally_missing_section", "manuscript")

    def test_read_section_default_doc_type_is_manuscript(self, writer):
        """Verify default doc_type is manuscript when omitted."""
        content_explicit = writer.read_section("abstract", "manuscript")
        content_default = writer.read_section("abstract")
        assert content_explicit == content_default


# ---------------------------------------------------------------------------
# write_section
# ---------------------------------------------------------------------------


class TestWriteSection:
    """Tests for Writer.write_section."""

    def test_write_section_returns_true_on_success(self, tmp_path):
        """Verify write_section returns True when write succeeds."""
        _setup_minimal_project(tmp_path)
        with patch("scitex_writer.writer._find_git_root", return_value=None):
            w = Writer(tmp_path)

        result = w.write_section("abstract", "Test abstract content.", "manuscript")
        assert result is True

    def test_write_section_content_is_readable_back(self, tmp_path):
        """Verify write_section writes content that read_section can read back."""
        _setup_minimal_project(tmp_path)
        with patch("scitex_writer.writer._find_git_root", return_value=None):
            w = Writer(tmp_path)

        test_content = "This is a unique test abstract for round-trip verification."
        w.write_section("abstract", test_content, "manuscript")
        result = w.read_section("abstract", "manuscript")
        assert result == test_content

    def test_write_section_overwrites_existing_content(self, tmp_path):
        """Verify write_section overwrites previously written content."""
        _setup_minimal_project(tmp_path)
        with patch("scitex_writer.writer._find_git_root", return_value=None):
            w = Writer(tmp_path)

        w.write_section("abstract", "First content.", "manuscript")
        w.write_section("abstract", "Second content.", "manuscript")
        result = w.read_section("abstract", "manuscript")
        assert result == "Second content."

    def test_write_section_shared_title(self, tmp_path):
        """Verify write_section works for shared doc_type."""
        _setup_minimal_project(tmp_path)
        with patch("scitex_writer.writer._find_git_root", return_value=None):
            w = Writer(tmp_path)

        test_title = "My Test Paper Title"
        result = w.write_section("title", test_title, "shared")
        assert result is True
        assert w.read_section("title", "shared") == test_title

    def test_write_section_default_doc_type_is_manuscript(self, tmp_path):
        """Verify default doc_type is manuscript when omitted."""
        _setup_minimal_project(tmp_path)
        with patch("scitex_writer.writer._find_git_root", return_value=None):
            w = Writer(tmp_path)

        test_content = "Abstract written with default doc_type."
        w.write_section("abstract", test_content)
        result = w.read_section("abstract", "manuscript")
        assert result == test_content

    def test_write_and_restore_actual_template(self, writer):
        """Verify write_section on actual template restores original content."""
        original_content = writer.read_section("abstract", "manuscript")
        try:
            writer.write_section(
                "abstract",
                "Temporary test content for write_section round-trip.",
                "manuscript",
            )
            modified_content = writer.read_section("abstract", "manuscript")
            assert (
                modified_content
                == "Temporary test content for write_section round-trip."
            )
        finally:
            # Always restore original content
            writer.write_section("abstract", original_content, "manuscript")
            restored_content = writer.read_section("abstract", "manuscript")
            assert restored_content == original_content

    def test_write_section_raises_for_invalid_doc_type(self, writer):
        """Verify write_section propagates ValueError for invalid doc_type."""
        with pytest.raises(ValueError):
            writer.write_section("abstract", "content", "bad_type")

    def test_write_section_raises_for_invalid_section_name(self, writer):
        """Verify write_section propagates ValueError for invalid section name."""
        with pytest.raises(ValueError):
            writer.write_section("nonexistent_section", "content", "manuscript")


# ---------------------------------------------------------------------------
# _list_sections
# ---------------------------------------------------------------------------


class TestListSections:
    """Tests for Writer._list_sections."""

    def test_list_sections_returns_list(self, writer):
        """Verify _list_sections returns a list."""
        result = writer._list_sections(writer.manuscript.contents)
        assert isinstance(result, list)

    def test_list_sections_returns_list_of_strings(self, writer):
        """Verify _list_sections returns a list of strings."""
        result = writer._list_sections(writer.manuscript.contents)
        assert all(isinstance(name, str) for name in result)

    def test_list_sections_manuscript_includes_abstract(self, writer):
        """Verify _list_sections for manuscript contents includes 'abstract'."""
        result = writer._list_sections(writer.manuscript.contents)
        assert "abstract" in result

    def test_list_sections_manuscript_includes_introduction(self, writer):
        """Verify _list_sections for manuscript contents includes 'introduction'."""
        result = writer._list_sections(writer.manuscript.contents)
        assert "introduction" in result

    def test_list_sections_manuscript_includes_methods(self, writer):
        """Verify _list_sections for manuscript contents includes 'methods'."""
        result = writer._list_sections(writer.manuscript.contents)
        assert "methods" in result

    def test_list_sections_manuscript_includes_results(self, writer):
        """Verify _list_sections for manuscript contents includes 'results'."""
        result = writer._list_sections(writer.manuscript.contents)
        assert "results" in result

    def test_list_sections_manuscript_includes_discussion(self, writer):
        """Verify _list_sections for manuscript contents includes 'discussion'."""
        result = writer._list_sections(writer.manuscript.contents)
        assert "discussion" in result

    def test_list_sections_shared_includes_title(self, writer):
        """Verify _list_sections for shared tree includes 'title'."""
        result = writer._list_sections(writer.shared)
        assert "title" in result

    def test_list_sections_shared_includes_authors(self, writer):
        """Verify _list_sections for shared tree includes 'authors'."""
        result = writer._list_sections(writer.shared)
        assert "authors" in result

    def test_list_sections_shared_includes_keywords(self, writer):
        """Verify _list_sections for shared tree includes 'keywords'."""
        result = writer._list_sections(writer.shared)
        assert "keywords" in result

    def test_list_sections_excludes_private_attributes(self, writer):
        """Verify _list_sections does not include names starting with underscore."""
        result = writer._list_sections(writer.manuscript.contents)
        for name in result:
            assert not name.startswith("_")

    def test_list_sections_excludes_path_only_attributes(self, writer):
        """Verify _list_sections excludes plain Path attributes (e.g., figures dir)."""
        result = writer._list_sections(writer.manuscript.contents)
        # 'figures' and 'tables' are plain Paths, not DocumentSections
        assert "figures" not in result
        assert "tables" not in result

    def test_list_sections_non_empty_for_manuscript(self, writer):
        """Verify _list_sections returns non-empty list for manuscript contents."""
        result = writer._list_sections(writer.manuscript.contents)
        assert len(result) > 0

    def test_list_sections_non_empty_for_shared(self, writer):
        """Verify _list_sections returns non-empty list for shared tree."""
        result = writer._list_sections(writer.shared)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# shared vs manuscript routing
# ---------------------------------------------------------------------------


class TestSharedVsManuscriptRouting:
    """Tests for shared vs manuscript routing difference in get_section."""

    def test_shared_title_path_is_in_shared_dir(self, writer):
        """Verify shared title section path is inside 00_shared."""
        section = writer.get_section("title", "shared")
        assert "00_shared" in str(section.path)

    def test_manuscript_title_path_is_in_manuscript_contents(self, writer):
        """Verify manuscript title section path is inside 01_manuscript/contents."""
        section = writer.get_section("title", "manuscript")
        assert "01_manuscript" in str(section.path)
        assert "contents" in str(section.path)

    def test_shared_and_manuscript_title_are_different_paths(self, writer):
        """Verify shared and manuscript title sections point to different files."""
        shared_section = writer.get_section("title", "shared")
        manuscript_section = writer.get_section("title", "manuscript")
        assert shared_section.path != manuscript_section.path

    def test_get_section_manuscript_not_shared(self, writer):
        """Verify manuscript does not have extra shared-only attributes exposed directly."""
        # 'bibliography' exists in manuscript contents but 'bib_files' (a plain Path) does not
        manuscript_sections = writer._list_sections(writer.manuscript.contents)
        shared_sections = writer._list_sections(writer.shared)
        # Both trees expose 'bibliography' as a DocumentSection
        assert "bibliography" in manuscript_sections
        assert "bibliography" in shared_sections

    def test_shared_doc_raises_for_manuscript_only_section(self, writer):
        """Verify 'introduction' is valid in manuscript but raises in shared."""
        # Introduction exists in manuscript contents
        section = writer.get_section("introduction", "manuscript")
        assert isinstance(section, DocumentSection)

        # Introduction does not exist in shared
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
