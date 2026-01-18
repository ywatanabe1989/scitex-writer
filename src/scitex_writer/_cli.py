#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-19 05:00:00
# File: src/scitex_writer/_cli.py

"""CLI entry point for scitex-writer."""

import argparse
import shutil
import sys

from . import __version__

MCP_TOOLS_INFO = """
MCP Server: scitex-writer
Version: {version}

Tool:
  scitex_writer(command, doc_type, project_dir)

Parameters:
  command:     Literal["usage"]
  doc_type:    Literal["manuscript", "supplementary", "revision"]
  project_dir: str (path to project)

Usage:
  The tool returns project usage guide for AI agents.
  AI agents can then use shell commands to perform actual operations.

Setup (clone template first):
  git clone https://github.com/ywatanabe1989/scitex-writer.git my-paper
  cd my-paper

Shell Commands (run via Bash):
  ./compile.sh manuscript       # Compile manuscript
  ./compile.sh supplementary    # Compile supplementary
  ./compile.sh revision         # Compile revision
  ./compile.sh --help-recursive # Full documentation
"""

CLAUDE_DESKTOP_CONFIG_CLI = """{
  "mcpServers": {
    "scitex-writer": {
      "command": "scitex-writer",
      "args": ["mcp", "start"]
    }
  }
}"""

CLAUDE_DESKTOP_CONFIG_PYTHON = """{
  "mcpServers": {
    "scitex-writer": {
      "command": "python",
      "args": ["-m", "scitex_writer", "mcp", "start"]
    }
  }
}"""


def cmd_mcp_info(args: argparse.Namespace) -> int:
    """Show MCP server information and available tools."""
    print(MCP_TOOLS_INFO.format(version=__version__))
    return 0


def cmd_mcp_start(args: argparse.Namespace) -> int:
    """Start the MCP server."""
    from ._mcp import run_server

    run_server(transport=args.transport)
    return 0


def cmd_version(args: argparse.Namespace) -> int:
    """Show version information."""
    print(f"scitex-writer {__version__}")
    return 0


def cmd_mcp_config(args: argparse.Namespace) -> int:
    """Show Claude Desktop configuration snippet."""
    print(f"scitex-writer {__version__}")
    print()
    print("Add this to your Claude Desktop config file:")
    print()
    print("  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("  Linux: ~/.config/Claude/claude_desktop_config.json")
    print()
    print("Option 1: CLI command")
    print(CLAUDE_DESKTOP_CONFIG_CLI)
    print()
    print("Option 2: Python module")
    print(CLAUDE_DESKTOP_CONFIG_PYTHON)
    return 0


def cmd_mcp_doctor(args: argparse.Namespace) -> int:
    """Check MCP server setup and dependencies."""
    print(f"scitex-writer version: {__version__}")
    print()

    # Check Python version
    py_version = sys.version_info
    py_ok = py_version >= (3, 10)
    print(
        f"Python version: {py_version.major}.{py_version.minor}.{py_version.micro}",
        end="",
    )
    print(" [OK]" if py_ok else " [FAIL: requires 3.10+]")

    # Check fastmcp
    try:
        import fastmcp

        fastmcp_version = getattr(fastmcp, "__version__", "unknown")
        print(f"fastmcp: {fastmcp_version} [OK]")
    except ImportError:
        print("fastmcp: not installed [FAIL]")

    # Check if scitex-writer command is available
    scitex_path = shutil.which("scitex-writer")
    if scitex_path:
        print(f"scitex-writer command: {scitex_path} [OK]")
    else:
        print("scitex-writer command: not in PATH [FAIL]")

    # Check MCP server can be imported
    try:
        from ._mcp import mcp

        print(f"MCP server module: {mcp.name} [OK]")
    except Exception as e:
        print(f"MCP server module: import failed - {e} [FAIL]")

    print()
    print("To start the MCP server:")
    print("  scitex-writer mcp start")

    return 0


def print_mcp_help_recursive(mcp_parser: argparse.ArgumentParser) -> None:
    """Print help for mcp and all its subcommands."""
    print("=" * 60)
    print("scitex-writer mcp")
    print("=" * 60)
    mcp_parser.print_help()
    print()

    # Get subparsers
    for action in mcp_parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, subparser in action.choices.items():
                print("-" * 60)
                print(f"scitex-writer mcp {name}")
                print("-" * 60)
                subparser.print_help()
                print()


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

    # version command
    version_parser = subparsers.add_parser(
        "version",
        help="Show version information",
    )
    version_parser.set_defaults(func=cmd_version)

    # MCP command group
    mcp_help = """MCP (Model Context Protocol) server commands.

Commands for managing the MCP server integration with Claude Desktop.

Quick start:
  scitex-writer mcp doctor    # Check MCP setup
  scitex-writer mcp config    # Show Claude Desktop config
  scitex-writer mcp start     # Start MCP server
"""
    mcp_parser = subparsers.add_parser(
        "mcp",
        help="MCP (Model Context Protocol) server commands",
        description=mcp_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True,
    )
    mcp_parser.add_argument(
        "--help-recursive",
        action="store_true",
        help="Show help for all subcommands",
    )
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", title="Commands")

    # mcp config
    mcp_config = mcp_subparsers.add_parser(
        "config",
        help="Show Claude Desktop configuration snippet",
    )
    mcp_config.set_defaults(func=cmd_mcp_config)

    # mcp doctor
    mcp_doctor = mcp_subparsers.add_parser(
        "doctor",
        help="Check MCP server setup and dependencies",
    )
    mcp_doctor.set_defaults(func=cmd_mcp_doctor)

    # mcp info
    mcp_info = mcp_subparsers.add_parser(
        "info",
        help="Show MCP server information and available tools",
    )
    mcp_info.set_defaults(func=cmd_mcp_info)

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

    # Handle --help-recursive for mcp
    if args.command == "mcp" and getattr(args, "help_recursive", False):
        print_mcp_help_recursive(mcp_parser)
        return 0

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
