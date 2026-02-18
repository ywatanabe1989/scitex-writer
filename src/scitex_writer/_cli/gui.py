#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/gui.py

"""GUI editor CLI command."""

import argparse
import sys
from pathlib import Path


def cmd_gui(args: argparse.Namespace) -> int:
    """Launch the GUI editor."""
    project = Path(args.project).resolve()
    if not project.exists():
        print(f"Error: Project not found: {project}", file=sys.stderr)
        return 1

    try:
        from .._editor import gui

        gui(
            project_dir=str(project),
            port=args.port,
            host=args.host,
            open_browser=not args.no_browser,
            desktop=args.desktop,
        )
    except ImportError as e:
        print(
            f"Error: {e}\nInstall with: pip install scitex-writer[editor]",
            file=sys.stderr,
        )
        return 1

    return 0


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register gui subcommand parser."""
    parser = subparsers.add_parser(
        "gui",
        help="Launch browser-based editor",
        description=(
            "Launch a standalone GUI editor with file tree, "
            "LaTeX editor, PDF preview, and compilation controls."
        ),
    )
    parser.add_argument(
        "project",
        nargs="?",
        default=".",
        help="Project directory (default: current directory)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=5050,
        help="Server port (default: 5050)",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open browser automatically",
    )
    parser.add_argument(
        "--desktop",
        action="store_true",
        help="Launch as desktop window (requires pywebview)",
    )
    parser.set_defaults(func=cmd_gui)

    return parser


# EOF
