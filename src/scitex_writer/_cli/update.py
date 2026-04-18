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

    # Header
    mode = " (dry run)" if args.dry_run else ""
    version = result.get("version", "unknown")
    print(f"\nSciTeX Writer Update{mode}")
    print(f"Package version: {version}")
    print(f"Project: {project}\n")

    # File listing with M/A/= markers
    modified = result.get("modified", [])
    added = result.get("added", [])
    unchanged = result.get("unchanged", [])

    if modified or added or unchanged:
        print("Files to update:" if args.dry_run else "Files updated:")
        for p in modified:
            print(f"  M {p} (modified)")
        for p in added:
            print(f"  A {p} (new)")
        for p in unchanged:
            print(f"  = {p} (unchanged)")
        print()

    print(f"  {len(modified)} modified, {len(added)} new, {len(unchanged)} unchanged")

    # Backup info
    backup_dir = result.get("backup_dir")
    if backup_dir:
        print(f"\n  Backup: {backup_dir}")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes.")
    elif modified or added:
        print(f"\nReview changes: git -C {project} diff")

    return 0


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register update subcommand."""
    parser = subparsers.add_parser(
        "update",
        help="Update engine files of a scitex-writer project",
        description=(
            "Update source code, build scripts, and templates to the latest "
            "version while preserving all user content (manuscript text, "
            "bibliography, figures, tables, and metadata)."
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
