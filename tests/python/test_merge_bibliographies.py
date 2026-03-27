#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: merge_bibliographies.py

import os
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

# Try to import bibtexparser and the functions
try:
    import bibtexparser  # noqa: F401
    from merge_bibliographies import (
        deduplicate_entries,
        get_doi,
        merge_bibtex_files,
        merge_entries,
        normalize_title,
    )

    HAS_DEPS = True
except ImportError:
    HAS_DEPS = False

# Skip all tests if bibtexparser not available
pytestmark = pytest.mark.skipif(not HAS_DEPS, reason="bibtexparser not installed")


class TestNormalizeTitle:
    """Test title normalization."""

    def test_normalize_title_lowercase(self):
        """Should convert title to lowercase."""
        result = normalize_title("The Quick Brown Fox")
        assert result == "the quick brown fox"

    def test_normalize_title_removes_latex(self):
        """Should remove LaTeX commands."""
        result = normalize_title(r"\textbf{Brain} Activity")
        assert result == "brain activity"

    def test_normalize_title_removes_punctuation(self):
        """Should remove punctuation marks."""
        result = normalize_title("Title: A Study, Part 1!")
        assert result == "title a study part 1"

    def test_normalize_title_removes_special_chars(self):
        """Should remove special characters."""
        result = normalize_title("Title & Research @ 2024")
        assert result == "title research 2024"

    def test_normalize_title_normalizes_whitespace(self):
        """Should normalize multiple spaces to single space."""
        result = normalize_title("Title   with    spaces")
        assert result == "title with spaces"

    def test_normalize_title_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        result = normalize_title("  Title  ")
        assert result == "title"

    def test_normalize_title_empty_string(self):
        """Should handle empty string."""
        result = normalize_title("")
        assert result == ""

    def test_normalize_title_none(self):
        """Should handle None value."""
        result = normalize_title(None)
        assert result == ""

    def test_normalize_title_complex_latex(self):
        """Should handle complex LaTeX commands."""
        result = normalize_title(r"\emph{Important} \textit{Words}")
        assert result == "important words"

    def test_normalize_title_unicode(self):
        """Should handle unicode characters."""
        result = normalize_title("Café résumé naïve")
        # Letters preserved, special chars removed
        assert "caf" in result.lower()


class TestGetDoi:
    """Test DOI extraction."""

    def test_get_doi_plain(self):
        """Should extract plain DOI."""
        entry = {"doi": "10.1234/test"}
        result = get_doi(entry)
        assert result == "10.1234/test"

    def test_get_doi_with_https_prefix(self):
        """Should strip https://doi.org/ prefix."""
        entry = {"doi": "https://doi.org/10.1234/test"}
        result = get_doi(entry)
        assert result == "10.1234/test"

    def test_get_doi_with_http_prefix(self):
        """Should strip http://doi.org/ prefix."""
        entry = {"doi": "http://doi.org/10.1234/test"}
        result = get_doi(entry)
        assert result == "10.1234/test"

    def test_get_doi_with_dx_prefix(self):
        """Should strip dx.doi.org prefix."""
        entry = {"doi": "https://dx.doi.org/10.1234/test"}
        result = get_doi(entry)
        assert result == "10.1234/test"

    def test_get_doi_empty(self):
        """Should return empty string for missing DOI."""
        entry = {}
        result = get_doi(entry)
        assert result == ""

    def test_get_doi_whitespace(self):
        """Should strip whitespace from DOI."""
        entry = {"doi": "  10.1234/test  "}
        result = get_doi(entry)
        assert result == "10.1234/test"

    def test_get_doi_case_insensitive_url(self):
        """Should handle case-insensitive URL matching."""
        entry = {"doi": "HTTPS://DOI.ORG/10.1234/test"}
        result = get_doi(entry)
        assert result == "10.1234/test"


class TestMergeEntries:
    """Test entry merging."""

    def test_merge_entries_prefers_longer_field(self):
        """Should prefer longer field values."""
        existing = {"title": "Short", "author": "Alice"}
        duplicate = {"title": "Much Longer Title", "year": "2024"}

        result = merge_entries(existing, duplicate)

        assert result["title"] == "Much Longer Title"
        assert result["author"] == "Alice"
        assert result["year"] == "2024"

    def test_merge_entries_fills_missing_fields(self):
        """Should fill in missing fields from duplicate."""
        existing = {"title": "Title", "author": "Alice"}
        duplicate = {"title": "Title", "year": "2024", "journal": "Nature"}

        result = merge_entries(existing, duplicate)

        assert result["year"] == "2024"
        assert result["journal"] == "Nature"

    def test_merge_entries_preserves_existing(self):
        """Should not overwrite existing with empty."""
        existing = {"title": "Title", "author": "Alice", "year": "2024"}
        duplicate = {"title": "Title", "author": "", "abstract": "Abstract"}

        result = merge_entries(existing, duplicate)

        # Should keep existing author (not overwrite with empty)
        assert result["author"] == "Alice"
        assert result["abstract"] == "Abstract"

    def test_merge_entries_returns_copy(self):
        """Should return a new dict, not modify existing."""
        existing = {"title": "Title"}
        duplicate = {"author": "Bob"}

        result = merge_entries(existing, duplicate)

        # Original should be unchanged
        assert "author" not in existing
        assert result["author"] == "Bob"

    def test_merge_entries_empty_duplicate(self):
        """Should handle empty duplicate entry."""
        existing = {"title": "Title", "author": "Alice"}
        duplicate = {}

        result = merge_entries(existing, duplicate)

        assert result["title"] == "Title"
        assert result["author"] == "Alice"

    def test_merge_entries_prefers_content_over_empty(self):
        """Should prefer any content over empty string."""
        existing = {"title": "Title", "abstract": ""}
        duplicate = {"title": "Title", "abstract": "Real abstract content"}

        result = merge_entries(existing, duplicate)

        assert result["abstract"] == "Real abstract content"


class TestDeduplicateEntries:
    """Test entry deduplication."""

    def test_deduplicate_by_doi(self):
        """Should deduplicate by DOI."""
        entries = [
            {"ID": "entry1", "doi": "10.1234/test", "title": "Title", "year": "2024"},
            {"ID": "entry2", "doi": "10.1234/test", "title": "Title", "year": "2024"},
        ]

        unique, stats = deduplicate_entries(entries)

        assert len(unique) == 1
        assert stats["total_input"] == 2
        assert stats["unique_output"] == 1
        assert stats["duplicates_found"] == 1

    def test_deduplicate_by_title_year(self):
        """Should deduplicate by normalized title + year."""
        entries = [
            {"ID": "entry1", "title": "The Brain Study", "year": "2024"},
            {"ID": "entry2", "title": "The Brain Study", "year": "2024"},
        ]

        unique, stats = deduplicate_entries(entries)

        assert len(unique) == 1
        assert stats["duplicates_found"] == 1

    def test_deduplicate_different_years_not_duplicates(self):
        """Should not deduplicate same title with different years."""
        entries = [
            {"ID": "entry1", "title": "Annual Report", "year": "2023"},
            {"ID": "entry2", "title": "Annual Report", "year": "2024"},
        ]

        unique, stats = deduplicate_entries(entries)

        assert len(unique) == 2
        assert stats["duplicates_found"] == 0

    def test_deduplicate_stats(self):
        """Should return accurate statistics."""
        entries = [
            {"ID": "entry1", "doi": "10.1234/a", "title": "Title A", "year": "2024"},
            {"ID": "entry2", "doi": "10.1234/a", "title": "Title A", "year": "2024"},
            {"ID": "entry3", "doi": "10.1234/b", "title": "Title B", "year": "2024"},
        ]

        unique, stats = deduplicate_entries(entries)

        assert stats["total_input"] == 3
        assert stats["unique_output"] == 2
        assert stats["duplicates_found"] == 1
        assert stats["duplicates_merged"] == 1

    def test_deduplicate_empty_list(self):
        """Should handle empty entry list."""
        entries = []

        unique, stats = deduplicate_entries(entries)

        assert len(unique) == 0
        assert stats["total_input"] == 0
        assert stats["unique_output"] == 0

    def test_deduplicate_merges_metadata(self):
        """Should merge metadata from duplicates."""
        entries = [
            {
                "ID": "entry1",
                "doi": "10.1234/test",
                "title": "Title",
                "author": "Alice",
            },
            {
                "ID": "entry2",
                "doi": "10.1234/test",
                "title": "Title",
                "abstract": "Abstract",
            },
        ]

        unique, stats = deduplicate_entries(entries)

        assert len(unique) == 1
        # Should have both author and abstract
        assert unique[0]["author"] == "Alice"
        assert unique[0]["abstract"] == "Abstract"

    def test_deduplicate_doi_takes_precedence(self):
        """DOI matching should take precedence over title matching."""
        entries = [
            {"ID": "entry1", "doi": "10.1234/a", "title": "Title X", "year": "2024"},
            {"ID": "entry2", "doi": "10.1234/a", "title": "Title Y", "year": "2024"},
        ]

        unique, stats = deduplicate_entries(entries)

        # Should be deduplicated by DOI even though titles differ
        assert len(unique) == 1

    def test_deduplicate_no_doi_or_title(self):
        """Should handle entries without DOI or title."""
        entries = [
            {"ID": "entry1", "author": "Alice"},
            {"ID": "entry2", "author": "Bob"},
        ]

        unique, stats = deduplicate_entries(entries)

        # Should keep both (can't deduplicate without DOI or title+year)
        assert len(unique) == 2

    def test_deduplicate_latex_in_titles(self):
        """Should normalize LaTeX commands in titles for comparison."""
        entries = [
            {"ID": "entry1", "title": r"\textbf{Brain} Activity", "year": "2024"},
            {"ID": "entry2", "title": "Brain Activity", "year": "2024"},
        ]

        unique, stats = deduplicate_entries(entries)

        # Should be considered duplicates after normalization
        assert len(unique) == 1

    def test_deduplicate_preserves_order(self):
        """Should preserve entry order (first occurrence wins)."""
        entries = [
            {"ID": "first", "doi": "10.1234/test", "title": "Title"},
            {"ID": "second", "title": "Other", "year": "2024"},
            {"ID": "third", "doi": "10.1234/test", "title": "Title"},
        ]

        unique, stats = deduplicate_entries(entries)

        # First entry with DOI should be kept
        assert unique[0]["ID"] == "first"
        assert unique[1]["ID"] == "second"

    def test_deduplicate_case_insensitive_title(self):
        """Title comparison should be case-insensitive."""
        entries = [
            {"ID": "entry1", "title": "THE BRAIN STUDY", "year": "2024"},
            {"ID": "entry2", "title": "the brain study", "year": "2024"},
        ]

        unique, stats = deduplicate_entries(entries)

        assert len(unique) == 1


class TestMergeBibtexFilesOutputPath:
    """Test output path handling in merge_bibtex_files (issue #68)."""

    def _create_bib_file(self, path, key="test2024", title="Test Title"):
        """Helper to create a minimal .bib file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"@article{{{key},\n  title = {{{title}}},\n  author = {{Author}},\n  year = {{2024}},\n}}\n"
        )

    def test_relative_filename_joins_with_bib_dir(self, tmp_path):
        """'-o bibliography.bib' should output inside bib_dir."""
        bib_dir = tmp_path / "bib_files"
        bib_dir.mkdir()
        self._create_bib_file(bib_dir / "refs.bib")

        merge_bibtex_files(bib_dir, output_file="merged.bib", verbose=False, force=True)

        assert (bib_dir / "merged.bib").exists()

    def test_full_path_with_input_dir_prefix_no_double(self, tmp_path):
        """Full path output should NOT be joined again with bib_dir."""
        bib_dir = tmp_path / "bib_files"
        bib_dir.mkdir()
        self._create_bib_file(bib_dir / "refs.bib")

        # Pass full path as output (the bug scenario from issue #68)
        output = str(bib_dir / "merged.bib")
        merge_bibtex_files(bib_dir, output_file=output, verbose=False, force=True)

        # File should exist at the specified path
        assert Path(output).exists()
        # Should NOT have created a nested path like bib_files/bib_files/merged.bib
        nested = bib_dir / "bib_files" / "merged.bib"
        assert not nested.exists()

    def test_absolute_output_path(self, tmp_path):
        """Absolute output path should be used as-is."""
        bib_dir = tmp_path / "bib_files"
        bib_dir.mkdir()
        self._create_bib_file(bib_dir / "refs.bib")

        out_dir = tmp_path / "output"
        out_dir.mkdir()
        output = str(out_dir / "merged.bib")

        merge_bibtex_files(bib_dir, output_file=output, verbose=False, force=True)

        assert Path(output).exists()

    def test_subdirectory_output_path(self, tmp_path):
        """'-o subdir/merged.bib' should use path as-is (not join with bib_dir)."""
        bib_dir = tmp_path / "bib_files"
        bib_dir.mkdir()
        self._create_bib_file(bib_dir / "refs.bib")

        out_dir = tmp_path / "subdir"
        out_dir.mkdir()
        output = str(out_dir / "merged.bib")

        merge_bibtex_files(bib_dir, output_file=output, verbose=False, force=True)

        assert Path(output).exists()

    def test_output_excludes_itself_from_input(self, tmp_path):
        """Output file should not be included as input even with full path."""
        bib_dir = tmp_path / "bib_files"
        bib_dir.mkdir()
        self._create_bib_file(bib_dir / "refs.bib", key="ref2024", title="Reference")
        # Pre-create the output file in the same dir
        self._create_bib_file(bib_dir / "merged.bib", key="old2024", title="Old")

        merge_bibtex_files(bib_dir, output_file="merged.bib", verbose=False, force=True)

        content = (bib_dir / "merged.bib").read_text()
        assert "ref2024" in content
        # Should not contain old entry from previous merged.bib
        assert "old2024" not in content


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
