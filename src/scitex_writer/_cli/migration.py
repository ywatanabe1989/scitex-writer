#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/migration.py

"""CLI: migration (import/export Overleaf)."""

import argparse
import sys


def cmd_import(args: argparse.Namespace) -> int:
    """Import Overleaf ZIP into scitex-writer project."""
    from .. import migration

    result = migration.from_overleaf(
        args.zip_path,
        output_dir=args.output,
        project_name=args.name,
        dry_run=args.dry_run,
        force=args.force,
    )

    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    for w in result.get("warnings", []):
        print(f"Warning: {w}", file=sys.stderr)

    if args.dry_run:
        print("Dry run — no files created.\n")
        report = result.get("mapping_report", {})
        if report.get("sections"):
            print("Section mapping:")
            for section, files in report["sections"].items():
                print(f"  {section}: {', '.join(files)}")
        if report.get("bib_files"):
            print(f"\nBibliography: {', '.join(report['bib_files'])}")
        if report.get("images"):
            print(f"Images: {len(report['images'])} file(s)")
        if report.get("unmapped_tex"):
            print(f"Unmapped .tex: {', '.join(report['unmapped_tex'])}")

    print(f"\n{result['message']}")
    return 0


def cmd_export(args: argparse.Namespace) -> int:
    """Export scitex-writer project as Overleaf ZIP."""
    from .. import migration

    result = migration.to_overleaf(
        args.project,
        output_path=args.output,
        dry_run=args.dry_run,
    )

    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    for w in result.get("warnings", []):
        print(f"Warning: {w}", file=sys.stderr)

    if args.dry_run:
        print("Dry run — no ZIP created.\n")
        for f in result.get("files_included", []):
            print(f"  {f}")

    print(f"\n{result['message']}")
    return 0


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register migration subcommand with import/export sub-subcommands."""
    parser = subparsers.add_parser(
        "migration",
        help="Import from / export to external platforms (Overleaf)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  scitex-writer migration import project.zip\n"
            "  scitex-writer migration import project.zip --output ./my-paper\n"
            "  scitex-writer migration import project.zip --dry-run\n"
            "  scitex-writer migration export . --output paper.zip\n"
        ),
    )
    subs = parser.add_subparsers(dest="migration_command")

    # import subcommand
    imp = subs.add_parser("import", help="Import Overleaf ZIP")
    imp.add_argument("zip_path", help="Path to Overleaf ZIP file")
    imp.add_argument("--output", "-o", default=None, help="Output directory")
    imp.add_argument("--name", default=None, help="Project name")
    imp.add_argument("--dry-run", action="store_true")
    imp.add_argument("--force", action="store_true")
    imp.set_defaults(func=cmd_import)

    # export subcommand
    exp = subs.add_parser("export", help="Export as Overleaf ZIP")
    exp.add_argument("project", nargs="?", default=".", help="Project directory")
    exp.add_argument("--output", "-o", default=None, help="Output ZIP path")
    exp.add_argument("--dry-run", action="store_true")
    exp.set_defaults(func=cmd_export)

    return parser


# EOF
