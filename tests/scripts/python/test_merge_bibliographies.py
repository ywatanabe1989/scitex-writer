#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: merge_bibliographies.py

import os
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports.
# parents[3] is the REPO ROOT (python -> scripts -> tests -> repo). This used to
# be `.parent.parent.parent`, i.e. `tests/` -- so `scripts/python` was never on
# sys.path, `from merge_bibliographies import ...` always raised ImportError, and
# the bare `except ImportError` below turned EVERY test in this file into a SKIP.
# The suite was green by skipping; the merge was in fact untested.
ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

pytest.importorskip("bibtexparser")

# Imported at module scope, NOT inside a try/except: bibtexparser is already
# handled by importorskip above, so any OTHER import failure here is a real
# breakage of the module under test and must FAIL loudly, never skip.
from merge_bibliographies import (  # noqa: E402
    deduplicate_entries,
    get_doi,
    is_stub,
    merge_bibtex_files,
    merge_entries,
    normalize_title,
)

# A scholar stub carries the stamps check_citations.py gates on.
STUB_ENTRY = {
    "ID": "PintoOrellana2023StatisticalIFF",
    "ENTRYTYPE": "article",
    "title": "Statistical inference for interpretable feature functions",
    "journal": "Pending scitex-scholar metadata lookup",
    "note": "Auto-generated stub",
    "year": "2023",
}
REAL_ENTRY = {
    "ID": "PintoOrellana2023StatisticalIFF",
    "ENTRYTYPE": "article",
    "title": "Statistical inference for interpretable feature functions",
    "author": "Pinto-Orellana, Marco",
    "journal": "Nature",
    "year": "2023",
    "doi": "10.1234/jrs.2023.101",
}

# (bibtexparser availability is handled by the importorskip above.)


class TestNormalizeTitle:
    """Test title normalization."""

    def test_normalize_title_lowercase(self):
        """Should convert title to lowercase."""
        # Arrange
        # Act
        result = normalize_title("The Quick Brown Fox")
        # Assert
        assert result == "the quick brown fox"

    def test_normalize_title_removes_latex(self):
        """Should remove LaTeX commands."""
        # Arrange
        # Act
        result = normalize_title(r"\textbf{Brain} Activity")
        # Assert
        assert result == "brain activity"

    def test_normalize_title_removes_punctuation(self):
        """Should remove punctuation marks."""
        # Arrange
        # Act
        result = normalize_title("Title: A Study, Part 1!")
        # Assert
        assert result == "title a study part 1"

    def test_normalize_title_removes_special_chars(self):
        """Should remove special characters."""
        # Arrange
        # Act
        result = normalize_title("Title & Research @ 2024")
        # Assert
        assert result == "title research 2024"

    def test_normalize_title_normalizes_whitespace(self):
        """Should normalize multiple spaces to single space."""
        # Arrange
        # Act
        result = normalize_title("Title   with    spaces")
        # Assert
        assert result == "title with spaces"

    def test_normalize_title_strips_whitespace(self):
        """Should strip leading/trailing whitespace."""
        # Arrange
        # Act
        result = normalize_title("  Title  ")
        # Assert
        assert result == "title"

    def test_normalize_title_empty_string(self):
        """Should handle empty string."""
        # Arrange
        # Act
        result = normalize_title("")
        # Assert
        assert result == ""

    def test_normalize_title_none(self):
        """Should handle None value."""
        # Arrange
        # Act
        result = normalize_title(None)
        # Assert
        assert result == ""

    def test_normalize_title_complex_latex(self):
        """Should handle complex LaTeX commands."""
        # Arrange
        # Act
        result = normalize_title(r"\emph{Important} \textit{Words}")
        # Assert
        assert result == "important words"

    def test_normalize_title_unicode(self):
        """Should handle unicode characters."""
        # Arrange
        # Act
        result = normalize_title("Café résumé naïve")
        # Letters preserved, special chars removed
        # Assert
        assert "caf" in result.lower()


class TestGetDoi:
    """Test DOI extraction."""

    def test_get_doi_plain(self):
        """Should extract plain DOI."""
        # Arrange
        entry = {"doi": "10.1234/test"}
        # Act
        result = get_doi(entry)
        # Assert
        assert result == "10.1234/test"

    def test_get_doi_with_https_prefix(self):
        """Should strip https://doi.org/ prefix."""
        # Arrange
        entry = {"doi": "https://doi.org/10.1234/test"}
        # Act
        result = get_doi(entry)
        # Assert
        assert result == "10.1234/test"

    def test_get_doi_with_http_prefix(self):
        """Should strip http://doi.org/ prefix."""
        # Arrange
        entry = {"doi": "http://doi.org/10.1234/test"}
        # Act
        result = get_doi(entry)
        # Assert
        assert result == "10.1234/test"

    def test_get_doi_with_dx_prefix(self):
        """Should strip dx.doi.org prefix."""
        # Arrange
        entry = {"doi": "https://dx.doi.org/10.1234/test"}
        # Act
        result = get_doi(entry)
        # Assert
        assert result == "10.1234/test"

    def test_get_doi_empty(self):
        """Should return empty string for missing DOI."""
        # Arrange
        entry = {}
        # Act
        result = get_doi(entry)
        # Assert
        assert result == ""

    def test_get_doi_whitespace(self):
        """Should strip whitespace from DOI."""
        # Arrange
        entry = {"doi": "  10.1234/test  "}
        # Act
        result = get_doi(entry)
        # Assert
        assert result == "10.1234/test"

    def test_get_doi_case_insensitive_url(self):
        """Should handle case-insensitive URL matching."""
        # Arrange
        entry = {"doi": "HTTPS://DOI.ORG/10.1234/test"}
        # Act
        result = get_doi(entry)
        # Assert
        assert result == "10.1234/test"


class TestMergeEntries:
    """Test entry merging."""

    def test_merge_entries_prefers_longer_field(self):
        """Should prefer longer field values."""
        # Arrange
        existing = {"title": "Short", "author": "Alice"}
        duplicate = {"title": "Much Longer Title", "year": "2024"}

        # Act
        result = merge_entries(existing, duplicate)

        # Assert
        assert (
            (result["title"] == "Much Longer Title")
            and (result["author"] == "Alice")
            and (result["year"] == "2024")
        )

    def test_merge_entries_fills_missing_fields(self):
        """Should fill in missing fields from duplicate."""
        # Arrange
        existing = {"title": "Title", "author": "Alice"}
        duplicate = {"title": "Title", "year": "2024", "journal": "Nature"}

        # Act
        result = merge_entries(existing, duplicate)

        # Assert
        assert (result["year"] == "2024") and (result["journal"] == "Nature")

    def test_merge_entries_preserves_existing(self):
        """Should not overwrite existing with empty."""
        # Arrange
        existing = {"title": "Title", "author": "Alice", "year": "2024"}
        duplicate = {"title": "Title", "author": "", "abstract": "Abstract"}

        # Act
        result = merge_entries(existing, duplicate)

        # Should keep existing author (not overwrite with empty)
        # Assert
        assert (result["author"] == "Alice") and (result["abstract"] == "Abstract")

    def test_merge_entries_returns_copy(self):
        """Should return a new dict, not modify existing."""
        # Arrange
        existing = {"title": "Title"}
        duplicate = {"author": "Bob"}

        # Act
        result = merge_entries(existing, duplicate)

        # Original should be unchanged
        # Assert
        assert ("author" not in existing) and (result["author"] == "Bob")

    def test_merge_entries_empty_duplicate(self):
        """Should handle empty duplicate entry."""
        # Arrange
        existing = {"title": "Title", "author": "Alice"}
        duplicate = {}

        # Act
        result = merge_entries(existing, duplicate)

        # Assert
        assert (result["title"] == "Title") and (result["author"] == "Alice")

    def test_merge_entries_prefers_content_over_empty(self):
        """Should prefer any content over empty string."""
        # Arrange
        existing = {"title": "Title", "abstract": ""}
        duplicate = {"title": "Title", "abstract": "Real abstract content"}

        # Act
        result = merge_entries(existing, duplicate)

        # Assert
        assert result["abstract"] == "Real abstract content"


class TestDeduplicateEntries:
    """Test entry deduplication."""

    def test_deduplicate_by_doi(self):
        """Should deduplicate by DOI."""
        # Arrange
        entries = [
            {"ID": "entry1", "doi": "10.1234/test", "title": "Title", "year": "2024"},
            {"ID": "entry2", "doi": "10.1234/test", "title": "Title", "year": "2024"},
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # Assert
        assert (
            (len(unique) == 1)
            and (stats["total_input"] == 2)
            and (stats["unique_output"] == 1)
            and (stats["duplicates_found"] == 1)
        )

    def test_deduplicate_by_cite_key(self):
        """Should deduplicate a repeated cite key (bibtex 'repeated entry')."""
        # Arrange: a stub entry duplicated across input files. No DOI, and the
        # stub's title/year need not match -- the shared cite key alone is what
        # breaks bibtex, so it must collapse to one entry.
        entries = [
            {
                "ID": "PintoOrellana2023StatisticalIFF",
                "title": "Statistical IFF",
                "year": "2023",
            },
            {
                "ID": "PintoOrellana2023StatisticalIFF",
                "note": "Auto-generated stub; replace before submission",
            },
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # Assert
        assert (
            (len(unique) == 1)
            and (stats["duplicates_found"] == 1)
            and (stats["duplicates_merged"] == 1)
        )

    def test_deduplicate_cite_key_takes_precedence_over_differing_content(self):
        """A repeated cite key collapses even when DOI/title differ."""
        # Arrange
        entries = [
            {"ID": "dupkey", "doi": "10.1/a", "title": "Title A", "year": "2023"},
            {"ID": "dupkey", "doi": "10.2/b", "title": "Title B", "year": "2024"},
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # Assert
        assert len(unique) == 1

    def test_deduplicate_distinct_cite_keys_kept(self):
        """Distinct cite keys with no DOI/title overlap must both survive."""
        # Arrange
        entries = [
            {"ID": "keyA", "author": "Alice"},
            {"ID": "keyB", "author": "Bob"},
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # Assert
        assert (len(unique) == 2) and (stats["duplicates_found"] == 0)

    def test_deduplicate_by_title_year(self):
        """Should deduplicate by normalized title + year."""
        # Arrange
        entries = [
            {"ID": "entry1", "title": "The Brain Study", "year": "2024"},
            {"ID": "entry2", "title": "The Brain Study", "year": "2024"},
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # Assert
        assert (len(unique) == 1) and (stats["duplicates_found"] == 1)

    def test_deduplicate_different_years_not_duplicates(self):
        """Should not deduplicate same title with different years."""
        # Arrange
        entries = [
            {"ID": "entry1", "title": "Annual Report", "year": "2023"},
            {"ID": "entry2", "title": "Annual Report", "year": "2024"},
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # Assert
        assert (len(unique) == 2) and (stats["duplicates_found"] == 0)

    def test_deduplicate_stats_stats_total_input_3_and_stats_unique_output_2_and_(self):
        """Should return accurate statistics."""
        # Arrange
        entries = [
            {"ID": "entry1", "doi": "10.1234/a", "title": "Title A", "year": "2024"},
            {"ID": "entry2", "doi": "10.1234/a", "title": "Title A", "year": "2024"},
            {"ID": "entry3", "doi": "10.1234/b", "title": "Title B", "year": "2024"},
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # Assert
        assert (
            (stats["total_input"] == 3)
            and (stats["unique_output"] == 2)
            and (stats["duplicates_found"] == 1)
            and (stats["duplicates_merged"] == 1)
        )

    def test_deduplicate_empty_list(self):
        """Should handle empty entry list."""
        # Arrange
        entries = []

        # Act
        unique, stats = deduplicate_entries(entries)

        # Assert
        assert (
            (len(unique) == 0)
            and (stats["total_input"] == 0)
            and (stats["unique_output"] == 0)
        )

    def test_deduplicate_merges_metadata(self):
        """Should merge metadata from duplicates."""
        # Arrange
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

        # Act
        unique, stats = deduplicate_entries(entries)

        # Assert
        assert (
            (len(unique) == 1)
            and (unique[0]["author"] == "Alice")
            and (unique[0]["abstract"] == "Abstract")
        )

    def test_deduplicate_doi_takes_precedence(self):
        """DOI matching should take precedence over title matching."""
        # Arrange
        entries = [
            {"ID": "entry1", "doi": "10.1234/a", "title": "Title X", "year": "2024"},
            {"ID": "entry2", "doi": "10.1234/a", "title": "Title Y", "year": "2024"},
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # Should be deduplicated by DOI even though titles differ
        # Assert
        assert len(unique) == 1

    def test_deduplicate_no_doi_or_title(self):
        """Should handle entries without DOI or title."""
        # Arrange
        entries = [
            {"ID": "entry1", "author": "Alice"},
            {"ID": "entry2", "author": "Bob"},
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # Should keep both (can't deduplicate without DOI or title+year)
        # Assert
        assert len(unique) == 2

    def test_deduplicate_latex_in_titles(self):
        """Should normalize LaTeX commands in titles for comparison."""
        # Arrange
        entries = [
            {"ID": "entry1", "title": r"\textbf{Brain} Activity", "year": "2024"},
            {"ID": "entry2", "title": "Brain Activity", "year": "2024"},
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # Should be considered duplicates after normalization
        # Assert
        assert len(unique) == 1

    def test_deduplicate_preserves_order(self):
        """Should preserve entry order (first occurrence wins)."""
        # Arrange
        entries = [
            {"ID": "first", "doi": "10.1234/test", "title": "Title"},
            {"ID": "second", "title": "Other", "year": "2024"},
            {"ID": "third", "doi": "10.1234/test", "title": "Title"},
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # First entry with DOI should be kept
        # Assert
        assert (unique[0]["ID"] == "first") and (unique[1]["ID"] == "second")

    def test_deduplicate_case_insensitive_title(self):
        """Title comparison should be case-insensitive."""
        # Arrange
        entries = [
            {"ID": "entry1", "title": "THE BRAIN STUDY", "year": "2024"},
            {"ID": "entry2", "title": "the brain study", "year": "2024"},
        ]

        # Act
        unique, stats = deduplicate_entries(entries)

        # Assert
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
        # Arrange
        bib_dir = tmp_path / "bib_files"
        bib_dir.mkdir()
        self._create_bib_file(bib_dir / "refs.bib")

        # Act
        merge_bibtex_files(bib_dir, output_file="merged.bib", verbose=False, force=True)

        # Assert
        assert (bib_dir / "merged.bib").exists()

    def test_full_path_with_input_dir_prefix_no_double_path_output_exists(
        self, tmp_path
    ):
        # Arrange
        bib_dir = tmp_path / "bib_files"
        bib_dir.mkdir()
        self._create_bib_file(bib_dir / "refs.bib")
        # Pass full path as output (the bug scenario from issue #68)
        output = str(bib_dir / "merged.bib")
        # Act
        merge_bibtex_files(bib_dir, output_file=output, verbose=False, force=True)
        # Act
        # Assert
        assert Path(output).exists()

    def test_full_path_with_input_dir_prefix_no_double_not_nested_exists(
        self, tmp_path
    ):
        # Arrange
        bib_dir = tmp_path / "bib_files"
        bib_dir.mkdir()
        self._create_bib_file(bib_dir / "refs.bib")
        # Pass full path as output (the bug scenario from issue #68)
        output = str(bib_dir / "merged.bib")
        merge_bibtex_files(bib_dir, output_file=output, verbose=False, force=True)
        # File should exist at the specified path
        # Should NOT have created a nested path like bib_files/bib_files/merged.bib
        # Act
        nested = bib_dir / "bib_files" / "merged.bib"
        # Act
        # Assert
        assert not nested.exists()

    def test_absolute_output_path(self, tmp_path):
        """Absolute output path should be used as-is."""
        # Arrange
        bib_dir = tmp_path / "bib_files"
        bib_dir.mkdir()
        self._create_bib_file(bib_dir / "refs.bib")

        out_dir = tmp_path / "output"
        out_dir.mkdir()
        output = str(out_dir / "merged.bib")

        # Act
        merge_bibtex_files(bib_dir, output_file=output, verbose=False, force=True)

        # Assert
        assert Path(output).exists()

    def test_subdirectory_output_path(self, tmp_path):
        """'-o subdir/merged.bib' should use path as-is (not join with bib_dir)."""
        # Arrange
        bib_dir = tmp_path / "bib_files"
        bib_dir.mkdir()
        self._create_bib_file(bib_dir / "refs.bib")

        out_dir = tmp_path / "subdir"
        out_dir.mkdir()
        output = str(out_dir / "merged.bib")

        # Act
        merge_bibtex_files(bib_dir, output_file=output, verbose=False, force=True)

        # Assert
        assert Path(output).exists()

    def test_output_excludes_itself_from_input(self, tmp_path):
        """Output file should not be included as input even with full path."""
        # Arrange
        bib_dir = tmp_path / "bib_files"
        bib_dir.mkdir()
        self._create_bib_file(bib_dir / "refs.bib", key="ref2024", title="Reference")
        # Pre-create the output file in the same dir
        self._create_bib_file(bib_dir / "merged.bib", key="old2024", title="Old")

        merge_bibtex_files(bib_dir, output_file="merged.bib", verbose=False, force=True)

        # Act
        content = (bib_dir / "merged.bib").read_text()
        # Assert
        assert ("ref2024" in content) and ("old2024" not in content)


class TestStubDetection:
    """A stub is defined by scholar's stamps (check_citations.py is the SSoT)."""

    def test_stub_note_stamp_marks_entry_as_stub(self):
        # Arrange
        entry = {"ID": "k", "note": "Auto-generated stub"}
        # Act
        result = is_stub(entry)
        # Assert
        assert result

    def test_stub_journal_stamp_marks_entry_as_stub(self):
        # Arrange
        entry = {"ID": "k", "journal": "Pending scitex-scholar metadata lookup"}
        # Act
        result = is_stub(entry)
        # Assert
        assert result

    def test_resolved_entry_is_not_a_stub(self):
        # Arrange
        # Act
        result = is_stub(REAL_ENTRY)
        # Assert
        assert not result


class TestStubVsRealPrecedence:
    """A REAL entry always beats a STUB when the same cite key appears twice."""

    def test_real_journal_survives_a_stub_duplicate(self):
        # Arrange: the stub's "Pending ..." journal is LONGER than "Nature", so a
        # longest-value-wins merge would have overwritten the real journal.
        entries = [dict(REAL_ENTRY), dict(STUB_ENTRY)]
        # Act
        unique, _stats = deduplicate_entries(entries)
        # Assert
        assert unique[0]["journal"] == "Nature"

    def test_real_entry_wins_even_when_the_stub_is_seen_first(self):
        # Arrange
        entries = [dict(STUB_ENTRY), dict(REAL_ENTRY)]
        # Act
        unique, _stats = deduplicate_entries(entries)
        # Assert
        assert unique[0]["journal"] == "Nature"

    def test_stub_stamp_is_not_copied_onto_the_real_entry(self):
        # Arrange: inheriting note="Auto-generated stub" would make
        # check_citations.py mis-flag this resolved reference as a stub.
        entries = [dict(REAL_ENTRY), dict(STUB_ENTRY)]
        # Act
        unique, _stats = deduplicate_entries(entries)
        # Assert
        assert "note" not in unique[0]

    def test_real_entry_keeps_its_doi_after_merging_a_stub(self):
        # Arrange
        entries = [dict(STUB_ENTRY), dict(REAL_ENTRY)]
        # Act
        unique, _stats = deduplicate_entries(entries)
        # Assert
        assert unique[0]["doi"] == "10.1234/jrs.2023.101"

    def test_two_stubs_stay_stamped_so_the_citation_gate_still_sees_them(self):
        # Arrange: collapsing two stubs must not launder them into a real entry
        entries = [dict(STUB_ENTRY), dict(STUB_ENTRY)]
        # Act
        unique, _stats = deduplicate_entries(entries)
        # Assert
        assert is_stub(unique[0])


class TestMergeIncludesOutputFile:
    """bibliography.bib is CONSUMER-OWNED: merged as an input, never destroyed."""

    def _write(self, path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def _bib_dir_with_stub_sidecar(self, tmp_path):
        bib_dir = tmp_path / "bib_files"
        self._write(
            bib_dir / "bibliography.bib",
            "@article{RealOnly2020,\n  title = {Only In Bibliography},\n"
            "  author = {Author},\n  year = {2020},\n}\n"
            "@article{Dup2023,\n  title = {Dup},\n  author = {Real},\n"
            "  journal = {Nature},\n  year = {2023},\n}\n",
        )
        self._write(
            bib_dir / "_stubs_pending_scholar.bib",
            "@article{Dup2023,\n  title = {Dup},\n"
            "  journal = {Pending scitex-scholar metadata lookup},\n"
            "  note = {Auto-generated stub},\n  year = {2023},\n}\n",
        )
        return bib_dir

    def test_entry_living_only_in_bibliography_survives_the_merge(self, tmp_path):
        # Arrange
        bib_dir = self._bib_dir_with_stub_sidecar(tmp_path)
        # Act
        merge_bibtex_files(bib_dir, verbose=False, force=True, include_output=True)
        # Assert
        assert "RealOnly2020" in (bib_dir / "bibliography.bib").read_text()

    def test_duplicate_cite_key_is_collapsed_to_one_entry(self, tmp_path):
        # Arrange: two files carry Dup2023 — bibtex would say "Repeated entry"
        bib_dir = self._bib_dir_with_stub_sidecar(tmp_path)
        # Act
        merge_bibtex_files(bib_dir, verbose=False, force=True, include_output=True)
        # Assert
        assert (bib_dir / "bibliography.bib").read_text().count("@article{Dup2023") == 1

    def test_merged_duplicate_keeps_the_real_journal(self, tmp_path):
        # Arrange
        bib_dir = self._bib_dir_with_stub_sidecar(tmp_path)
        # Act
        merge_bibtex_files(bib_dir, verbose=False, force=True, include_output=True)
        # Assert
        assert (
            "Pending scitex-scholar" not in (bib_dir / "bibliography.bib").read_text()
        )

    def test_duplicate_inside_bibliography_alone_is_collapsed(self, tmp_path):
        # Arrange: the single-bib case — the merge used to be SKIPPED entirely
        # here, so the repeated key reached bibtex and it exited non-zero.
        bib_dir = tmp_path / "bib_files"
        self._write(
            bib_dir / "bibliography.bib",
            "@article{Dup2023,\n  title = {Dup},\n  author = {Real},\n"
            "  journal = {Nature},\n  year = {2023},\n}\n"
            "@article{Dup2023,\n  title = {Dup},\n"
            "  journal = {Pending scitex-scholar metadata lookup},\n"
            "  note = {Auto-generated stub},\n  year = {2023},\n}\n",
        )
        # Act
        merge_bibtex_files(bib_dir, verbose=False, force=True, include_output=True)
        # Assert
        assert (bib_dir / "bibliography.bib").read_text().count("@article{Dup2023") == 1


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
