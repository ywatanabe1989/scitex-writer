#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_citations.py (compiler-owns citation stub gate)

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_citations import (  # noqa: E402
    audit_citations,
    extract_cited_keys,
    iter_bib_entries,
    resolve_bib_paths,
    stub_reason,
)


class TestExtractCitedKeys:
    def test_single_cite_command_yields_its_key(self):
        # Arrange
        tex = r"see \cite{Foo2020}"
        # Act
        keys = extract_cited_keys(tex)
        # Assert
        assert keys == {"Foo2020"}

    def test_multiple_keys_in_one_command_all_extracted(self):
        # Arrange
        tex = r"\citep{A2020,B2021, C2022}"
        # Act
        keys = extract_cited_keys(tex)
        # Assert
        assert keys == {"A2020", "B2021", "C2022"}

    def test_citet_with_optional_notes_extracts_key(self):
        # Arrange
        tex = r"\citet[see][p.~5]{Bar2019}"
        # Act
        keys = extract_cited_keys(tex)
        # Assert
        assert keys == {"Bar2019"}

    def test_commented_out_cite_is_ignored(self):
        # Arrange
        tex = "real \\cite{Keep2020}\n% dropped \\cite{Skip1999}"
        # Act
        keys = extract_cited_keys(tex)
        # Assert
        assert keys == {"Keep2020"}

    def test_escaped_percent_is_not_a_comment(self):
        # Arrange
        tex = r"100\% \cite{Keep2020}"
        # Act
        keys = extract_cited_keys(tex)
        # Assert
        assert keys == {"Keep2020"}

    def test_text_without_citations_yields_empty_set(self):
        # Arrange
        tex = "plain text, no cites"
        # Act
        keys = extract_cited_keys(tex)
        # Assert
        assert keys == set()


class TestIterBibEntries:
    def test_parses_cite_key_and_field_values(self):
        # Arrange
        bib = (
            "@article{Foo2020,\n  title = {A Title},\n  doi = {10.1/x},\n"
            '  journal = "Nature"\n}\n'
        )
        # Act
        entries = dict(iter_bib_entries(bib))
        # Assert
        e = entries.get("Foo2020", {})
        assert (e.get("doi") == "10.1/x") and (e.get("journal") == "Nature")

    def test_nested_braces_in_field_value_parsed(self):
        # Arrange
        bib = "@article{Foo2020,\n  title = {A {Nested} Title},\n  doi = {10.1/x}\n}\n"
        # Act
        entries = dict(iter_bib_entries(bib))
        # Assert
        assert entries.get("Foo2020", {}).get("doi") == "10.1/x"

    def test_string_and_comment_entries_are_skipped(self):
        # Arrange
        bib = "@string{pub = {ACME}}\n@article{Real2020,\n  doi = {10.1/x}\n}\n"
        # Act
        keys = {k for k, _ in iter_bib_entries(bib)}
        # Assert
        assert keys == {"Real2020"}


class TestStubReason:
    def test_auto_generated_note_marks_a_stub(self):
        # Arrange
        fields = {"note": "Auto-generated stub; replace before submission."}
        # Act
        reason = stub_reason(fields)
        # Assert
        assert reason is not None

    def test_pending_journal_marker_marks_a_stub(self):
        # Arrange
        fields = {"journal": "Pending scitex-scholar metadata lookup"}
        # Act
        reason = stub_reason(fields)
        # Assert
        assert reason is not None

    def test_complete_entry_is_not_a_stub(self):
        # Arrange
        fields = {"title": "Real", "doi": "10.1/x", "journal": "Nature"}
        # Act
        reason = stub_reason(fields)
        # Assert
        assert reason is None

    def test_missing_doi_alone_is_not_a_stub(self):
        # Arrange: a legitimate book/arXiv entry with no DOI must NOT be flagged
        # (no false positives) -- only a scholar stamp marks a stub.
        fields = {"title": "A Book", "publisher": "MIT Press"}
        # Act
        reason = stub_reason(fields)
        # Assert
        assert reason is None


class TestAuditCitations:
    _ENTRIES = {
        "Good2020": {"doi": "10.1/x", "title": "Real"},
        "Stub2023": {"note": "Auto-generated stub; replace before submission."},
        "NoDoi2018": {"title": "A Book", "publisher": "MIT Press"},
    }

    def test_cited_stub_entry_is_reported(self):
        # Arrange
        cited = {"Stub2023"}
        # Act
        stubs, missing, no_doi = audit_citations(cited, self._ENTRIES)
        # Assert
        assert (len(stubs) == 1) and (stubs[0][0] == "Stub2023")

    def test_missing_entry_reported_as_missing_not_stub(self):
        # Arrange
        cited = {"Ghost2000"}
        # Act
        stubs, missing, no_doi = audit_citations(cited, self._ENTRIES)
        # Assert
        assert (missing == ["Ghost2000"]) and (stubs == [])

    def test_missing_doi_is_info_only_not_stub(self):
        # Arrange
        cited = {"NoDoi2018"}
        # Act
        stubs, missing, no_doi = audit_citations(cited, self._ENTRIES)
        # Assert
        assert (stubs == []) and (no_doi == ["NoDoi2018"])

    def test_clean_cited_entry_passes_all_buckets_empty(self):
        # Arrange
        cited = {"Good2020"}
        # Act
        stubs, missing, no_doi = audit_citations(cited, self._ENTRIES)
        # Assert
        assert (stubs == []) and (missing == []) and (no_doi == [])


class TestResolveBibPaths:
    def _make_symlinked_tree(self, tmp_path):
        """A project whose contents/bibliography.bib is a symlink chain to the
        real (legacy-style) enriched bib -- mirrors the live neurovista tree."""
        real = tmp_path / "shared" / "bib_files" / "enriched.bib"
        real.parent.mkdir(parents=True)
        real.write_text("@article{Foo2020,\n  doi = {10.1/x}\n}\n")
        mid = tmp_path / "shared" / "bibliography.bib"
        mid.symlink_to(real)
        contents = tmp_path / "01_manuscript" / "contents"
        contents.mkdir(parents=True)
        (contents / "bibliography.bib").symlink_to(mid)
        tex = contents / "main.tex"
        tex.write_text(r"\bibliography{bibliography}" + "\n\\cite{Foo2020}")
        return tex, real

    def test_follows_symlink_chain_from_bibliography_command(self, tmp_path):
        # Arrange
        tex, real = self._make_symlinked_tree(tmp_path)
        # Act
        resolved = resolve_bib_paths(tmp_path, [str(tex)], None)
        # Assert
        assert resolved == [real.resolve()]

    def test_explicit_bib_argument_overrides_tex_target(self, tmp_path):
        # Arrange
        tex, real = self._make_symlinked_tree(tmp_path)
        other = tmp_path / "other.bib"
        other.write_text("@article{Bar,\n doi={10.2/y}\n}\n")
        # Act
        resolved = resolve_bib_paths(tmp_path, [str(tex)], str(other))
        # Assert
        assert resolved == [other.resolve()]

    def test_addbibresource_with_extension_resolves(self, tmp_path):
        # Arrange
        contents = tmp_path / "01_manuscript" / "contents"
        contents.mkdir(parents=True)
        bib = contents / "refs.bib"
        bib.write_text("@article{Baz,\n doi={10.3/z}\n}\n")
        tex = contents / "main.tex"
        tex.write_text(r"\addbibresource{refs.bib}")
        # Act
        resolved = resolve_bib_paths(tmp_path, [str(tex)], None)
        # Assert
        assert resolved == [bib.resolve()]


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
