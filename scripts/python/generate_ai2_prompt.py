#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-12 12:57:38 (ywatanabe)"


"""
Generate AI2 Asta prompt from manuscript files for finding related papers

Functionalities:
  - Extracts title, keywords, authors, and abstract from manuscript .tex files
  - Generates formatted prompt for AI2 Asta
  - Can save to file or print to stdout
  - Supports both co-author paper search and general related paper search
  - Flexible section inclusion/exclusion
  - Optional bibliography statistics
  - Multiple output formats

Dependencies:
  - packages:
    - pathlib
    - re
    - argparse
    - yaml

IO:
  - input-files:
    - 00_shared/title.tex
    - 00_shared/keywords.tex
    - 00_shared/authors.tex
    - 01_manuscript/contents/abstract.tex
    - 00_shared/**/*.bib (optional, for stats)

  - output-files:
    - Prompt text to stdout or file
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml
from _logging import getLogger

HEADER = """# Literature Search Request
We are preparing a manuscript with the information provided below.

1. Please identify related papers that may be relevant to our work.
2. Comprehensive results are welcome, as we will evaluate all suggestions for relevance.
3. Your contribution to advancing scientific research is greatly appreciated.
4. If possible, please output as a BibTeX file (.bib).
"""


def load_config(config_path: Path = None) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to config file. If None, uses default location.

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Default to ../config/config_manuscript.yaml relative to script location
        script_dir = Path(__file__).resolve().parent
        config_path = script_dir.parent.parent / "config" / "config_manuscript.yaml"

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config


def read_tex_content(tex_path: Path) -> str:
    """Read raw content from .tex file, removing comments.

    Args:
        tex_path: Path to .tex file

    Returns:
        Raw tex content without comments (empty string if file doesn't exist)
    """
    if not tex_path.exists():
        return ""

    content = tex_path.read_text(encoding="utf-8")

    # Remove comment lines (lines starting with %)
    lines = content.split("\n")
    lines = [line for line in lines if not line.strip().startswith("%")]

    return "\n".join(lines).strip()


def clean_latex_content(content: str) -> str:
    """Clean LaTeX commands from content, keeping only the text.

    Args:
        content: Raw LaTeX content

    Returns:
        Cleaned text content
    """
    import re

    # Remove PDF bookmarks first
    content = re.sub(r"\\pdfbookmark\[[^\]]*\]\{[^}]*\}\{[^}]*\}", "", content)

    # Remove correlation references
    content = re.sub(r"\\corref\{[^}]*\}", "", content)

    # Remove author numbering like \author[1]{Name}
    content = re.sub(r"\\author\[[^\]]*\]\{([^}]*)\}", r"\1", content)

    # Remove addresses
    content = re.sub(r"\\address\[[^\]]*\]\{[^}]*\}", "", content)

    # Remove cortext
    content = re.sub(r"\\cortext\[[^\]]*\]\{[^}]*\}", "", content)

    # Remove environment markers
    content = re.sub(r"\\begin\{[^}]+\}", "", content)
    content = re.sub(r"\\end\{[^}]+\}", "", content)

    # Remove standalone commands with optional arguments
    content = re.sub(r"\\[a-zA-Z]+\[[^\]]*\]", "", content)

    # Remove common LaTeX commands but keep their content (iteratively)
    # \command{content} -> content
    for _ in range(3):  # Multiple passes for nested commands
        content = re.sub(r"\\[a-zA-Z]+\{([^{}]*)\}", r"\1", content)

    # Remove any remaining backslash commands
    content = re.sub(r"\\[a-zA-Z]+", "", content)

    # Remove special characters
    content = re.sub(r"\\&", "&", content)
    content = re.sub(r"\\_", "_", content)
    content = re.sub(r"\{", "", content)
    content = re.sub(r"\}", "", content)

    # Clean up keyword separators
    content = re.sub(r"\\sep", ", ", content)

    # Clean up multiple spaces and newlines
    content = re.sub(r"\n\s*\n\s*\n+", "\n\n", content)
    content = re.sub(r" +", " ", content)
    content = re.sub(r"^\s+", "", content, flags=re.MULTILINE)

    return content.strip()


def extract_bib_keys(bib_path: Path) -> Set[str]:
    """Extract all citation keys from a .bib file.

    Args:
        bib_path: Path to .bib file

    Returns:
        Set of citation keys found in the file
    """
    if not bib_path.exists():
        return set()

    content = bib_path.read_text(encoding="utf-8")

    # Match @article{key, @book{key, etc.
    pattern = r"@\w+\s*\{\s*([^,\s]+)"
    keys = re.findall(pattern, content)

    return set(keys)


def get_bibliography_stats(bib_dir: Path) -> Dict[str, int]:
    """Get statistics about bibliography files.

    Args:
        bib_dir: Path to bibliography directory

    Returns:
        Dictionary with bibliography statistics
    """
    bib_files = list(bib_dir.rglob("*.bib"))
    all_keys = set()

    for bib_file in bib_files:
        keys = extract_bib_keys(bib_file)
        all_keys.update(keys)

    return {
        "total_references": len(all_keys),
        "total_files": len(bib_files),
    }


def add_title(parts: List[str], title: str) -> None:
    """Add title section to prompt parts.

    Args:
        parts: List to append prompt parts to
        title: Title content (LaTeX will be cleaned)
    """
    title_clean = clean_latex_content(title) if title else ""
    if title_clean:
        parts.append(f"## Title\n{title_clean}")
        parts.append("")


def add_keywords(parts: List[str], keywords: str) -> None:
    """Add keywords section to prompt parts.

    Args:
        parts: List to append prompt parts to
        keywords: Keywords content (LaTeX will be cleaned)
    """
    keywords_clean = clean_latex_content(keywords) if keywords else ""
    if keywords_clean:
        parts.append(f"## Keywords\n{keywords_clean}")
        parts.append("")


def add_authors(parts: List[str], authors: str) -> None:
    """Add authors section to prompt parts.

    Args:
        parts: List to append prompt parts to
        authors: Authors content (LaTeX will be cleaned)
    """
    authors_clean = clean_latex_content(authors) if authors else ""
    if authors_clean:
        parts.append(f"## Authors\n{authors_clean}")
        parts.append("")


def add_abstract(parts: List[str], abstract: str) -> None:
    """Add abstract section to prompt parts.

    Args:
        parts: List to append prompt parts to
        abstract: Abstract content (LaTeX will be cleaned)
    """
    abstract_clean = clean_latex_content(abstract) if abstract else ""
    if abstract_clean:
        parts.append(f"## Abstract\n{abstract_clean}")


def add_citation_info(
    parts: List[str],
    citation_data: Dict[str, Any],
    bib_filters: Dict[str, bool],
) -> None:
    """Add citation information sections to prompt parts.

    Args:
        parts: List to append prompt parts to
        citation_data: Citation data from check_cited_states.py
        bib_filters: Dictionary indicating which citation lists to include
    """
    if not citation_data or not any(bib_filters.values()):
        return

    parts.append("")
    parts.append("---")
    parts.append("")

    details = citation_data.get("details", {})

    # Add cited references
    if bib_filters.get("cited", False):
        cited_refs = details.get("successfully_cited", [])
        if cited_refs:
            parts.append(f"### Already Cited References ({len(cited_refs)})")
            for ref in cited_refs:
                parts.append(f"- `{ref}`")
            parts.append("")

    # Add uncited references
    if bib_filters.get("uncited", False):
        uncited_refs = details.get("uncited_references", [])
        if uncited_refs:
            parts.append(
                f"### Uncited References in Our Bibliography ({len(uncited_refs)})"
            )
            parts.append("*These might be relevant to cite*")
            for ref in uncited_refs:
                parts.append(f"- `{ref}`")
            parts.append("")

    # Add missing references
    if bib_filters.get("missing", False):
        missing_refs = details.get("missing_references", [])
        if missing_refs:
            parts.append(f"### Missing References ({len(missing_refs)})")
            parts.append("*Cited but not in our bibliography - need to find*")
            for ref in missing_refs:
                parts.append(f"- `{ref}`")
            parts.append("")


def generate_ai2_prompt(
    title: str,
    keywords: str,
    authors: str,
    abstract: str,
    sections: List[str] = None,
    citation_data: Dict[str, Any] = None,
    bib_filters: Dict[str, bool] = None,
) -> str:
    """Generate AI2 Asta prompt in markdown format.

    Args:
        title: Paper title
        keywords: Keywords
        authors: Author names
        abstract: Abstract text
        sections: List of sections to include (default: all)
        citation_data: Citation data from check_cited_states.py (optional)
        bib_filters: Dictionary indicating which citation lists to include

    Returns:
        Formatted prompt for AI2 Asta in markdown
    """
    if sections is None:
        sections = ["title", "keywords", "authors", "abstract"]

    if bib_filters is None:
        bib_filters = {}

    # Build the prompt header
    header = HEADER
    parts = [header, ""]

    # Add requested sections
    if "title" in sections:
        add_title(parts, title)
    if "keywords" in sections:
        add_keywords(parts, keywords)
    if "authors" in sections:
        add_authors(parts, authors)
    if "abstract" in sections:
        add_abstract(parts, abstract)

    # Add citation information
    add_citation_info(parts, citation_data, bib_filters)

    return "\n".join(parts).strip()


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI2 Asta prompt from manuscript files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate prompt for related papers (default: all sections, markdown format)
  %(prog)s

  # Only title and abstract
  %(prog)s --title --abstract

  # Everything except authors (for blind review)
  %(prog)s --title --keywords --abstract

  # Include uncited refs to get suggestions for citing them (recommended!)
  %(prog)s --bib-uncited

  # Include all citation info
  %(prog)s --bib-cited --bib-uncited --bib-missing

  # Save to custom file
  %(prog)s --output ai2_prompt.txt

  # Verbose output
  %(prog)s --verbose
        """,
    )

    # Section selection (if none specified, include all)
    parser.add_argument(
        "--title",
        action="store_true",
        help="Include title section",
    )
    parser.add_argument(
        "--keywords",
        action="store_true",
        help="Include keywords section",
    )
    parser.add_argument(
        "--authors",
        action="store_true",
        help="Include authors section",
    )
    parser.add_argument(
        "--abstract",
        action="store_true",
        help="Include abstract section",
    )

    # Bibliography options
    parser.add_argument(
        "--bib-cited",
        action="store_true",
        help="Include list of successfully cited references in the prompt",
    )
    parser.add_argument(
        "--bib-uncited",
        action="store_true",
        help="Include list of uncited references in the prompt",
    )
    parser.add_argument(
        "--bib-missing",
        action="store_true",
        help="Include list of missing references in the prompt",
    )

    # Other options
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to config YAML file (default: auto-detect from script location)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file path (default: print to stdout)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Setup logger
    logger = getLogger(__name__, args.verbose)

    # Determine which sections to include
    # If any section flag is specified, include only those
    # Otherwise, include all sections
    section_flags = {
        "title": args.title,
        "keywords": args.keywords,
        "authors": args.authors,
        "abstract": args.abstract,
    }

    if any(section_flags.values()):
        sections = [name for name, enabled in section_flags.items() if enabled]
    else:
        sections = ["title", "keywords", "authors", "abstract"]

    # Load configuration
    load_config(args.config)

    # Get project root (where the config file is located)
    if args.config:
        project_root = args.config.parent.parent
    else:
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent.parent

    # Extract information from manuscript files
    # Use paths relative to project root
    title_path = project_root / "00_shared" / "title.tex"
    keywords_path = project_root / "00_shared" / "keywords.tex"
    authors_path = project_root / "00_shared" / "authors.tex"
    abstract_path = project_root / "01_manuscript" / "contents" / "abstract.tex"

    logger.info("Reading manuscript files...")

    title = read_tex_content(title_path)
    keywords = read_tex_content(keywords_path)
    authors = read_tex_content(authors_path)
    abstract = read_tex_content(abstract_path)

    # Validate required content
    if not title and "title" in sections:
        logger.warning("No title found in 00_shared/title.tex")
    if not abstract and "abstract" in sections:
        logger.warning("No abstract found in 01_manuscript/contents/abstract.tex")

    # Load citation data if any bib options are specified
    citation_data = None
    if args.bib_cited or args.bib_uncited or args.bib_missing:
        citation_json_path = (
            project_root / "00_shared" / "bib_files" / "cited_states.json"
        )
        if citation_json_path.exists():
            try:
                citation_data = json.loads(
                    citation_json_path.read_text(encoding="utf-8")
                )
                logger.info(f"Loaded citation data from {citation_json_path.name}")
            except Exception as e:
                logger.warning(f"Could not load citation data: {e}")
        else:
            logger.warning("Citation data not found. Run check_cited_states.py first.")
            logger.warning(f"Expected: {citation_json_path}")

    # Determine which citation filters are active
    bib_filters = {
        "cited": args.bib_cited,
        "uncited": args.bib_uncited,
        "missing": args.bib_missing,
    }

    # Generate prompt in markdown format
    prompt = generate_ai2_prompt(
        title,
        keywords,
        authors,
        abstract,
        sections,
        citation_data,
        bib_filters,
    )

    # Create structured data for JSON output
    data = {
        "metadata": {
            "title": title,
            "keywords": keywords,
            "authors": authors,
            "abstract": abstract,
        },
        "prompt": prompt,
        "sections_included": sections,
        "citation_filters": bib_filters if any(bib_filters.values()) else None,
        "citation_data": (citation_data.get("summary") if citation_data else None),
    }

    # Always save to default locations unless custom output specified
    default_json_path = project_root / "00_shared" / "ai2_prompt_data.json"
    default_md_path = project_root / "00_shared" / "ai2_prompt.md"
    default_json_path.parent.mkdir(parents=True, exist_ok=True)

    # Save JSON and markdown to default locations (always)
    if not args.output:
        # Save JSON data
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        default_json_path.write_text(json_str, encoding="utf-8")

        # Save markdown prompt
        default_md_path.write_text(prompt, encoding="utf-8")

    # Output
    if args.output:
        args.output.write_text(prompt, encoding="utf-8")
        logger.success(f"Saved to: {args.output}")
        logger.info("\nNext steps:")
        logger.info("1. Visit https://asta.allen.ai/chat/")
        logger.info(f"2. Paste the prompt from {args.output}")
        logger.info("3. Click 'Export All Citations' to download BibTeX file")
    else:
        print("\n" + "=" * 80)
        print("AI2 ASTA PROMPT")
        print("=" * 80)
        print()
        print(prompt)
        print()
        print("=" * 80)
        logger.info("\nNext steps:")
        logger.info("1. Visit https://asta.allen.ai/chat/")
        logger.info("2. Copy and paste the prompt above")
        logger.info("3. Click 'Export All Citations' to download BibTeX file")
        logger.success(f"Saved to: {default_md_path}")
        logger.success(f"Saved to: {default_json_path}")


if __name__ == "__main__":
    main()

# EOF
