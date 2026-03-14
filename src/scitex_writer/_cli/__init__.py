#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_cli/__init__.py

"""CLI package for scitex-writer.

Subcommands:
    mcp        - MCP server commands
    guidelines - IMRAD writing guidelines
    prompts    - Action prompts (Asta)
    compile    - Compile LaTeX to PDF
    bib        - Bibliography management
    tables     - Table management
    figures    - Figure management
    gui        - Browser-based editor
"""

import argparse
import sys

from .. import __version__
from .._usage import get_usage
from . import (
    bib,
    compile,
    export,
    figures,
    gui,
    guidelines,
    introspect,
    mcp,
    migration,
    prompts,
    tables,
    update,
)


def _cmd_usage(args: argparse.Namespace) -> int:
    """Print usage guide."""
    print(get_usage())
    return 0


def _register_usage_command(subparsers) -> None:
    """Register usage command."""
    usage_parser = subparsers.add_parser(
        "usage",
        help="Show usage guide for scitex-writer",
    )
    usage_parser.set_defaults(func=_cmd_usage)


def _print_help_recursive(parser, subparsers_map) -> None:
    """Print help for the main parser and all subcommands."""
    parser.print_help()
    print()
    for name in sorted(subparsers_map):
        print(f"=== {name} ===")
        subparsers_map[name].print_help()
        print()


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="scitex-writer",
        description="SciTeX Writer - LaTeX manuscript compilation system with MCP server",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--help-recursive",
        action="store_true",
        default=False,
        help="Show help for all commands and subcommands",
    )
    subparsers = parser.add_subparsers(dest="command", title="Commands")

    # Register all subcommand modules
    mcp_parser = mcp.register_parser(subparsers)
    guidelines_parser = guidelines.register_parser(subparsers)
    prompts_parser = prompts.register_parser(subparsers)
    compile_parser = compile.register_parser(subparsers)
    export_parser = export.register_parser(subparsers)
    bib_parser = bib.register_parser(subparsers)
    tables_parser = tables.register_parser(subparsers)
    figures_parser = figures.register_parser(subparsers)
    gui_parser = gui.register_parser(subparsers)
    update_parser = update.register_parser(subparsers)
    migration_parser = migration.register_parser(subparsers)
    introspect.register_parser(subparsers)

    # Register top-level convenience commands
    introspect.register_list_python_apis(subparsers)
    _register_usage_command(subparsers)

    # docs — reusable mixin from scitex_dev
    try:
        from scitex_dev.cli import register_docs_subcommand

        register_docs_subcommand(subparsers, package="scitex-writer")
    except ImportError:
        pass

    # Handle --help-recursive before parse_args to avoid requiring a subcommand
    if "--help-recursive" in sys.argv:
        all_subparsers = {}
        for action in parser._subparsers._actions:
            if isinstance(action, argparse._SubParsersAction):
                all_subparsers.update(action.choices)
        _print_help_recursive(parser, all_subparsers)
        return 0

    args = parser.parse_args()

    # Handle command dispatch
    if hasattr(args, "func"):
        return args.func(args)

    # No subcommand - show help for the command group
    parsers = {
        "mcp": mcp_parser,
        "guidelines": guidelines_parser,
        "prompts": prompts_parser,
        "compile": compile_parser,
        "export": export_parser,
        "bib": bib_parser,
        "tables": tables_parser,
        "figures": figures_parser,
        "gui": gui_parser,
        "update": update_parser,
        "migration": migration_parser,
    }

    if args.command in parsers:
        parsers[args.command].print_help()
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# EOF
