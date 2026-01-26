#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_cli/tables.py

"""Tables CLI commands."""

import argparse
import sys
from pathlib import Path


def cmd_list(args: argparse.Namespace) -> int:
    """List tables in project."""
    from .. import tables

    result = tables.list(args.project, args.doc_type)
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"# Tables ({result['count']})\n")
    print("| Name | CSV | Caption |")
    print("|------|-----|---------|")
    for t in result["tables"]:
        has_cap = "✓" if t["has_caption"] else ""
        print(f"| {t['name']} | ✓ | {has_cap} |")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Add a table to the project."""
    from .. import tables

    if args.csv == "-":
        csv_content = sys.stdin.read()
    else:
        csv_path = Path(args.csv)
        if csv_path.exists():
            csv_content = csv_path.read_text(encoding="utf-8")
        else:
            csv_content = args.csv

    result = tables.add(
        args.project,
        args.name,
        csv_content,
        args.caption,
        args.label,
        args.doc_type,
    )

    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"Added table: {args.name}")
    print(f"  CSV: {result['csv_path']}")
    print(f"  Caption: {result['caption_path']}")
    print(f"  Label: {result['label']}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    """Remove a table from the project."""
    from .. import tables

    result = tables.remove(args.project, args.name, args.doc_type)
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"Removed: {', '.join(result['removed'])}")
    return 0


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register tables subcommand parser."""
    tables_help = """Table management.

Quick start:
  scitex-writer tables list                  # List tables
  scitex-writer tables add results data.csv "Results summary"
  scitex-writer tables remove results
"""
    parser = subparsers.add_parser(
        "tables",
        help="Table management",
        description=tables_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="tables_command", title="Commands")

    # list
    lst = sub.add_parser("list", help="List tables")
    lst.add_argument("-p", "--project", default=".", help="Project path")
    lst.add_argument(
        "-t",
        "--doc-type",
        default="manuscript",
        choices=["manuscript", "supplementary", "revision"],
    )
    lst.set_defaults(func=cmd_list)

    # add
    a = sub.add_parser("add", help="Add a table")
    a.add_argument("name", help="Table name")
    a.add_argument("csv", help="CSV content, file path, or '-' for stdin")
    a.add_argument("caption", help="Table caption")
    a.add_argument("-l", "--label", help="LaTeX label (default: tab:<name>)")
    a.add_argument("-p", "--project", default=".", help="Project path")
    a.add_argument(
        "-t",
        "--doc-type",
        default="manuscript",
        choices=["manuscript", "supplementary"],
    )
    a.set_defaults(func=cmd_add)

    # remove
    r = sub.add_parser("remove", help="Remove a table")
    r.add_argument("name", help="Table name")
    r.add_argument("-p", "--project", default=".", help="Project path")
    r.add_argument(
        "-t",
        "--doc-type",
        default="manuscript",
        choices=["manuscript", "supplementary"],
    )
    r.set_defaults(func=cmd_remove)

    return parser


# EOF
