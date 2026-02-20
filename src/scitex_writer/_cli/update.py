#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/update.py

"""CLI: update engine files in a scitex-writer project."""

import argparse
import sys
from pathlib import Path


def cmd_update(args: argparse.Namespace) -> int:
    """Update engine files while preserving user content."""
    from .. import update

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"Error: Project not found: {project}", file=sys.stderr)
        return 1

    result = update.project(
        str(project),
        branch=args.branch,
        tag=args.tag,
        dry_run=args.dry_run,
        force=args.force,
    )

    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    # Warnings (e.g. not a git repo)
    for w in result.get("warnings", []):
        print(f"Warning: {w}", file=sys.stderr)

    # Report
    if args.dry_run:
        print("Dry run — no files modified.\n")

    if result["updated_paths"]:
        verb = "Would update" if args.dry_run else "Updated"
        print(f"{verb}:")
        for p in result["updated_paths"]:
            print(f"  {p}")

    if result.get("missing_paths"):
        print("\nNot found in source (skipped):")
        for p in result["missing_paths"]:
            print(f"  {p}")

    print(f"\n{result['message']}")
    return 0


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register update subcommand."""
    parser = subparsers.add_parser(
        "update",
        help="Update engine files of a scitex-writer project",
        description=(
            "Update build scripts, LaTeX styles, and base templates to the latest "
            "version while preserving all user content (manuscript text, bibliography, "
            "figures, tables, and metadata)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  scitex-writer update                    # update current directory\n"
            "  scitex-writer update ~/proj/my-paper    # update specific project\n"
            "  scitex-writer update --dry-run           # preview changes only\n"
            "  scitex-writer update --tag v2.8.0        # update to specific version\n"
        ),
    )
    parser.add_argument(
        "project",
        nargs="?",
        default=".",
        help="Project directory to update (default: current directory)",
    )
    parser.add_argument(
        "--branch",
        default=None,
        metavar="BRANCH",
        help="Pull from a specific template branch (requires internet)",
    )
    parser.add_argument(
        "--tag",
        default=None,
        metavar="TAG",
        help="Pull from a specific template tag/version (requires internet)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be updated without modifying any files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip git safety check (allow update with uncommitted changes)",
    )
    parser.set_defaults(func=cmd_update)
    return parser


# EOF
