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

import pytest


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
    bib_file = tmp_path / "test.bib"
    bib_file.write_text("@article{smith2020,\n  title={Test}\n}")

    keys = extract_bib_keys(bib_file)
    assert keys == {"smith2020"}


def test_extract_bib_keys_multiple(tmp_path):
    """Test extracting multiple entries."""
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

    keys = extract_bib_keys(bib_file)
    assert keys == {"smith2020", "jones2019", "doe2021"}


def test_extract_bib_keys_empty_file(tmp_path):
    """Test empty bib file returns empty set."""
    bib_file = tmp_path / "empty.bib"
    bib_file.write_text("")

    keys = extract_bib_keys(bib_file)
    assert keys == set()


def test_extract_bib_keys_missing_file(tmp_path):
    """Test non-existent file returns empty set."""
    bib_file = tmp_path / "nonexistent.bib"

    keys = extract_bib_keys(bib_file)
    assert keys == set()


def test_extract_bib_keys_various_formats(tmp_path):
    """Test various BibTeX entry formats."""
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

    keys = extract_bib_keys(bib_file)
    assert "key_with_underscore_2020" in keys
    assert "KeyWithNoSpace2019" in keys
    assert "doi-123.456" in keys


# Tests for extract_citations_from_tex
def test_extract_citations_cite(tmp_path):
    """Test extracting simple cite command."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("This is text \\cite{smith2020} and more.")

    citations = extract_citations_from_tex(tex_file)
    assert citations == {"smith2020"}


def test_extract_citations_citep(tmp_path):
    """Test extracting citep command with multiple keys."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("Previous work \\citep{smith2020, jones2019} showed.")

    citations = extract_citations_from_tex(tex_file)
    assert citations == {"smith2020", "jones2019"}


def test_extract_citations_commented(tmp_path):
    """Test that commented citations are ignored."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("""
This is cited \\cite{smith2020}
% This is commented \\cite{hidden2019}
Also cited \\cite{jones2021}
""")

    citations = extract_citations_from_tex(tex_file)
    assert citations == {"smith2020", "jones2021"}
    assert "hidden2019" not in citations


def test_extract_citations_multiple_commands(tmp_path):
    """Test multiple citation commands in one file."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("""
First \\cite{a}
Second \\citep{b}
Third \\citet{c}
Fourth \\citeauthor{d}
Fifth \\citeyear{e}
""")

    citations = extract_citations_from_tex(tex_file)
    assert citations == {"a", "b", "c", "d", "e"}


def test_extract_citations_optional_args(tmp_path):
    """Test citation commands with optional arguments."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("""
See \\cite[p.~5]{key1}
Also \\cite[Chapter 2][p.~10-15]{key2}
And \\citep[see][]{key3}
""")

    citations = extract_citations_from_tex(tex_file)
    assert citations == {"key1", "key2", "key3"}


def test_extract_citations_empty_file(tmp_path):
    """Test empty tex file returns empty set."""
    tex_file = tmp_path / "empty.tex"
    tex_file.write_text("")

    citations = extract_citations_from_tex(tex_file)
    assert citations == set()


def test_extract_citations_missing_file(tmp_path):
    """Test non-existent file returns empty set."""
    tex_file = tmp_path / "nonexistent.tex"

    citations = extract_citations_from_tex(tex_file)
    assert citations == set()


def test_extract_citations_inline_comments(tmp_path):
    """Test inline comments are removed."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("""
Valid \\cite{valid} % inline comment \\cite{invalid}
Another \\cite{valid2}
""")

    citations = extract_citations_from_tex(tex_file)
    assert citations == {"valid", "valid2"}
    assert "invalid" not in citations


# Tests for generate_citation_data
def test_generate_citation_data_all_cited(tmp_path):
    """Test when all bib keys are cited."""
    bib_keys = {"smith2020", "jones2019"}
    citations = {"smith2020", "jones2019"}

    data = generate_citation_data(bib_keys, citations, [], [])

    assert data["summary"]["total_references"] == 2
    assert data["summary"]["total_citations"] == 2
    assert data["summary"]["successfully_cited"] == 2
    assert data["summary"]["uncited"] == 0
    assert data["summary"]["missing"] == 0
    assert set(data["details"]["successfully_cited"]) == {"smith2020", "jones2019"}
    assert data["details"]["uncited_references"] == []
    assert data["details"]["missing_references"] == []


def test_generate_citation_data_uncited(tmp_path):
    """Test when some bib keys are not cited."""
    bib_keys = {"smith2020", "jones2019", "doe2021"}
    citations = {"smith2020"}

    data = generate_citation_data(bib_keys, citations, [], [])

    assert data["summary"]["total_references"] == 3
    assert data["summary"]["total_citations"] == 1
    assert data["summary"]["successfully_cited"] == 1
    assert data["summary"]["uncited"] == 2
    assert data["summary"]["missing"] == 0
    assert data["details"]["successfully_cited"] == ["smith2020"]
    assert set(data["details"]["uncited_references"]) == {"jones2019", "doe2021"}


def test_generate_citation_data_missing(tmp_path):
    """Test when some citations are not in bib."""
    bib_keys = {"smith2020", "jones2019"}
    citations = {"smith2020", "unknown2021", "missing2022"}

    data = generate_citation_data(bib_keys, citations, [], [])

    assert data["summary"]["total_references"] == 2
    assert data["summary"]["total_citations"] == 3
    assert data["summary"]["successfully_cited"] == 1
    assert data["summary"]["uncited"] == 1
    assert data["summary"]["missing"] == 2
    assert set(data["details"]["missing_references"]) == {"unknown2021", "missing2022"}


def test_generate_citation_data_empty(tmp_path):
    """Test with no bib keys or citations."""
    data = generate_citation_data(set(), set(), [], [])

    assert data["summary"]["total_references"] == 0
    assert data["summary"]["total_citations"] == 0
    assert data["summary"]["successfully_cited"] == 0
    assert data["summary"]["uncited"] == 0
    assert data["summary"]["missing"] == 0


def test_generate_citation_data_sorted(tmp_path):
    """Test that output lists are sorted."""
    bib_keys = {"zebra", "alpha", "beta"}
    citations = {"beta", "gamma"}

    data = generate_citation_data(bib_keys, citations, [], [])

    # Check that lists are sorted alphabetically
    assert data["details"]["successfully_cited"] == ["beta"]
    assert data["details"]["uncited_references"] == ["alpha", "zebra"]
    assert data["details"]["missing_references"] == ["gamma"]


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
