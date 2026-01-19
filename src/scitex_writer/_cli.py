#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: src/scitex_writer/_cli.py

"""CLI entry point for scitex-writer."""

import argparse
import sys

from . import __version__

CLAUDE_DESKTOP_CONFIG_CLI = """{
  "mcpServers": {
    "scitex-writer": {
      "command": "/path/to/.venv/bin/scitex-writer",
      "args": ["mcp", "start"]
    }
  }
}"""

CLAUDE_DESKTOP_CONFIG_PYTHON = """{
  "mcpServers": {
    "scitex-writer": {
      "command": "/path/to/.venv/bin/python",
      "args": ["-m", "scitex_writer", "mcp", "start"]
    }
  }
}"""


def cmd_mcp_start(args: argparse.Namespace) -> int:
    """Start the MCP server."""
    from ._mcp import run_server

    run_server(transport=args.transport)
    return 0


def cmd_mcp_config(args: argparse.Namespace) -> int:
    """Show Claude Desktop configuration snippet."""
    import shutil

    print(f"scitex-writer {__version__}")
    print()
    print("Add this to your Claude Desktop config file:")
    print()
    print("  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("  Linux: ~/.config/Claude/claude_desktop_config.json")
    print()

    # Show actual paths if available
    scitex_path = shutil.which("scitex-writer")
    if scitex_path:
        print(f"Your installation path: {scitex_path}")
        print()

    print("Option 1: CLI command (replace path with your installation)")
    print(CLAUDE_DESKTOP_CONFIG_CLI)
    print()
    print("Option 2: Python module (replace path with your installation)")
    print(CLAUDE_DESKTOP_CONFIG_PYTHON)
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="scitex-writer",
        description="SciTeX Writer - LaTeX manuscript compilation system with MCP server",
        add_help=True,
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command", title="Commands")

    # MCP command group
    mcp_help = """MCP (Model Context Protocol) server commands.

Quick start:
  scitex-writer mcp installation  # Show Claude Desktop installation guide
  scitex-writer mcp start         # Start MCP server
"""
    mcp_parser = subparsers.add_parser(
        "mcp",
        help="MCP (Model Context Protocol) server commands",
        description=mcp_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True,
    )
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", title="Commands")

    # mcp installation
    mcp_installation = mcp_subparsers.add_parser(
        "installation",
        help="Show Claude Desktop installation guide",
    )
    mcp_installation.set_defaults(func=cmd_mcp_config)

    # mcp start
    mcp_start = mcp_subparsers.add_parser(
        "start",
        help="Start the MCP server",
    )
    mcp_start.add_argument(
        "-t",
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport method (default: stdio)",
    )
    mcp_start.set_defaults(func=cmd_mcp_start)

    args = parser.parse_args()

    # Handle command dispatch
    if hasattr(args, "func"):
        return args.func(args)

    # No subcommand - show help
    if args.command == "mcp":
        mcp_parser.print_help()
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

# EOF
