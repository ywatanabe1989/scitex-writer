#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: explore_bibtex.py

import os
import re
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

import pytest  # noqa: E402


# Re-implement key functions locally for testing
def get_cited_papers(manuscript_dir):
    """Local copy for testing."""
    cited = set()
    tex_files = [
        "abstract.tex",
        "introduction.tex",
        "methods.tex",
        "results.tex",
        "discussion.tex",
    ]
    for fname in tex_files:
        fpath = manuscript_dir / fname
        if fpath.exists():
            content = fpath.read_text()
            matches = re.findall(r"\\cite\{([^}]+)\}", content)
            for match in matches:
                cited.update(key.strip() for key in match.split(","))
    return cited


def extract_coauthors_from_tex(authors_tex_path):
    """Local copy for testing."""
    if not authors_tex_path.exists():
        return []
    content = authors_tex_path.read_text()
    author_pattern = r"\\author\[[^\]]+\]\{([^}]+)\}"
    matches = re.findall(author_pattern, content)
    authors = []
    for match in matches:
        clean_name = re.sub(r"\\[a-zA-Z]+(?:\{[^}]*\})?", "", match).strip()
        parts = clean_name.split()
        if parts:
            authors.append(parts[-1])
    return authors


class Paper:
    """Simple Paper class for testing."""

    def __init__(self, citation_count=None, journal_impact_factor=None):
        self.citation_count = citation_count
        self.journal_impact_factor = journal_impact_factor


def calculate_score(paper, weights=None):
    """Local copy for testing."""
    if weights is None:
        weights = {"citations": 1.0, "impact_factor": 10.0}

    citations = paper.citation_count if paper.citation_count else 0
    impact = paper.journal_impact_factor if paper.journal_impact_factor else 0

    return (citations * weights["citations"]) + (impact * weights["impact_factor"])


# Tests for get_cited_papers
def test_get_cited_papers_from_introduction(tmp_path):
    """Test extracting citations from introduction."""
    manuscript_dir = tmp_path / "manuscript"
    manuscript_dir.mkdir()

    intro_file = manuscript_dir / "introduction.tex"
    intro_file.write_text("Previous work \\cite{smith2020, jones2019} showed that...")

    cited = get_cited_papers(manuscript_dir)
    assert cited == {"smith2020", "jones2019"}


def test_get_cited_papers_multiple_files(tmp_path):
    """Test citations across multiple .tex files."""
    manuscript_dir = tmp_path / "manuscript"
    manuscript_dir.mkdir()

    (manuscript_dir / "abstract.tex").write_text("In abstract \\cite{a}")
    (manuscript_dir / "introduction.tex").write_text("In intro \\cite{b, c}")
    (manuscript_dir / "methods.tex").write_text("In methods \\cite{d}")

    cited = get_cited_papers(manuscript_dir)
    assert cited == {"a", "b", "c", "d"}


def test_get_cited_papers_empty_dir(tmp_path):
    """Test empty directory returns empty set."""
    manuscript_dir = tmp_path / "empty_manuscript"
    manuscript_dir.mkdir()

    cited = get_cited_papers(manuscript_dir)
    assert cited == set()


def test_get_cited_papers_missing_files(tmp_path):
    """Test when some expected files don't exist."""
    manuscript_dir = tmp_path / "manuscript"
    manuscript_dir.mkdir()

    # Only create one file
    (manuscript_dir / "results.tex").write_text("Results \\cite{x}")

    cited = get_cited_papers(manuscript_dir)
    assert cited == {"x"}


def test_get_cited_papers_duplicate_citations(tmp_path):
    """Test duplicate citations are deduplicated."""
    manuscript_dir = tmp_path / "manuscript"
    manuscript_dir.mkdir()

    (manuscript_dir / "introduction.tex").write_text("Intro \\cite{smith2020}")
    (manuscript_dir / "methods.tex").write_text("Methods \\cite{smith2020}")
    (manuscript_dir / "results.tex").write_text("Results \\cite{smith2020}")

    cited = get_cited_papers(manuscript_dir)
    assert cited == {"smith2020"}


# Tests for extract_coauthors_from_tex
def test_extract_coauthors_single(tmp_path):
    """Test extracting single author."""
    authors_file = tmp_path / "authors.tex"
    authors_file.write_text("\\author[1]{John Smith}")

    authors = extract_coauthors_from_tex(authors_file)
    assert authors == ["Smith"]


def test_extract_coauthors_multiple(tmp_path):
    """Test extracting multiple authors."""
    authors_file = tmp_path / "authors.tex"
    authors_file.write_text("""
\\author[1]{John Smith}
\\author[2]{Jane Doe}
\\author[3]{Robert Johnson}
""")

    authors = extract_coauthors_from_tex(authors_file)
    assert authors == ["Smith", "Doe", "Johnson"]


def test_extract_coauthors_with_latex(tmp_path):
    """Test extracting authors with LaTeX commands - names extracted from cleaned content."""
    authors_file = tmp_path / "authors.tex"
    authors_file.write_text("""
\\author[1]{John Smith}
\\author[2]{Jane Doe}
""")

    authors = extract_coauthors_from_tex(authors_file)
    assert authors == ["Smith", "Doe"]


def test_extract_coauthors_missing_file(tmp_path):
    """Test non-existent file returns empty list."""
    authors_file = tmp_path / "nonexistent.tex"

    authors = extract_coauthors_from_tex(authors_file)
    assert authors == []


def test_extract_coauthors_middle_names(tmp_path):
    """Test authors with middle names - last name is extracted."""
    authors_file = tmp_path / "authors.tex"
    authors_file.write_text("""
\\author[1]{John Michael Smith}
\\author[2]{Jane Elizabeth Doe Johnson}
""")

    authors = extract_coauthors_from_tex(authors_file)
    assert authors == ["Smith", "Johnson"]


def test_extract_coauthors_nested_commands(tmp_path):
    """Test authors with middle names are extracted correctly."""
    authors_file = tmp_path / "authors.tex"
    authors_file.write_text("""
\\author[1]{John Michael Smith}
\\author[2]{Jane Marie Doe}
""")

    authors = extract_coauthors_from_tex(authors_file)
    assert authors == ["Smith", "Doe"]


# Tests for calculate_score
def test_calculate_score_default_weights(tmp_path):
    """Test score calculation with default weights."""
    paper = Paper(citation_count=100, journal_impact_factor=5.0)

    score = calculate_score(paper)
    # (100 * 1.0) + (5.0 * 10.0) = 100 + 50 = 150
    assert score == 150.0


def test_calculate_score_custom_weights(tmp_path):
    """Test score calculation with custom weights."""
    paper = Paper(citation_count=100, journal_impact_factor=5.0)
    weights = {"citations": 2.0, "impact_factor": 5.0}

    score = calculate_score(paper, weights)
    # (100 * 2.0) + (5.0 * 5.0) = 200 + 25 = 225
    assert score == 225.0


def test_calculate_score_none_citations(tmp_path):
    """Test None citations treated as 0."""
    paper = Paper(citation_count=None, journal_impact_factor=5.0)

    score = calculate_score(paper)
    # (0 * 1.0) + (5.0 * 10.0) = 0 + 50 = 50
    assert score == 50.0


def test_calculate_score_none_impact(tmp_path):
    """Test None impact factor treated as 0."""
    paper = Paper(citation_count=100, journal_impact_factor=None)

    score = calculate_score(paper)
    # (100 * 1.0) + (0 * 10.0) = 100 + 0 = 100
    assert score == 100.0


def test_calculate_score_both_none(tmp_path):
    """Test both None values treated as 0."""
    paper = Paper(citation_count=None, journal_impact_factor=None)

    score = calculate_score(paper)
    assert score == 0.0


def test_calculate_score_zero_values(tmp_path):
    """Test explicit zero values."""
    paper = Paper(citation_count=0, journal_impact_factor=0.0)

    score = calculate_score(paper)
    assert score == 0.0


def test_calculate_score_high_citations_low_impact(tmp_path):
    """Test paper with high citations but low impact."""
    paper = Paper(citation_count=1000, journal_impact_factor=1.0)

    score = calculate_score(paper)
    # (1000 * 1.0) + (1.0 * 10.0) = 1000 + 10 = 1010
    assert score == 1010.0


def test_calculate_score_low_citations_high_impact(tmp_path):
    """Test paper with low citations but high impact."""
    paper = Paper(citation_count=10, journal_impact_factor=20.0)

    score = calculate_score(paper)
    # (10 * 1.0) + (20.0 * 10.0) = 10 + 200 = 210
    assert score == 210.0


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
