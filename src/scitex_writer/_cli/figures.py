#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_cli/figures.py

"""Figures CLI commands."""

import argparse
import sys
from pathlib import Path


def cmd_list(args: argparse.Namespace) -> int:
    """List figures in project."""
    from .. import figures

    result = figures.list(
        args.project, args.extensions.split(",") if args.extensions else None
    )
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"# Figures ({result['count']})\n")
    if result["figures"]:
        print("| Name | Format | Caption |")
        print("|------|--------|---------|")
        for f in result["figures"]:
            fmt = Path(f["path"]).suffix
            has_cap = "✓" if f.get("has_caption") else ""
            print(f"| {f['name']} | {fmt} | {has_cap} |")
    return 0


def cmd_add(args: argparse.Namespace) -> int:
    """Add a figure to the project."""
    from .. import figures

    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image not found: {image_path}", file=sys.stderr)
        return 1

    result = figures.add(
        args.project,
        args.name,
        str(image_path),
        args.caption,
        args.label,
        args.doc_type,
    )

    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"Added figure: {args.name}")
    print(f"  Image: {result['image_path']}")
    print(f"  Caption: {result['caption_path']}")
    print(f"  Label: {result['label']}")
    return 0


def cmd_remove(args: argparse.Namespace) -> int:
    """Remove a figure from the project."""
    from .. import figures

    result = figures.remove(args.project, args.name, args.doc_type)
    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"Removed: {', '.join(result['removed'])}")
    return 0


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register figures subcommand parser."""
    figures_help = """Figure management.

Quick start:
  scitex-writer figures list                 # List figures
  scitex-writer figures add fig01 plot.png "Results plot"
  scitex-writer figures remove fig01
"""
    parser = subparsers.add_parser(
        "figures",
        help="Figure management",
        description=figures_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="figures_command", title="Commands")

    # list
    lst = sub.add_parser("list", help="List figures")
    lst.add_argument("-p", "--project", default=".", help="Project path")
    lst.add_argument(
        "-e", "--extensions", help="Extensions to filter (comma-separated)"
    )
    lst.set_defaults(func=cmd_list)

    # add
    a = sub.add_parser("add", help="Add a figure")
    a.add_argument("name", help="Figure name")
    a.add_argument("image", help="Image file path")
    a.add_argument("caption", help="Figure caption")
    a.add_argument("-l", "--label", help="LaTeX label (default: fig:<name>)")
    a.add_argument("-p", "--project", default=".", help="Project path")
    a.add_argument(
        "-t",
        "--doc-type",
        default="manuscript",
        choices=["manuscript", "supplementary"],
    )
    a.set_defaults(func=cmd_add)

    # remove
    r = sub.add_parser("remove", help="Remove a figure")
    r.add_argument("name", help="Figure name")
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
