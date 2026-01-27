#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_cli/compile.py

"""Compile CLI commands."""

import argparse
import sys
from pathlib import Path


def cmd_manuscript(args: argparse.Namespace) -> int:
    """Compile manuscript to PDF."""
    from .. import compile

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"Error: Project not found: {project}", file=sys.stderr)
        return 1

    result = compile.manuscript(
        str(project),
        draft=args.draft,
        no_figs=args.no_figs,
        no_tables=args.no_tables,
        no_diff=args.no_diff,
        engine=args.engine,
    )

    if result["success"]:
        print(f"PDF: {result['pdf_path']}")
        return 0
    else:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1


def cmd_supplementary(args: argparse.Namespace) -> int:
    """Compile supplementary materials to PDF."""
    from .. import compile

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"Error: Project not found: {project}", file=sys.stderr)
        return 1

    result = compile.supplementary(
        str(project),
        draft=args.draft,
        engine=args.engine,
    )

    if result["success"]:
        print(f"PDF: {result['pdf_path']}")
        return 0
    else:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1


def cmd_revision(args: argparse.Namespace) -> int:
    """Compile revision letter to PDF."""
    from .. import compile

    project = Path(args.project).resolve()
    if not project.exists():
        print(f"Error: Project not found: {project}", file=sys.stderr)
        return 1

    result = compile.revision(
        str(project),
        track_changes=args.track_changes,
        engine=args.engine,
    )

    if result["success"]:
        print(f"PDF: {result['pdf_path']}")
        return 0
    else:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1


def cmd_content(args: argparse.Namespace) -> int:
    """Compile raw LaTeX content to PDF."""
    from .. import compile

    # Read content from file or stdin
    if args.file:
        content_path = Path(args.file)
        if not content_path.exists():
            print(f"Error: File not found: {content_path}", file=sys.stderr)
            return 1
        latex_content = content_path.read_text(encoding="utf-8")
    else:
        latex_content = sys.stdin.read()

    project_dir = str(Path(args.project).resolve()) if args.project else None

    result = compile.content(
        latex_content,
        project_dir=project_dir,
        color_mode=args.color_mode,
        name=args.name,
        timeout=args.timeout,
        keep_aux=args.keep_aux,
    )

    if result["success"]:
        print(f"PDF: {result['output_pdf']}")
        return 0
    else:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
        if result.get("log"):
            print(f"Log: {result['log'][-500:]}", file=sys.stderr)
        return 1


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register compile subcommand parser."""
    compile_help = """Compile LaTeX documents to PDF.

Quick start:
  scitex-writer compile manuscript           # Compile manuscript
  scitex-writer compile manuscript --draft   # Fast single-pass
  scitex-writer compile supplementary        # Compile supplementary
  scitex-writer compile revision             # Compile revision letter
  scitex-writer compile content -f intro.tex  # Compile content with color modes
  echo '\\section{Test}' | scitex-writer compile content --color-mode dark
"""
    parser = subparsers.add_parser(
        "compile",
        help="Compile LaTeX to PDF",
        description=compile_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="compile_command", title="Commands")

    # manuscript
    ms = sub.add_parser("manuscript", help="Compile manuscript")
    ms.add_argument("-p", "--project", default=".", help="Project path")
    ms.add_argument("--draft", action="store_true", help="Fast single-pass mode")
    ms.add_argument("--no-figs", action="store_true", help="Skip figures")
    ms.add_argument("--no-tables", action="store_true", help="Skip tables")
    ms.add_argument("--no-diff", action="store_true", help="Skip diff generation")
    ms.add_argument(
        "--engine", choices=["tectonic", "latexmk", "3pass"], help="LaTeX engine"
    )
    ms.set_defaults(func=cmd_manuscript)

    # supplementary
    sp = sub.add_parser("supplementary", help="Compile supplementary materials")
    sp.add_argument("-p", "--project", default=".", help="Project path")
    sp.add_argument("--draft", action="store_true", help="Fast single-pass mode")
    sp.add_argument(
        "--engine", choices=["tectonic", "latexmk", "3pass"], help="LaTeX engine"
    )
    sp.set_defaults(func=cmd_supplementary)

    # revision
    rv = sub.add_parser("revision", help="Compile revision letter")
    rv.add_argument("-p", "--project", default=".", help="Project path")
    rv.add_argument(
        "--track-changes", action="store_true", help="Include track changes"
    )
    rv.add_argument(
        "--engine", choices=["tectonic", "latexmk", "3pass"], help="LaTeX engine"
    )
    rv.set_defaults(func=cmd_revision)

    # content
    ct = sub.add_parser("content", help="Compile raw LaTeX content to PDF")
    ct.add_argument("-f", "--file", help="LaTeX file to compile (or use stdin)")
    ct.add_argument("-p", "--project", help="Project path for bibliography access")
    ct.add_argument("-n", "--name", default="content", help="Output name")
    ct.add_argument(
        "-c",
        "--color-mode",
        choices=["light", "dark", "sepia", "paper"],
        default="light",
        help="Color mode (default: light)",
    )
    ct.add_argument("-t", "--timeout", type=int, default=60, help="Timeout in seconds")
    ct.add_argument("--keep-aux", action="store_true", help="Keep auxiliary files")
    ct.set_defaults(func=cmd_content)

    return parser


# EOF
