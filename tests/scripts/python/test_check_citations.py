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
    def test_simple_cite(self):
        assert extract_cited_keys(r"see \cite{Foo2020}") == {"Foo2020"}

    def test_multiple_keys_in_one_command(self):
        assert extract_cited_keys(r"\citep{A2020,B2021, C2022}") == {
            "A2020",
            "B2021",
            "C2022",
        }

    def test_citet_and_optional_notes(self):
        assert extract_cited_keys(r"\citet[see][p.~5]{Bar2019}") == {"Bar2019"}

    def test_commented_out_cite_ignored(self):
        tex = "real \\cite{Keep2020}\n% dropped \\cite{Skip1999}"
        assert extract_cited_keys(tex) == {"Keep2020"}

    def test_escaped_percent_not_treated_as_comment(self):
        assert extract_cited_keys(r"100\% \cite{Keep2020}") == {"Keep2020"}

    def test_no_citations(self):
        assert extract_cited_keys("plain text, no cites") == set()


class TestIterBibEntries:
    def test_parses_key_and_fields(self):
        bib = (
            "@article{Foo2020,\n  title = {A Title},\n  doi = {10.1/x},\n"
            '  journal = "Nature"\n}\n'
        )
        entries = dict(iter_bib_entries(bib))
        e = entries.get("Foo2020", {})
        assert (e.get("doi") == "10.1/x") and (e.get("journal") == "Nature")

    def test_nested_braces_in_value(self):
        bib = "@article{Foo2020,\n  title = {A {Nested} Title},\n  doi = {10.1/x}\n}\n"
        entries = dict(iter_bib_entries(bib))
        assert entries.get("Foo2020", {}).get("doi") == "10.1/x"

    def test_skips_string_and_comment_entries(self):
        bib = "@string{pub = {ACME}}\n@article{Real2020,\n  doi = {10.1/x}\n}\n"
        keys = {k for k, _ in iter_bib_entries(bib)}
        assert keys == {"Real2020"}


class TestStubReason:
    def test_note_marker_is_stub(self):
        fields = {"note": "Auto-generated stub; replace before submission."}
        assert stub_reason(fields) is not None

    def test_journal_marker_is_stub(self):
        fields = {"journal": "Pending scitex-scholar metadata lookup"}
        assert stub_reason(fields) is not None

    def test_clean_entry_is_not_stub(self):
        fields = {"title": "Real", "doi": "10.1/x", "journal": "Nature"}
        assert stub_reason(fields) is None

    def test_no_doi_alone_is_not_a_stub(self):
        # A legitimate book/arXiv entry with no DOI must NOT be flagged (no
        # false positives) -- only a scholar stamp marks a stub.
        fields = {"title": "A Book", "publisher": "MIT Press"}
        assert stub_reason(fields) is None


class TestAuditCitations:
    _ENTRIES = {
        "Good2020": {"doi": "10.1/x", "title": "Real"},
        "Stub2023": {"note": "Auto-generated stub; replace before submission."},
        "NoDoi2018": {"title": "A Book", "publisher": "MIT Press"},
    }

    def test_stub_is_reported(self):
        stubs, missing, no_doi = audit_citations({"Stub2023"}, self._ENTRIES)
        assert (len(stubs) == 1) and (stubs[0][0] == "Stub2023")

    def test_missing_entry_is_reported_not_stub(self):
        stubs, missing, no_doi = audit_citations({"Ghost2000"}, self._ENTRIES)
        assert (missing == ["Ghost2000"]) and (stubs == [])

    def test_no_doi_is_info_only_not_stub(self):
        stubs, missing, no_doi = audit_citations({"NoDoi2018"}, self._ENTRIES)
        assert (stubs == []) and (no_doi == ["NoDoi2018"])

    def test_clean_citation_passes(self):
        stubs, missing, no_doi = audit_citations({"Good2020"}, self._ENTRIES)
        assert (stubs == []) and (missing == []) and (no_doi == [])


class TestResolveBibPaths:
    def _make_tree(self, tmp_path):
        """A project whose contents/bibliography.bib is a symlink chain to the
        real (legacy-style) enriched bib -- mirrors the live neurovista tree."""
        real = tmp_path / "shared" / "bib_files" / "enriched.bib"
        real.parent.mkdir(parents=True)
        real.write_text("@article{Foo2020,\n  doi = {10.1/x}\n}\n")
        mid = tmp_path / "shared" / "bibliography.bib"
        mid.symlink_to(real)
        contents = tmp_path / "01_manuscript" / "contents"
        contents.mkdir(parents=True)
        link = contents / "bibliography.bib"
        link.symlink_to(mid)
        tex = contents / "main.tex"
        tex.write_text(r"\bibliography{bibliography}" + "\n\\cite{Foo2020}")
        return tex, real

    def test_follows_symlink_chain_from_bibliography_command(self, tmp_path):
        tex, real = self._make_tree(tmp_path)
        resolved = resolve_bib_paths(tmp_path, [str(tex)], None)
        assert resolved == [real.resolve()]

    def test_explicit_bib_arg_wins(self, tmp_path):
        tex, real = self._make_tree(tmp_path)
        other = tmp_path / "other.bib"
        other.write_text("@article{Bar,\n doi={10.2/y}\n}\n")
        resolved = resolve_bib_paths(tmp_path, [str(tex)], str(other))
        assert resolved == [other.resolve()]

    def test_addbibresource_with_extension(self, tmp_path):
        contents = tmp_path / "01_manuscript" / "contents"
        contents.mkdir(parents=True)
        bib = contents / "refs.bib"
        bib.write_text("@article{Baz,\n doi={10.3/z}\n}\n")
        tex = contents / "main.tex"
        tex.write_text(r"\addbibresource{refs.bib}")
        resolved = resolve_bib_paths(tmp_path, [str(tex)], None)
        assert resolved == [bib.resolve()]


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
