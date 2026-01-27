#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_cli/guidelines.py

"""Guidelines CLI commands."""

import argparse
import sys
from pathlib import Path


def cmd_guidelines(args: argparse.Namespace) -> int:
    """Get IMRAD writing guidelines for a section."""
    from ..guidelines import build, get, get_source

    try:
        source = get_source(args.section)

        if args.info:
            print(f"Section: {args.section}")
            print(f"Source: {source['source']}")
            print(f"Path: {source['path']}\n")

        if args.draft:
            if args.draft == "-":
                draft = sys.stdin.read()
            else:
                draft_path = Path(args.draft)
                if not draft_path.exists():
                    print(f"Error: Draft file not found: {draft_path}", file=sys.stderr)
                    return 1
                draft = draft_path.read_text(encoding="utf-8")

            prompt = build(args.section, draft)
            print(prompt)
        else:
            guidelines = get(args.section)
            print(guidelines)

        return 0
    except (ValueError, FileNotFoundError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    """List available guidelines sections."""
    from ..guidelines import SECTIONS

    print("Available sections:")
    for section in SECTIONS:
        print(f"  - {section}")
    return 0


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register guidelines subcommand parser."""
    guidelines_help = """IMRAD writing guidelines for scientific manuscripts.

Quick start:
  scitex-writer guidelines list              # List available sections
  scitex-writer guidelines abstract          # Get abstract guidelines
  scitex-writer guidelines abstract -d draft.tex  # Build with draft
"""
    parser = subparsers.add_parser(
        "guidelines",
        help="IMRAD writing guidelines",
        description=guidelines_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="guidelines_command", title="Commands")

    lst = sub.add_parser("list", help="List available sections")
    lst.set_defaults(func=cmd_list)

    for section in ["abstract", "introduction", "methods", "discussion", "proofread"]:
        sp = sub.add_parser(section, help=f"Get {section} guidelines")
        sp.add_argument("-d", "--draft", help="Path to draft file (use '-' for stdin)")
        sp.add_argument("-i", "--info", action="store_true", help="Show source info")
        sp.set_defaults(func=cmd_guidelines, section=section)

    return parser


# EOF
