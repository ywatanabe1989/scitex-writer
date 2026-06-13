#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_cited_states.py
# Wave 2 cluster A batch 1 — NM+TQ003+TQ002+TQ007 cleanup.

import os
import sys
from pathlib import Path

import pytest  # noqa: E402

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_cited_states import (  # noqa: E402
    extract_bib_keys,
    extract_citations_from_tex,
    generate_citation_data,
)

# ============================================================================
# extract_bib_keys
# ============================================================================


def test_extract_bib_keys_single_article_entry_returns_one_key(tmp_path):
    """Single @article entry yields the single citation key."""
    # Arrange
    bib_file = tmp_path / "test.bib"
    bib_file.write_text("@article{smith2020,\n  title={Test}\n}")
    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert keys == {"smith2020"}


def test_extract_bib_keys_three_entry_file_yields_three_keys(tmp_path):
    """Three different entry types yield all three keys as a set."""
    # Arrange
    bib_file = tmp_path / "test.bib"
    bib_file.write_text(
        "@article{smith2020, title={Test}}\n"
        "@book{jones2019, title={Book}}\n"
        "@inproceedings{doe2021, title={Proc}}\n"
    )
    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert keys == {"smith2020", "jones2019", "doe2021"}


def test_extract_bib_keys_empty_file_returns_empty_set(tmp_path):
    """Empty .bib file yields the empty set."""
    # Arrange
    bib_file = tmp_path / "empty.bib"
    bib_file.write_text("")
    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert keys == set()


def test_extract_bib_keys_missing_file_returns_empty_set(tmp_path):
    """Non-existent path yields the empty set instead of raising."""
    # Arrange
    bib_file = tmp_path / "nonexistent.bib"
    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert keys == set()


def test_extract_bib_keys_underscore_format_is_recognised(tmp_path):
    """Underscored keys with whitespace around braces are captured."""
    # Arrange
    bib_file = tmp_path / "test.bib"
    bib_file.write_text("@article { key_with_underscore_2020 , title={T} }\n")
    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert "key_with_underscore_2020" in keys


def test_extract_bib_keys_camelcase_format_is_recognised(tmp_path):
    """CamelCase keys without surrounding whitespace are captured."""
    # Arrange
    bib_file = tmp_path / "test.bib"
    bib_file.write_text("@book{\n  KeyWithNoSpace2019,\n  title={B}\n}\n")
    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert "KeyWithNoSpace2019" in keys


def test_extract_bib_keys_doi_style_format_is_recognised(tmp_path):
    """DOI-style keys containing hyphens and dots are captured."""
    # Arrange
    bib_file = tmp_path / "test.bib"
    bib_file.write_text("@misc{doi-123.456, title={D}}\n")
    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert "doi-123.456" in keys


# ============================================================================
# extract_citations_from_tex
# ============================================================================


def test_extract_citations_from_tex_single_cite_returns_one_key(tmp_path):
    """Single \\cite command yields the cited key as a set."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("This is text \\cite{smith2020} and more.")
    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == {"smith2020"}


def test_extract_citations_from_tex_citep_with_multiple_keys(tmp_path):
    """\\citep with comma-separated keys yields all keys."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("Previous work \\citep{smith2020, jones2019} showed.")
    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == {"smith2020", "jones2019"}


def test_extract_citations_from_tex_full_line_comment_is_ignored(tmp_path):
    """A whole-line comment beginning with % is ignored."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        "This is cited \\cite{smith2020}\n% This is commented \\cite{hidden2019}\n"
    )
    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert "hidden2019" not in citations


def test_extract_citations_from_tex_recognises_natbib_variants(tmp_path):
    """natbib variants (\\cite, \\citep, \\citet, \\citeauthor, \\citeyear) are captured."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        "First \\cite{a}\n"
        "Second \\citep{b}\n"
        "Third \\citet{c}\n"
        "Fourth \\citeauthor{d}\n"
        "Fifth \\citeyear{e}\n"
    )
    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == {"a", "b", "c", "d", "e"}


def test_extract_citations_from_tex_optional_args_are_skipped(tmp_path):
    """\\cite[prefix][postfix]{key} captures key, dropping the optional args."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        "See \\cite[p.~5]{key1}\n"
        "Also \\cite[Chapter 2][p.~10-15]{key2}\n"
        "And \\citep[see][]{key3}\n"
    )
    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == {"key1", "key2", "key3"}


def test_extract_citations_from_tex_empty_file_returns_empty_set(tmp_path):
    """Empty .tex file yields the empty set."""
    # Arrange
    tex_file = tmp_path / "empty.tex"
    tex_file.write_text("")
    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == set()


def test_extract_citations_from_tex_missing_file_returns_empty_set(tmp_path):
    """Non-existent .tex path yields the empty set instead of raising."""
    # Arrange
    tex_file = tmp_path / "nonexistent.tex"
    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == set()


def test_extract_citations_from_tex_inline_comment_is_stripped(tmp_path):
    """Inline `% comment` strips the trailing \\cite on the same line."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text(
        "Valid \\cite{valid} % inline comment \\cite{invalid}\nAnother \\cite{valid2}\n"
    )
    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert "invalid" not in citations


# ============================================================================
# generate_citation_data
# ============================================================================


def test_generate_citation_data_full_intersection_marks_all_cited():
    """When every bib key is cited, successfully_cited equals total references."""
    # Arrange
    bib_keys = {"smith2020", "jones2019"}
    citations = {"smith2020", "jones2019"}
    # Act
    data = generate_citation_data(bib_keys, citations, [], [])
    # Assert
    assert data["summary"]["successfully_cited"] == 2


def test_generate_citation_data_full_intersection_reports_zero_uncited():
    """When every bib key is cited, uncited count is zero."""
    # Arrange
    bib_keys = {"smith2020", "jones2019"}
    citations = {"smith2020", "jones2019"}
    # Act
    data = generate_citation_data(bib_keys, citations, [], [])
    # Assert
    assert data["summary"]["uncited"] == 0


def test_generate_citation_data_subset_citations_reports_uncited_count():
    """Bib keys absent from citations are counted as uncited references."""
    # Arrange
    bib_keys = {"smith2020", "jones2019", "doe2021"}
    citations = {"smith2020"}
    # Act
    data = generate_citation_data(bib_keys, citations, [], [])
    # Assert
    assert data["summary"]["uncited"] == 2


def test_generate_citation_data_extra_citations_reports_missing_count():
    """Citations absent from bib are counted as missing references."""
    # Arrange
    bib_keys = {"smith2020", "jones2019"}
    citations = {"smith2020", "unknown2021", "missing2022"}
    # Act
    data = generate_citation_data(bib_keys, citations, [], [])
    # Assert
    assert data["summary"]["missing"] == 2


def test_generate_citation_data_empty_inputs_returns_zero_references():
    """No bib keys and no citations yields total_references == 0."""
    # Arrange
    empty_keys = set()
    empty_citations = set()
    # Act
    data = generate_citation_data(empty_keys, empty_citations, [], [])
    # Assert
    assert data["summary"]["total_references"] == 0


def test_generate_citation_data_uncited_list_is_alphabetically_sorted():
    """uncited_references is returned in alphabetical order."""
    # Arrange
    bib_keys = {"zebra", "alpha", "beta"}
    citations = {"beta", "gamma"}
    # Act
    data = generate_citation_data(bib_keys, citations, [], [])
    # Assert
    assert data["details"]["uncited_references"] == ["alpha", "zebra"]


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
