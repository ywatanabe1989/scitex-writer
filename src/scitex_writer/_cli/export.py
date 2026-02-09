#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/export.py

"""Export CLI commands."""

import argparse
import sys
from pathlib import Path


def cmd_manuscript(args: argparse.Namespace) -> int:
    """Export manuscript as arXiv-ready tarball."""
    from .. import export

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"Error: Project not found: {project}", file=sys.stderr)
        return 1

    result = export.manuscript(
        str(project),
        output_dir=args.output_dir,
        format=args.format,
    )

    if result["success"]:
        print(f"Tarball: {result['tarball_path']}")
        return 0
    else:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register export subcommands."""
    export_parser = subparsers.add_parser(
        "export",
        help="Export manuscript for submission",
    )
    export_subs = export_parser.add_subparsers(dest="export_command")

    # export manuscript
    ms_parser = export_subs.add_parser(
        "manuscript",
        help="Export manuscript as arXiv-ready tarball",
    )
    ms_parser.add_argument(
        "project",
        nargs="?",
        default=".",
        help="Project directory (default: current directory)",
    )
    ms_parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: 01_manuscript/export/)",
    )
    ms_parser.add_argument(
        "--format",
        default="arxiv",
        choices=["arxiv"],
        help="Export format (default: arxiv)",
    )
    ms_parser.set_defaults(func=cmd_manuscript)

    return export_parser


# EOF
