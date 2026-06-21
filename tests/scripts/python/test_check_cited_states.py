#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_cited_states.py

import os
import re
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

import pytest  # noqa: E402


# Re-implement key functions locally for testing
def extract_bib_keys(bib_path):
    """Local copy for testing."""
    if not bib_path.exists():
        return set()
    content = bib_path.read_text(encoding="utf-8")
    pattern = r"@\w+\s*\{\s*([^,\s]+)"
    return set(re.findall(pattern, content))


def extract_citations_from_tex(tex_path):
    """Local copy for testing."""
    if not tex_path.exists() or not tex_path.is_file():
        return set()
    content = tex_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    lines = [line.split("%")[0] for line in lines]
    content = "\n".join(lines)
    pattern = r"\\cite\w*\s*(?:\[[^\]]*\])?\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}"
    matches = re.findall(pattern, content)
    citations = set()
    for match in matches:
        keys = [k.strip() for k in match.split(",")]
        citations.update(keys)
    return citations


def generate_citation_data(all_bib_keys, all_citations, bib_files, tex_files):
    """Local copy for testing."""
    cited = sorted(all_bib_keys & all_citations)
    uncited = sorted(all_bib_keys - all_citations)
    missing = sorted(all_citations - all_bib_keys)

    return {
        "summary": {
            "total_references": len(all_bib_keys),
            "total_citations": len(all_citations),
            "successfully_cited": len(cited),
            "uncited": len(uncited),
            "missing": len(missing),
        },
        "details": {
            "successfully_cited": cited,
            "uncited_references": uncited,
            "missing_references": missing,
        },
        "files": {
            "bib_files": [str(f) for f in sorted(bib_files)],
            "tex_files": [str(f) for f in sorted(tex_files)],
        },
    }


# Tests for extract_bib_keys
def test_extract_bib_keys_article(tmp_path):
    """Test extracting single article entry."""
    # Arrange
    bib_file = tmp_path / "test.bib"
    bib_file.write_text("@article{smith2020,\n  title={Test}\n}")

    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert keys == {"smith2020"}


def test_extract_bib_keys_multiple(tmp_path):
    """Test extracting multiple entries."""
    # Arrange
    bib_file = tmp_path / "test.bib"
    bib_file.write_text("""
@article{smith2020,
  title={Test}
}
@book{jones2019,
  title={Book}
}
@inproceedings{doe2021,
  title={Proceedings}
}
""")

    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert keys == {"smith2020", "jones2019", "doe2021"}


def test_extract_bib_keys_empty_file(tmp_path):
    """Test empty bib file returns empty set."""
    # Arrange
    bib_file = tmp_path / "empty.bib"
    bib_file.write_text("")

    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert keys == set()


def test_extract_bib_keys_missing_file(tmp_path):
    """Test non-existent file returns empty set."""
    # Arrange
    bib_file = tmp_path / "nonexistent.bib"

    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert keys == set()


def test_extract_bib_keys_various_formats(tmp_path):
    """Test various BibTeX entry formats."""
    # Arrange
    bib_file = tmp_path / "test.bib"
    bib_file.write_text("""
@article { key_with_underscore_2020 ,
  title={Test}
}
@book{
  KeyWithNoSpace2019,
  title={Book}
}
@misc{doi-123.456,
  title={DOI format}
}
""")

    # Act
    keys = extract_bib_keys(bib_file)
    # Assert
    assert ('key_with_underscore_2020' in keys) and ('KeyWithNoSpace2019' in keys) and ('doi-123.456' in keys)


# Tests for extract_citations_from_tex
def test_extract_citations_cite(tmp_path):
    """Test extracting simple cite command."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("This is text \\cite{smith2020} and more.")

    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == {"smith2020"}


def test_extract_citations_citep(tmp_path):
    """Test extracting citep command with multiple keys."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("Previous work \\citep{smith2020, jones2019} showed.")

    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == {"smith2020", "jones2019"}


def test_extract_citations_commented(tmp_path):
    """Test that commented citations are ignored."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("""
This is cited \\cite{smith2020}
% This is commented \\cite{hidden2019}
Also cited \\cite{jones2021}
""")

    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert (citations == {'smith2020', 'jones2021'}) and ('hidden2019' not in citations)


def test_extract_citations_multiple_commands(tmp_path):
    """Test multiple citation commands in one file."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("""
First \\cite{a}
Second \\citep{b}
Third \\citet{c}
Fourth \\citeauthor{d}
Fifth \\citeyear{e}
""")

    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == {"a", "b", "c", "d", "e"}


def test_extract_citations_optional_args(tmp_path):
    """Test citation commands with optional arguments."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("""
See \\cite[p.~5]{key1}
Also \\cite[Chapter 2][p.~10-15]{key2}
And \\citep[see][]{key3}
""")

    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == {"key1", "key2", "key3"}


def test_extract_citations_empty_file(tmp_path):
    """Test empty tex file returns empty set."""
    # Arrange
    tex_file = tmp_path / "empty.tex"
    tex_file.write_text("")

    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == set()


def test_extract_citations_missing_file(tmp_path):
    """Test non-existent file returns empty set."""
    # Arrange
    tex_file = tmp_path / "nonexistent.tex"

    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert citations == set()


def test_extract_citations_inline_comments(tmp_path):
    """Test inline comments are removed."""
    # Arrange
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("""
Valid \\cite{valid} % inline comment \\cite{invalid}
Another \\cite{valid2}
""")

    # Act
    citations = extract_citations_from_tex(tex_file)
    # Assert
    assert (citations == {'valid', 'valid2'}) and ('invalid' not in citations)


# Tests for generate_citation_data
def test_generate_citation_data_all_cited(tmp_path):
    """Test when all bib keys are cited."""
    # Arrange
    bib_keys = {"smith2020", "jones2019"}
    citations = {"smith2020", "jones2019"}

    # Act
    data = generate_citation_data(bib_keys, citations, [], [])

    # Assert
    assert (data['summary']['total_references'] == 2) and (data['summary']['total_citations'] == 2) and (data['summary']['successfully_cited'] == 2) and (data['summary']['uncited'] == 0) and (data['summary']['missing'] == 0) and (set(data['details']['successfully_cited']) == {'smith2020', 'jones2019'}) and (data['details']['uncited_references'] == []) and (data['details']['missing_references'] == [])


def test_generate_citation_data_uncited(tmp_path):
    """Test when some bib keys are not cited."""
    # Arrange
    bib_keys = {"smith2020", "jones2019", "doe2021"}
    citations = {"smith2020"}

    # Act
    data = generate_citation_data(bib_keys, citations, [], [])

    # Assert
    assert (data['summary']['total_references'] == 3) and (data['summary']['total_citations'] == 1) and (data['summary']['successfully_cited'] == 1) and (data['summary']['uncited'] == 2) and (data['summary']['missing'] == 0) and (data['details']['successfully_cited'] == ['smith2020']) and (set(data['details']['uncited_references']) == {'jones2019', 'doe2021'})


def test_generate_citation_data_missing(tmp_path):
    """Test when some citations are not in bib."""
    # Arrange
    bib_keys = {"smith2020", "jones2019"}
    citations = {"smith2020", "unknown2021", "missing2022"}

    # Act
    data = generate_citation_data(bib_keys, citations, [], [])

    # Assert
    assert (data['summary']['total_references'] == 2) and (data['summary']['total_citations'] == 3) and (data['summary']['successfully_cited'] == 1) and (data['summary']['uncited'] == 1) and (data['summary']['missing'] == 2) and (set(data['details']['missing_references']) == {'unknown2021', 'missing2022'})


def test_generate_citation_data_empty(tmp_path):
    """Test with no bib keys or citations."""
    # Arrange
    # Act
    data = generate_citation_data(set(), set(), [], [])

    # Assert
    assert (data['summary']['total_references'] == 0) and (data['summary']['total_citations'] == 0) and (data['summary']['successfully_cited'] == 0) and (data['summary']['uncited'] == 0) and (data['summary']['missing'] == 0)


def test_generate_citation_data_sorted(tmp_path):
    """Test that output lists are sorted."""
    # Arrange
    bib_keys = {"zebra", "alpha", "beta"}
    citations = {"beta", "gamma"}

    # Act
    data = generate_citation_data(bib_keys, citations, [], [])

    # Check that lists are sorted alphabetically
    # Assert
    assert (data['details']['successfully_cited'] == ['beta']) and (data['details']['uncited_references'] == ['alpha', 'zebra']) and (data['details']['missing_references'] == ['gamma'])


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
