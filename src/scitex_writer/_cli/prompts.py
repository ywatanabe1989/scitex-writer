#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_cli/prompts.py

"""Prompts CLI commands."""

import argparse
import sys
from pathlib import Path


def cmd_asta(args: argparse.Namespace) -> int:
    """Generate AI2 Asta prompt from manuscript."""
    from ..prompts import generate_ai2_prompt

    project_path = Path(args.project).resolve()

    if not project_path.exists():
        print(f"Error: Project path not found: {project_path}", file=sys.stderr)
        return 1

    result = generate_ai2_prompt(project_path, search_type=args.type)

    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        if result["next_steps"]:
            print("\nSuggested next steps:", file=sys.stderr)
            for step in result["next_steps"]:
                print(f"  - {step}", file=sys.stderr)
        return 1

    if args.info:
        print(f"Search type: {result['search_type']}\n")
        print("Next steps:")
        for step in result["next_steps"]:
            print(f"  - {step}")
        print("\n--- Generated Prompt ---\n")

    print(result["prompt"])
    return 0


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register prompts subcommand parser."""
    prompts_help = """Action prompts for manuscript workflows.

Quick start:
  scitex-writer prompts asta                 # Generate AI2 Asta prompt
  scitex-writer prompts asta -t coauthors    # Find collaborators
"""
    parser = subparsers.add_parser(
        "prompts",
        help="Action prompts (Asta)",
        description=prompts_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="prompts_command", title="Commands")

    asta = sub.add_parser("asta", help="Generate AI2 Asta prompt from manuscript")
    asta.add_argument(
        "-t", "--type", choices=["related", "coauthors"], default="related"
    )
    asta.add_argument("-p", "--project", default=".", help="Project path")
    asta.add_argument("-i", "--info", action="store_true", help="Show search info")
    asta.set_defaults(func=cmd_asta)

    return parser


# EOF
