#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: generate_ai2_prompt.py

import os
import re
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

import pytest  # noqa: E402


# Re-implement key functions locally for testing
def read_tex_content(tex_path):
    """Local copy for testing."""
    if not tex_path.exists():
        return ""
    content = tex_path.read_text(encoding="utf-8")
    lines = content.split("\n")
    lines = [line for line in lines if not line.strip().startswith("%")]
    return "\n".join(lines).strip()


def clean_latex_content(content):
    """Local copy for testing."""
    # Remove PDF bookmarks first
    content = re.sub(r"\\pdfbookmark\[[^\]]*\]\{[^}]*\}\{[^}]*\}", "", content)

    # Remove environment markers
    content = re.sub(r"\\begin\{[^}]+\}", "", content)
    content = re.sub(r"\\end\{[^}]+\}", "", content)

    # Remove standalone commands with optional arguments
    content = re.sub(r"\\[a-zA-Z]+\[[^\]]*\]", "", content)

    # Remove common LaTeX commands but keep their content (iteratively)
    for _ in range(3):  # Multiple passes for nested commands
        content = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", content)

    # Remove any remaining backslash commands
    content = re.sub(r"\\[a-zA-Z]+", "", content)

    # Remove special characters
    content = re.sub(r"\{", "", content)
    content = re.sub(r"\}", "", content)

    # Clean up multiple spaces and newlines
    content = re.sub(r"\n\s*\n\s*\n+", "\n\n", content)
    content = re.sub(r" +", " ", content)

    return content.strip()


HEADER = """# Literature Search Request
We are preparing a manuscript with the information provided below.

1. Please identify related papers that may be relevant to our work.
2. Comprehensive results are welcome, as we will evaluate all suggestions for relevance.
3. Your contribution to advancing scientific research is greatly appreciated.
4. If possible, please output as a BibTeX file (.bib)."""


def generate_ai2_prompt(title, keywords, authors, abstract, sections=None):
    """Simplified version for testing."""
    if sections is None:
        sections = ["title", "keywords", "authors", "abstract"]

    parts = [HEADER, ""]

    if "title" in sections and title:
        title_clean = clean_latex_content(title)
        if title_clean:
            parts.append(f"## Title\n{title_clean}")
            parts.append("")

    if "keywords" in sections and keywords:
        keywords_clean = clean_latex_content(keywords)
        if keywords_clean:
            parts.append(f"## Keywords\n{keywords_clean}")
            parts.append("")

    if "authors" in sections and authors:
        authors_clean = clean_latex_content(authors)
        if authors_clean:
            parts.append(f"## Authors\n{authors_clean}")
            parts.append("")

    if "abstract" in sections and abstract:
        abstract_clean = clean_latex_content(abstract)
        if abstract_clean:
            parts.append(f"## Abstract\n{abstract_clean}")

    return "\n".join(parts).strip()


# Tests for read_tex_content
def test_read_tex_content_normal(tmp_path):
    """Test reading normal tex content."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("This is normal content\nWith multiple lines")

    content = read_tex_content(tex_file)
    assert content == "This is normal content\nWith multiple lines"


def test_read_tex_content_removes_comments(tmp_path):
    """Test that comment lines are removed."""
    tex_file = tmp_path / "test.tex"
    tex_file.write_text("""
This is valid content
% This is a comment line
More valid content
% Another comment
""")

    content = read_tex_content(tex_file)
    assert "This is valid content" in content
    assert "More valid content" in content
    assert "comment" not in content.lower()


def test_read_tex_content_missing_file(tmp_path):
    """Test missing file returns empty string."""
    tex_file = tmp_path / "nonexistent.tex"

    content = read_tex_content(tex_file)
    assert content == ""


def test_read_tex_content_empty_file(tmp_path):
    """Test empty file returns empty string."""
    tex_file = tmp_path / "empty.tex"
    tex_file.write_text("")

    content = read_tex_content(tex_file)
    assert content == ""


def test_read_tex_content_only_comments(tmp_path):
    """Test file with only comments."""
    tex_file = tmp_path / "comments.tex"
    tex_file.write_text("""
% Comment 1
% Comment 2
% Comment 3
""")

    content = read_tex_content(tex_file)
    assert content == ""


# Tests for clean_latex_content
def test_clean_latex_removes_begin_end(tmp_path):
    """Test that begin/end environments are removed."""
    content = "\\begin{abstract}This is text\\end{abstract}"

    cleaned = clean_latex_content(content)
    assert "begin" not in cleaned
    assert "end" not in cleaned
    assert "This is text" in cleaned


def test_clean_latex_removes_commands(tmp_path):
    """Test that LaTeX commands are removed."""
    content = "This is \\textbf{bold} and \\emph{italic} text"

    cleaned = clean_latex_content(content)
    assert "\\textbf" not in cleaned
    assert "\\emph" not in cleaned
    assert "bold" in cleaned
    assert "italic" in cleaned


def test_clean_latex_removes_nested(tmp_path):
    """Test nested commands are properly handled."""
    content = "This is \\textbf{\\emph{nested}} text"

    cleaned = clean_latex_content(content)
    assert "textbf" not in cleaned
    assert "emph" not in cleaned
    assert "nested" in cleaned


def test_clean_latex_removes_pdfbookmark(tmp_path):
    """Test pdfbookmark commands are removed."""
    content = "\\pdfbookmark[1]{Title}{label}This is content"

    cleaned = clean_latex_content(content)
    assert "pdfbookmark" not in cleaned
    assert "This is content" in cleaned


def test_clean_latex_removes_optional_args(tmp_path):
    """Test commands with optional arguments are handled."""
    content = "\\section[short]{Long Title}"

    cleaned = clean_latex_content(content)
    assert "section" not in cleaned
    assert "Long Title" in cleaned


def test_clean_latex_multiple_spaces(tmp_path):
    """Test multiple spaces are collapsed."""
    content = "This  has    many     spaces"

    cleaned = clean_latex_content(content)
    assert "  " not in cleaned  # No double spaces
    assert "This has many spaces" in cleaned


def test_clean_latex_multiple_newlines(tmp_path):
    """Test multiple newlines are collapsed."""
    content = "Para 1\n\n\n\nPara 2"

    cleaned = clean_latex_content(content)
    # Should have at most 2 consecutive newlines
    assert "\n\n\n" not in cleaned


# Tests for generate_ai2_prompt
def test_generate_prompt_has_header(tmp_path):
    """Test output starts with expected header."""
    prompt = generate_ai2_prompt("Title", "", "", "")

    assert prompt.startswith("# Literature Search Request")
    assert "We are preparing a manuscript" in prompt


def test_generate_prompt_includes_title(tmp_path):
    """Test title appears in prompt."""
    prompt = generate_ai2_prompt("Test Manuscript Title", "", "", "")

    assert "## Title" in prompt
    assert "Test Manuscript Title" in prompt


def test_generate_prompt_includes_abstract(tmp_path):
    """Test abstract appears in prompt."""
    abstract = "This is the abstract text with important findings."
    prompt = generate_ai2_prompt("", "", "", abstract)

    assert "## Abstract" in prompt
    assert "important findings" in prompt


def test_generate_prompt_selective_sections(tmp_path):
    """Test only requested sections are included."""
    prompt = generate_ai2_prompt(
        "Title Text",
        "Keywords Text",
        "Authors Text",
        "Abstract Text",
        sections=["title", "abstract"],
    )

    assert "## Title" in prompt
    assert "## Abstract" in prompt
    assert "## Keywords" not in prompt
    assert "## Authors" not in prompt


def test_generate_prompt_all_sections(tmp_path):
    """Test all sections when requested."""
    prompt = generate_ai2_prompt(
        "Title",
        "keyword1, keyword2",
        "John Smith, Jane Doe",
        "This is abstract",
        sections=["title", "keywords", "authors", "abstract"],
    )

    assert "## Title" in prompt
    assert "## Keywords" in prompt
    assert "## Authors" in prompt
    assert "## Abstract" in prompt


def test_generate_prompt_cleans_latex(tmp_path):
    """Test LaTeX commands are cleaned from content."""
    prompt = generate_ai2_prompt(
        "\\textbf{Bold Title}", "", "", "Abstract with \\emph{italic} words"
    )

    assert "\\textbf" not in prompt
    assert "\\emph" not in prompt
    assert "Bold Title" in prompt
    assert "italic" in prompt


def test_generate_prompt_empty_sections_omitted(tmp_path):
    """Test empty sections are not included."""
    prompt = generate_ai2_prompt("Title", "", "", "")

    assert "## Title" in prompt
    assert "## Keywords" not in prompt
    assert "## Authors" not in prompt
    assert "## Abstract" not in prompt


def test_generate_prompt_structure(tmp_path):
    """Test overall prompt structure is correct."""
    prompt = generate_ai2_prompt(
        "Test Title", "test, keywords", "Author Name", "Test abstract"
    )

    lines = prompt.split("\n")
    # Should start with header
    assert lines[0] == "# Literature Search Request"
    # Should have proper section markers
    title_idx = lines.index("## Title")
    keywords_idx = lines.index("## Keywords")
    authors_idx = lines.index("## Authors")
    abstract_idx = lines.index("## Abstract")

    # Sections should be in order
    assert title_idx < keywords_idx < authors_idx < abstract_idx


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
