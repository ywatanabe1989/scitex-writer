#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/prompts/_ai2.py

"""AI2 Asta (Semantic Scholar) prompt generation from manuscript files.

Uses tag-based templates that can be customized via environment variables:
    SCITEX_WRITER_PROMPT_ASTA_RELATED=/path/to/custom_related.md
    SCITEX_WRITER_PROMPT_ASTA_COAUTHORS=/path/to/custom_coauthors.md

Available tags in templates:
    {title}    - Manuscript title
    {abstract} - Manuscript abstract
    {keywords} - Keywords (comma-separated)
    {authors}  - Author names (comma-separated)
"""

import os
import re
from pathlib import Path
from typing import TypedDict

# Default data directory
_DEFAULT_DATA_DIR = Path(__file__).parent / "data"

# Template tags
TEMPLATE_TAGS = ["title", "abstract", "keywords", "authors"]


class AI2PromptResult(TypedDict):
    """Result from AI2 prompt generation."""

    success: bool
    prompt: str
    search_type: str
    next_steps: list[str]
    error: str | None


def _get_template_path(search_type: str) -> Path:
    """Get path to Asta template, checking env overrides first."""
    env_key = f"SCITEX_WRITER_PROMPT_ASTA_{search_type.upper()}"
    if env_path := os.environ.get(env_key):
        return Path(env_path)

    if prompt_dir := os.environ.get("SCITEX_WRITER_PROMPT_DIR"):
        custom_path = Path(prompt_dir) / f"asta_{search_type}.md"
        if custom_path.exists():
            return custom_path

    return _DEFAULT_DATA_DIR / f"asta_{search_type}.md"


def _read_tex_content(tex_path: Path) -> str:
    """Read raw content from .tex file, removing comments.

    Args:
        tex_path: Path to the .tex file.

    Returns:
        Content with LaTeX comments removed.
    """
    if not tex_path.exists():
        return ""

    content = tex_path.read_text(encoding="utf-8")

    # Remove LaTeX comments (lines starting with %)
    lines = []
    for line in content.split("\n"):
        # Remove inline comments (but preserve escaped \%)
        line = re.sub(r"(?<!\\)%.*$", "", line)
        lines.append(line)

    return "\n".join(lines).strip()


def _clean_latex(text: str) -> str:
    """Remove common LaTeX commands from text for plain text output.

    Args:
        text: Text possibly containing LaTeX commands.

    Returns:
        Cleaned text with LaTeX commands removed.
    """
    # Remove \pdfbookmark and similar commands
    text = re.sub(r"\\pdfbookmark\[[^\]]*\]\{[^}]*\}\{[^}]*\}", "", text)
    # Remove \begin{...} and \end{...}
    text = re.sub(r"\\begin\{[^}]*\}", "", text)
    text = re.sub(r"\\end\{[^}]*\}", "", text)
    # Remove \sep
    text = re.sub(r"\\sep", ",", text)
    # Remove common formatting commands
    text = re.sub(r"\\textbf\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\textit\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\emph\{([^}]*)\}", r"\1", text)
    # Remove \label{...}
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _extract_title(shared_path: Path) -> str:
    """Extract title from shared metadata."""
    title_file = shared_path / "title.tex"
    if title_file.exists():
        content = _read_tex_content(title_file)
        # Remove \title{} wrapper if present
        match = re.search(r"\\title\{(.+?)\}", content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return content
    return ""


def _extract_abstract(contents_path: Path) -> str:
    """Extract abstract from manuscript contents."""
    abstract_file = contents_path / "abstract.tex"
    if abstract_file.exists():
        content = _read_tex_content(abstract_file)
        # Remove \begin{abstract}...\end{abstract} wrapper if present
        match = re.search(
            r"\\begin\{abstract\}(.+?)\\end\{abstract\}",
            content,
            re.DOTALL,
        )
        if match:
            content = match.group(1).strip()
        # Clean LaTeX commands
        return _clean_latex(content)
    return ""


def _extract_keywords(shared_path: Path) -> list[str]:
    """Extract keywords from shared metadata."""
    keywords_file = shared_path / "keywords.tex"
    if keywords_file.exists():
        content = _read_tex_content(keywords_file)
        # Remove \begin{keyword}...\end{keyword} wrapper
        match = re.search(
            r"\\begin\{keyword\}(.+?)\\end\{keyword\}",
            content,
            re.DOTALL,
        )
        if match:
            content = match.group(1)
        # Replace \sep with comma for splitting
        content = re.sub(r"\\sep", ",", content)
        # Parse keywords (comma-separated)
        keywords = [kw.strip() for kw in content.split(",") if kw.strip()]
        return keywords
    return []


def _extract_authors(shared_path: Path) -> list[str]:
    """Extract author names from shared metadata."""
    authors_file = shared_path / "authors.tex"
    if authors_file.exists():
        content = _read_tex_content(authors_file)
        # Try to extract author names from \author{} commands
        matches = re.findall(r"\\author\{(.+?)\}", content, re.DOTALL)
        if matches:
            return [m.strip() for m in matches]
        # Fallback: split by common separators
        authors = re.split(r"[,;&]|\\and", content)
        return [a.strip() for a in authors if a.strip()]
    return []


def resolve_tags(
    template: str,
    tags: dict[str, str],
) -> str:
    """Resolve tags in a template string.

    Args:
        template: Template string with {tag} placeholders.
        tags: Dictionary of tag -> value mappings.

    Returns:
        Template with all tags replaced by their values.
    """
    result = template
    for tag, value in tags.items():
        result = result.replace(f"{{{tag}}}", value)
    return result


def get_template(search_type: str) -> str:
    """Get the Asta prompt template for a search type.

    Args:
        search_type: One of "related" or "coauthors".

    Returns:
        The template content with {tag} placeholders.

    Raises:
        ValueError: If search_type is invalid.
        FileNotFoundError: If template file not found.
    """
    if search_type not in ("related", "coauthors"):
        raise ValueError(
            f"Invalid search_type: '{search_type}'. Use 'related' or 'coauthors'."
        )

    template_path = _get_template_path(search_type)

    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    return template_path.read_text(encoding="utf-8")


def build_prompt(
    template: str,
    title: str = "",
    abstract: str = "",
    keywords: list[str] | None = None,
    authors: list[str] | None = None,
) -> str:
    """Build final prompt from template and tag values.

    Args:
        template: Template string with {tag} placeholders.
        title: Manuscript title.
        abstract: Manuscript abstract.
        keywords: List of keywords.
        authors: List of author names.

    Returns:
        Final prompt with all tags resolved.
    """
    tags = {
        "title": title or "(No title provided)",
        "abstract": abstract or "(No abstract provided)",
        "keywords": ", ".join(keywords) if keywords else "(No keywords)",
        "authors": ", ".join(authors) if authors else "(No authors listed)",
    }
    return resolve_tags(template, tags)


def generate_ai2_prompt(
    project_path: Path,
    search_type: str = "related",
) -> AI2PromptResult:
    """Generate AI2 Asta prompt from manuscript files.

    This creates a prompt suitable for Semantic Scholar's Asta AI
    to find related papers or potential collaborators.

    Args:
        project_path: Path to scitex/writer project directory.
                      Should contain 00_shared/ and 01_manuscript/contents/.
        search_type: Type of search. One of:
                     - "related": Find related papers
                     - "coauthors": Find potential collaborators

    Returns:
        Dictionary with:
        - success: Whether generation succeeded
        - prompt: The generated prompt for AI2 Asta
        - search_type: The search type used
        - next_steps: List of suggested next steps
        - error: Error message if failed, None otherwise

    Environment Variables:
        SCITEX_WRITER_PROMPT_ASTA_RELATED: Custom template for related papers
        SCITEX_WRITER_PROMPT_ASTA_COAUTHORS: Custom template for collaborators
    """
    project_path = Path(project_path)

    # Validate search_type and get template
    try:
        template = get_template(search_type)
    except ValueError as e:
        return AI2PromptResult(
            success=False,
            prompt="",
            search_type=search_type,
            next_steps=[],
            error=str(e),
        )
    except FileNotFoundError as e:
        return AI2PromptResult(
            success=False,
            prompt="",
            search_type=search_type,
            next_steps=[],
            error=str(e),
        )

    # Locate directories
    shared_path = project_path / "00_shared"
    contents_path = project_path / "01_manuscript" / "contents"

    if not shared_path.exists():
        return AI2PromptResult(
            success=False,
            prompt="",
            search_type=search_type,
            next_steps=[],
            error=f"Shared directory not found: {shared_path}",
        )

    # Extract manuscript components
    title = _extract_title(shared_path)
    abstract = _extract_abstract(contents_path)
    keywords = _extract_keywords(shared_path)
    authors = _extract_authors(shared_path)

    # Check we have minimum content
    if not title and not abstract:
        return AI2PromptResult(
            success=False,
            prompt="",
            search_type=search_type,
            next_steps=[
                "Add title to 00_shared/title.tex",
                "Add abstract to 01_manuscript/contents/abstract.tex",
            ],
            error="No title or abstract found. Cannot generate prompt.",
        )

    # Build the final prompt
    prompt = build_prompt(
        template=template,
        title=title,
        abstract=abstract,
        keywords=keywords,
        authors=authors,
    )

    # Define next steps based on search type
    if search_type == "related":
        next_steps = [
            "Go to https://www.semanticscholar.org/product/semantic-reader",
            "Paste the generated prompt",
            "Review and save relevant papers to your library",
        ]
    else:  # coauthors
        next_steps = [
            "Go to https://www.semanticscholar.org/product/semantic-reader",
            "Paste the generated prompt",
            "Review suggested researchers and their work",
            "Consider reaching out for collaboration",
        ]

    return AI2PromptResult(
        success=True,
        prompt=prompt,
        search_type=search_type,
        next_steps=next_steps,
        error=None,
    )


# EOF
