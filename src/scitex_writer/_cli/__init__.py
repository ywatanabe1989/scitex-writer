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
"""

import argparse
import sys

from .. import __version__
from . import bib, compile, figures, guidelines, introspect, mcp, prompts, tables


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
    subparsers = parser.add_subparsers(dest="command", title="Commands")

    # Register all subcommand modules
    mcp_parser = mcp.register_parser(subparsers)
    guidelines_parser = guidelines.register_parser(subparsers)
    prompts_parser = prompts.register_parser(subparsers)
    compile_parser = compile.register_parser(subparsers)
    bib_parser = bib.register_parser(subparsers)
    tables_parser = tables.register_parser(subparsers)
    figures_parser = figures.register_parser(subparsers)
    introspect.register_parser(subparsers)

    # Register top-level convenience commands
    introspect.register_list_python_apis(subparsers)

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
        "bib": bib_parser,
        "tables": tables_parser,
        "figures": figures_parser,
    }

    if args.command in parsers:
        parsers[args.command].print_help()
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())


# EOF
