#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_cli/bib.py

"""Bibliography CLI commands."""

import argparse
import sys
from pathlib import Path


def cmd_list_files(args: argparse.Namespace) -> int:
    """List bibliography files."""
    from .. import bib

    result = bib.list_files(args.project)
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"# Bibliography Files ({result['count']})\n")
    print("| File | Entries | Merged |")
    print("|------|---------|--------|")
    for f in result["bibfiles"]:
        merged = "✓" if f["is_merged"] else ""
        print(f"| {f['name']} | {f['entry_count']} | {merged} |")
    return 0


def cmd_list_entries(args: argparse.Namespace) -> int:
    """List bibliography entries."""
    from .. import bib

    result = bib.list_entries(args.project, args.file)
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"# Bibliography Entries ({result['count']})\n")
    print("| Key | Type | File |")
    print("|-----|------|------|")
    for e in result["entries"]:
        print(f"| {e['citation_key']} | {e['entry_type']} | {e['bibfile']} |")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    """Get a specific bibliography entry."""
    from .. import bib

    result = bib.get(args.project, args.key)
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(result["entry"])
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Add a bibliography entry."""
    from .. import bib

    if args.entry == "-":
        entry = sys.stdin.read()
    elif args.entry.startswith("@"):
        entry = args.entry
    else:
        entry_path = Path(args.entry)
        if entry_path.exists():
            entry = entry_path.read_text(encoding="utf-8")
        else:
            entry = args.entry

    result = bib.add(args.project, entry, args.file, not args.allow_duplicates)
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"Added: {result['citation_key']} to {result['bibfile']}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    """Remove a bibliography entry."""
    from .. import bib

    result = bib.remove(args.project, args.key)
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"Removed: {result['citation_key']} from {result['removed_from']}")
    return 0


def cmd_merge(args: argparse.Namespace) -> int:
    """Merge all bibliography files."""
    from .. import bib

    result = bib.merge(args.project, args.output, not args.keep_duplicates)
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"Merged {result['entry_count']} entries to {result['output_file']}")
    if result["duplicates_skipped"] > 0:
        print(f"Skipped {result['duplicates_skipped']} duplicates")
    return 0


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register bib subcommand parser."""
    bib_help = """Bibliography management.

Quick start:
  scitex-writer bib list-files               # List .bib files
  scitex-writer bib list-entries             # List all entries
  scitex-writer bib get Smith2024            # Get specific entry
  scitex-writer bib add '@article{...}'      # Add entry
  scitex-writer bib remove Smith2024         # Remove entry
  scitex-writer bib merge                    # Merge and deduplicate
"""
    parser = subparsers.add_parser(
        "bib",
        help="Bibliography management",
        description=bib_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="bib_command", title="Commands")

    # list-files
    lf = sub.add_parser("list-files", help="List .bib files")
    lf.add_argument("-p", "--project", default=".", help="Project path")
    lf.set_defaults(func=cmd_list_files)

    # list-entries
    le = sub.add_parser("list-entries", help="List bibliography entries")
    le.add_argument("-p", "--project", default=".", help="Project path")
    le.add_argument("-f", "--file", help="Specific .bib file")
    le.set_defaults(func=cmd_list_entries)

    # get
    g = sub.add_parser("get", help="Get a specific entry")
    g.add_argument("key", help="Citation key")
    g.add_argument("-p", "--project", default=".", help="Project path")
    g.set_defaults(func=cmd_get)

    # add
    a = sub.add_parser("add", help="Add a bibliography entry")
    a.add_argument("entry", help="BibTeX entry, file path, or '-' for stdin")
    a.add_argument("-p", "--project", default=".", help="Project path")
    a.add_argument("-f", "--file", default="custom.bib", help="Target .bib file")
    a.add_argument(
        "--allow-duplicates", action="store_true", help="Allow duplicate keys"
    )
    a.set_defaults(func=cmd_add)

    # remove
    r = sub.add_parser("remove", help="Remove an entry")
    r.add_argument("key", help="Citation key to remove")
    r.add_argument("-p", "--project", default=".", help="Project path")
    r.set_defaults(func=cmd_remove)

    # merge
    m = sub.add_parser("merge", help="Merge all .bib files")
    m.add_argument("-p", "--project", default=".", help="Project path")
    m.add_argument("-o", "--output", default="bibliography.bib", help="Output file")
    m.add_argument(
        "--keep-duplicates", action="store_true", help="Keep duplicate entries"
    )
    m.set_defaults(func=cmd_merge)

    return parser


# EOF
