#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-11 (ywatanabe)"


r"""
Check citation states in manuscript - find uncited and missing references

Functionalities:
  - Extracts citation keys from .bib files
  - Finds all \cite commands in .tex files
  - Reports uncited references (in .bib but not cited)
  - Reports missing references (cited but not in .bib)
  - Reports successfully cited references
  - Supports various citation commands (\cite, \cite, \citet, etc.)
  - JSON output option for programmatic use
  - Proper logging with color-coded output

Dependencies:
  - packages:
    - pathlib
    - re
    - argparse
    - yaml
    - logging
    - json

IO:
  - input-files:
    - All .tex files in manuscript directory
    - All .bib files in bibliography directory

  - output-files:
    - Report to stdout or file (text or JSON format)
"""

import argparse
import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Set

import yaml
from _logging import getLogger


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


def extract_citations_from_tex(tex_path: Path) -> Set[str]:
    r"""Extract all citation keys from \cite commands in a .tex file.

    Args:
        tex_path: Path to .tex file

    Returns:
        Set of citation keys found in cite commands
    """
    if not tex_path.exists() or not tex_path.is_file():
        return set()

    content = tex_path.read_text(encoding="utf-8")

    # Remove comment lines
    lines = content.split("\n")
    lines = [line.split("%")[0] for line in lines]  # Remove inline comments
    content = "\n".join(lines)

    # Match various cite commands: \cite{key}, \cite{key1,key2}, etc.
    # Supports: cite, cite, citet, citealt, citealp, citeauthor, citeyear, etc.
    pattern = r"\\cite\w*\s*(?:\[[^\]]*\])?\s*(?:\[[^\]]*\])?\s*\{([^}]+)\}"
    matches = re.findall(pattern, content)

    # Split multiple citations and clean whitespace
    citations = set()
    for match in matches:
        keys = [k.strip() for k in match.split(",")]
        citations.update(keys)

    return citations


def find_all_tex_files(manuscript_dir: Path) -> List[Path]:
    """Find all .tex files in manuscript directory recursively.

    Args:
        manuscript_dir: Path to manuscript directory

    Returns:
        List of .tex file paths (excludes directories)
    """
    return [f for f in manuscript_dir.rglob("*.tex") if f.is_file()]


def find_all_bib_files(bib_dir: Path) -> List[Path]:
    """Find all .bib files in bibliography directory recursively.

    Args:
        bib_dir: Path to bibliography directory

    Returns:
        List of .bib file paths (excludes directories)
    """
    return [f for f in bib_dir.rglob("*.bib") if f.is_file()]


def generate_citation_data(
    all_bib_keys: Set[str],
    all_citations: Set[str],
    bib_files: List[Path],
    tex_files: List[Path],
) -> Dict[str, Any]:
    """Generate structured citation data.

    Args:
        all_bib_keys: All citation keys found in .bib files
        all_citations: All citations found in .tex files
        bib_files: List of .bib files processed
        tex_files: List of .tex files processed

    Returns:
        Dictionary with citation statistics and details
    """
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


def print_text_report(
    data: Dict[str, Any],
    logger: logging.Logger,
    show_details: bool = True,
    show_sections: Dict[str, bool] = None,
):
    """Print citation report to console using logger.

    Args:
        data: Citation data dictionary
        logger: Logger instance
        show_details: Show detailed lists of citations
        show_sections: Dictionary indicating which sections to show
    """
    if show_sections is None:
        show_sections = {"cited": True, "uncited": True, "missing": True}

    summary = data["summary"]
    details = data["details"]

    print("\n" + "=" * 80)
    print("CITATION STATUS REPORT")
    print("=" * 80 + "\n")

    # Summary (always show)
    print("SUMMARY")
    print("-" * 80)
    logger.info(f"Total references in .bib files: {summary['total_references']}")
    logger.info(f"Total citations in .tex files:  {summary['total_citations']}")
    logger.success(f"Successfully cited:              {summary['successfully_cited']}")

    if summary["uncited"] > 0:
        logger.warning(f"Uncited references:              {summary['uncited']}")
    else:
        logger.info(f"Uncited references:              {summary['uncited']}")

    if summary["missing"] > 0:
        logger.error(f"Missing references:              {summary['missing']}")
    else:
        logger.info(f"Missing references:              {summary['missing']}")

    print()

    if not show_details:
        print("=" * 80 + "\n")
        return

    # Successfully cited
    if show_sections.get("cited", False):
        print("SUCCESSFULLY CITED REFERENCES")
        print("-" * 80)
        if details["successfully_cited"]:
            for key in details["successfully_cited"]:
                logger.success(f"  ✓ {key}")
        else:
            logger.info("  (none)")
        print()

    # Uncited references
    if show_sections.get("uncited", False):
        print("UNCITED REFERENCES (in .bib but not cited in .tex)")
        print("-" * 80)
        if details["uncited_references"]:
            for key in details["uncited_references"]:
                logger.warning(f"  ⚠ {key}")
        else:
            logger.success("  ✓ All references are cited")
        print()

    # Missing references
    if show_sections.get("missing", False):
        print("MISSING REFERENCES (cited in .tex but not in .bib)")
        print("-" * 80)
        if details["missing_references"]:
            for key in details["missing_references"]:
                logger.error(f"  ✗ {key}")
        else:
            logger.success("  ✓ All citations have references")
        print()

    print("=" * 80 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Check citation states in manuscript",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all citation states (default: show all)
  %(prog)s

  # Show only successfully cited references
  %(prog)s --bib-cited

  # Show only uncited references (in .bib but not cited)
  %(prog)s --bib-uncited

  # Show only missing references (cited but not in .bib)
  %(prog)s --bib-missing

  # Show summary only (no detailed lists)
  %(prog)s --summary-only

  # Output as JSON
  %(prog)s --json

  # Save to custom file
  %(prog)s --output citation_report.txt

  # Verbose logging
  %(prog)s --verbose
        """,
    )

    # Filter options (if none specified, show all)
    parser.add_argument(
        "--bib-cited",
        action="store_true",
        help="Show only successfully cited references",
    )
    parser.add_argument(
        "--bib-uncited",
        action="store_true",
        help="Show only uncited references (in .bib but not cited in .tex)",
    )
    parser.add_argument(
        "--bib-missing",
        action="store_true",
        help="Show only missing references (cited in .tex but not in .bib)",
    )

    # Output options
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Show only summary statistics (no detailed lists)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format (default output: 00_shared/bib_files/cited_states.json)",
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
        help="Output file path (default: 00_shared/bib_files/cited_states.json for JSON, stdout for text)",
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

    # Determine what to show based on filter flags
    filter_flags = {
        "cited": args.bib_cited,
        "uncited": args.bib_uncited,
        "missing": args.bib_missing,
    }

    # If any filter is specified, show only those
    # Otherwise, show all
    if any(filter_flags.values()):
        show_sections = {
            name: enabled for name, enabled in filter_flags.items() if enabled
        }
    else:
        show_sections = {"cited": True, "uncited": True, "missing": True}

    # Load configuration
    try:
        load_config(args.config)
    except FileNotFoundError as e:
        logger.error(str(e))
        return 1

    # Get project root
    if args.config:
        project_root = args.config.parent.parent
    else:
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent.parent

    # Find all .bib and .tex files
    bib_dir = project_root / "00_shared"
    manuscript_dir = project_root / "01_manuscript"

    logger.info("Scanning files...")

    bib_files = find_all_bib_files(bib_dir)
    tex_files = find_all_tex_files(manuscript_dir)

    if not bib_files:
        logger.warning(f"No .bib files found in {bib_dir}")
    if not tex_files:
        logger.warning(f"No .tex files found in {manuscript_dir}")

    logger.debug(f"Found {len(bib_files)} .bib files")
    logger.debug(f"Found {len(tex_files)} .tex files")

    # Extract all citation keys from .bib files
    all_bib_keys = set()
    for bib_file in bib_files:
        keys = extract_bib_keys(bib_file)
        all_bib_keys.update(keys)
        logger.debug(f"  {bib_file.name}: {len(keys)} references")

    # Extract all citations from .tex files
    all_citations = set()
    for tex_file in tex_files:
        citations = extract_citations_from_tex(tex_file)
        all_citations.update(citations)
        if citations:
            logger.debug(f"  {tex_file.name}: {len(citations)} citations")

    # Generate citation data
    data = generate_citation_data(all_bib_keys, all_citations, bib_files, tex_files)

    # Always save JSON to default location unless custom output specified
    default_json_path = project_root / "00_shared" / "bib_files" / "cited_states.json"
    default_json_path.parent.mkdir(parents=True, exist_ok=True)

    # Save JSON data to default location (always)
    if not args.output:
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        default_json_path.write_text(json_str, encoding="utf-8")

    # Output
    if args.json:
        # JSON output to stdout or custom file
        if args.output:
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            args.output.write_text(json_str, encoding="utf-8")
            logger.success(f"Saved to: {args.output}")
        else:
            # Already saved to default location, just print
            print(json.dumps(data, indent=2, ensure_ascii=False))
            logger.success(f"Saved to: {default_json_path}")
    else:
        # Text output
        if args.output:
            # For text file output, generate plain text without colors
            with open(args.output, "w", encoding="utf-8") as f:
                f.write("=" * 80 + "\n")
                f.write("CITATION STATUS REPORT\n")
                f.write("=" * 80 + "\n\n")
                f.write("SUMMARY\n")
                f.write("-" * 80 + "\n")
                f.write(
                    f"Total references in .bib files: {data['summary']['total_references']}\n"
                )
                f.write(
                    f"Total citations in .tex files:  {data['summary']['total_citations']}\n"
                )
                f.write(
                    f"Successfully cited:              {data['summary']['successfully_cited']}\n"
                )
                f.write(
                    f"Uncited references:              {data['summary']['uncited']}\n"
                )
                f.write(
                    f"Missing references:              {data['summary']['missing']}\n\n"
                )

                if not args.summary_only:
                    f.write("SUCCESSFULLY CITED REFERENCES\n")
                    f.write("-" * 80 + "\n")
                    for key in data["details"]["successfully_cited"]:
                        f.write(f"  ✓ {key}\n")
                    f.write("\n")

                    f.write("UNCITED REFERENCES (in .bib but not cited in .tex)\n")
                    f.write("-" * 80 + "\n")
                    for key in data["details"]["uncited_references"]:
                        f.write(f"  ⚠ {key}\n")
                    f.write("\n")

                    f.write("MISSING REFERENCES (cited in .tex but not in .bib)\n")
                    f.write("-" * 80 + "\n")
                    for key in data["details"]["missing_references"]:
                        f.write(f"  ✗ {key}\n")
                    f.write("\n")

                f.write("=" * 80 + "\n")

            logger.success(f"Saved to: {args.output}")
        else:
            # Console output with colors (JSON already saved to default location)
            print_text_report(
                data,
                logger,
                show_details=not args.summary_only,
                show_sections=show_sections,
            )
            logger.success(f"Saved to: {default_json_path}")

    # Return exit code based on results
    if data["summary"]["missing"] > 0:
        return 1  # Error: missing references
    return 0


if __name__ == "__main__":
    main()

# EOF
