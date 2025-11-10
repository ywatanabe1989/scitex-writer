#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line interface for scitex-writer.

Provides CLI commands for manuscript compilation and management.
"""

import argparse
import sys
from pathlib import Path
import subprocess


def main():
    """Main CLI entry point for scitex-writer."""
    from . import __version__

    parser = argparse.ArgumentParser(
        description=f"SciTeX Writer v{__version__} - Scientific Manuscript Writing System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"scitex-writer {__version__}",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Compile command
    compile_parser = subparsers.add_parser(
        "compile",
        help="Compile manuscript",
    )
    compile_parser.add_argument(
        "doc_type",
        choices=["manuscript", "supplementary", "revision"],
        default="manuscript",
        nargs="?",
        help="Document type to compile",
    )
    compile_parser.add_argument(
        "--no-figs",
        action="store_true",
        help="Skip figure processing (~4s faster)",
    )
    compile_parser.add_argument(
        "--no-tables",
        action="store_true",
        help="Skip table processing (~4s faster)",
    )
    compile_parser.add_argument(
        "--no-diff",
        action="store_true",
        help="Skip diff generation (~17s faster)",
    )
    compile_parser.add_argument(
        "--draft",
        action="store_true",
        help="Single-pass compilation (~5s faster)",
    )
    compile_parser.add_argument(
        "--dark-mode",
        action="store_true",
        help="Dark mode: black background, white text (figures unchanged)",
    )
    compile_parser.add_argument(
        "--do-p2t",
        action="store_true",
        help="Convert PPTX to TIF",
    )
    compile_parser.add_argument(
        "--crop-tif",
        action="store_true",
        help="Crop TIF files",
    )
    compile_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show verbose output",
    )
    compile_parser.add_argument(
        "--force",
        action="store_true",
        help="Force full recompilation",
    )
    compile_parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current directory)",
    )

    # New command
    new_parser = subparsers.add_parser(
        "new",
        help="Create new manuscript project",
    )
    new_parser.add_argument(
        "project_name",
        help="Name of the new project",
    )
    new_parser.add_argument(
        "--target-dir",
        type=Path,
        default=None,
        help="Target directory (default: current directory)",
    )
    new_parser.add_argument(
        "--git-strategy",
        choices=["child", "parent", "origin", "none"],
        default="child",
        help="Git initialization strategy",
    )

    # Watch command
    watch_parser = subparsers.add_parser(
        "watch",
        help="Watch for changes and auto-compile",
    )
    watch_parser.add_argument(
        "doc_type",
        choices=["manuscript", "supplementary", "revision"],
        default="manuscript",
        nargs="?",
        help="Document type to watch",
    )
    watch_parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path.cwd(),
        help="Project directory (default: current directory)",
    )

    # Update command
    update_parser = subparsers.add_parser(
        "update",
        help="Update scitex-writer to latest version",
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Execute command
    if args.command == "compile":
        return _compile_cmd(args)
    elif args.command == "new":
        return _new_cmd(args)
    elif args.command == "watch":
        return _watch_cmd(args)
    elif args.command == "update":
        return update()

    return 0


def _compile_cmd(args):
    """Execute compile command."""
    from .writer import Writer

    writer = Writer(args.project_dir, doc_type=args.doc_type)
    result = writer.compile(
        no_figs=args.no_figs,
        no_tables=args.no_tables,
        no_diff=args.no_diff,
        draft=args.draft,
        dark_mode=args.dark_mode,
        do_p2t=args.do_p2t,
        crop_tif=args.crop_tif,
        verbose=args.verbose,
        force=args.force,
    )

    if result.success:
        print(f"✓ Compilation successful: {result.pdf_path}")
        return 0
    else:
        print(f"✗ Compilation failed: {result.error}")
        return 1


def _new_cmd(args):
    """Execute new command."""
    from .template import clone_writer_project

    success = clone_writer_project(
        project_name=args.project_name,
        target_dir=args.target_dir,
        git_strategy=args.git_strategy,
    )

    return 0 if success else 1


def _watch_cmd(args):
    """Execute watch command."""
    from .watch import watch_manuscript

    try:
        watch_manuscript(
            project_dir=args.project_dir,
            doc_type=args.doc_type,
        )
        return 0
    except Exception as e:
        print(f"Watch failed: {e}")
        return 1


def update():
    """Update scitex-writer to latest version."""
    from . import __version__

    print(f"SciTeX Writer v{__version__}")
    print("Checking for updates...")

    # Try to run update script if in git repository
    try:
        project_root = Path(__file__).parent.parent.parent.parent
        update_script = project_root / "scripts" / "repository_maintenance" / "update.sh"

        if update_script.exists():
            subprocess.run([str(update_script)], check=True)
            return 0
        else:
            print("Update script not found. Trying pip...")
            subprocess.run(
                ["pip", "install", "--upgrade", "scitex-writer"],
                check=True,
            )
            return 0

    except subprocess.CalledProcessError as e:
        print(f"Update failed: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["main", "update"]
