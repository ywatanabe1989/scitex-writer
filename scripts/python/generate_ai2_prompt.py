#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-30 22:08:55 (ywatanabe)"
# File: /ssh:sp:/home/ywatanabe/proj/neurovista/paper/scripts/python/generate_ai2_prompt.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./scripts/python/generate_ai2_prompt.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Generate AI2 Asta prompt from manuscript files for finding related papers

Functionalities:
  - Extracts title, keywords, authors, and abstract from manuscript .tex files
  - Generates formatted prompt for AI2 Asta
  - Can copy to clipboard or save to file
  - Supports both co-author paper search and general related paper search

Dependencies:
  - packages:
    - pathlib
    - re
    - argparse

IO:
  - input-files:
    - shared/title.tex
    - shared/keywords.tex
    - shared/authors.tex
    - 01_manuscript/contents/abstract.tex

  - output-files:
    - Prompt text to stdout or file
"""

import argparse
from pathlib import Path
from typing import Any, Dict

import yaml


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
        config_path = (
            script_dir.parent.parent / "config" / "config_manuscript.yaml"
        )

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


def generate_ai2_prompt(
    title: str,
    keywords: str,
    authors: str,
    abstract: str,
    search_type: str = "related",
) -> str:
    """Generate AI2 Asta prompt.

    Args:
        title: Paper title
        keywords: Keywords
        authors: Author names
        abstract: Abstract text
        search_type: "related" or "coauthors"

    Returns:
        Formatted prompt for AI2 Asta
    """

    if search_type == "coauthors":
        prompt = f"""We are currently writing a paper manuscript with the information below. Please find (partially) related papers published by at least one of the authors of our manuscript, particularly focusing on their work related to the topics covered in this manuscript.

Title: {title}

Keywords: {keywords}

Authors: {authors}

Abstract: {abstract}"""
    else:  # related
        prompt = f"""We are currently writing a paper manuscript with the information below. Please find related papers.:

Title: {title}

Keywords: {keywords}

Authors: {authors}

Abstract: {abstract}"""

    return prompt


def main():
    parser = argparse.ArgumentParser(
        description="Generate AI2 Asta prompt from manuscript files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate prompt for co-author papers
  %(prog)s --type coauthors

  # Generate prompt for related papers
  %(prog)s --type related

  # Save to file
  %(prog)s --type coauthors --output ai2_prompt.txt

  # Use custom config file
  %(prog)s --config ./config/config_manuscript.yaml
        """,
    )

    parser.add_argument(
        "--type",
        choices=["related", "coauthors"],
        default="coauthors",
        help="Type of search: related papers or co-author papers (default: coauthors)",
    )
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

    args = parser.parse_args()

    # Load configuration
    config = load_config(args.config)

    # Get project root (where the config file is located)
    if args.config:
        project_root = args.config.parent.parent
    else:
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent.parent

    # Extract information from manuscript files
    # Use paths relative to project root
    title_path = project_root / "shared" / "title.tex"
    keywords_path = project_root / "shared" / "keywords.tex"
    authors_path = project_root / "shared" / "authors.tex"
    abstract_path = (
        project_root / "01_manuscript" / "contents" / "abstract.tex"
    )

    print("Reading manuscript files...", flush=True)

    title = read_tex_content(title_path)
    keywords = read_tex_content(keywords_path)
    authors = read_tex_content(authors_path)
    abstract = read_tex_content(abstract_path)

    # Generate prompt
    prompt = generate_ai2_prompt(title, keywords, authors, abstract, args.type)

    # Output
    if args.output:
        args.output.write_text(prompt, encoding="utf-8")
        print(f"\n✓ Prompt saved to: {args.output}")
        print(f"\nNext steps:")
        print(f"1. Visit https://asta.allen.ai/chat/")
        print(f"2. Paste the prompt from {args.output}")
        print(f"3. Click 'Export All Citations' to download BibTeX file")
    else:
        print("\n" + "=" * 80)
        print("AI2 ASTA PROMPT")
        print("=" * 80)
        print()
        print(prompt)
        print()
        print("=" * 80)
        print("\nNext steps:")
        print("1. Visit https://asta.allen.ai/chat/")
        print("2. Copy and paste the prompt above")
        print("3. Click 'Export All Citations' to download BibTeX file")


if __name__ == "__main__":
    main()

# EOF
