#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_cli/mcp.py

"""MCP CLI commands."""

import argparse
import shutil

from .. import __version__

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


def cmd_start(args: argparse.Namespace) -> int:
    """Start the MCP server."""
    from .._mcp import run_server

    run_server(transport=args.transport)
    return 0


def cmd_list_tools(args: argparse.Namespace) -> int:
    """List all available MCP tools as markdown."""
    from .._mcp import mcp

    print(f"# scitex-writer {__version__} MCP Tools\n")

    # Group tools by category
    categories = {}
    for tool in mcp._tool_manager._tools.values():
        name = tool.name
        parts = name.split("_")
        category = parts[0] if len(parts) > 1 else "general"
        if category not in categories:
            categories[category] = []
        categories[category].append(tool)

    for category in sorted(categories.keys()):
        print(f"## {category.title()}\n")
        print("| Tool | Description |")
        print("|------|-------------|")
        for tool in sorted(categories[category], key=lambda t: t.name):
            desc = (tool.description or "").split("\n")[0][:60]
            print(f"| `{tool.name}` | {desc} |")
        print()

    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    """Check MCP server health and configuration."""
    print(f"scitex-writer {__version__}\n")
    print("Health Check")
    print("=" * 40)

    checks = []

    try:
        import fastmcp

        checks.append(("fastmcp", True, fastmcp.__version__))
    except ImportError:
        checks.append(("fastmcp", False, "not installed"))

    try:
        from .._mcp import mcp

        tool_count = len(mcp._tool_manager._tools)
        checks.append(("MCP server", True, f"{tool_count} tools"))
    except Exception as e:
        checks.append(("MCP server", False, str(e)))

    scitex_path = shutil.which("scitex-writer")
    if scitex_path:
        checks.append(("CLI", True, scitex_path))
    else:
        checks.append(("CLI", False, "not in PATH"))

    all_ok = True
    for name, ok, info in checks:
        status = "✓" if ok else "✗"
        if not ok:
            all_ok = False
        print(f"  {status} {name}: {info}")

    print()
    if all_ok:
        print("All checks passed!")
    else:
        print("Some checks failed. Run 'pip install scitex-writer' to fix.")

    return 0 if all_ok else 1


def cmd_config(args: argparse.Namespace) -> int:
    """Show Claude Desktop configuration snippet."""
    print(f"scitex-writer {__version__}\n")
    print("Add this to your Claude Desktop config file:\n")
    print("  macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("  Linux: ~/.config/Claude/claude_desktop_config.json\n")

    scitex_path = shutil.which("scitex-writer")
    if scitex_path:
        print(f"Your installation path: {scitex_path}\n")

    print("Option 1: CLI command (replace path with your installation)")
    print(CLAUDE_DESKTOP_CONFIG_CLI)
    print("\nOption 2: Python module (replace path with your installation)")
    print(CLAUDE_DESKTOP_CONFIG_PYTHON)
    return 0


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register MCP subcommand parser."""
    mcp_help = """MCP (Model Context Protocol) server commands.

Quick start:
  scitex-writer mcp list-tools    # List all tools
  scitex-writer mcp doctor        # Check server health
  scitex-writer mcp installation  # Show Claude Desktop installation guide
  scitex-writer mcp start         # Start MCP server
"""
    mcp_parser = subparsers.add_parser(
        "mcp",
        help="MCP server commands",
        description=mcp_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    mcp_sub = mcp_parser.add_subparsers(dest="mcp_command", title="Commands")

    inst = mcp_sub.add_parser(
        "installation", help="Show Claude Desktop installation guide"
    )
    inst.set_defaults(func=cmd_config)

    lst = mcp_sub.add_parser("list-tools", help="List all available MCP tools")
    lst.set_defaults(func=cmd_list_tools)

    doc = mcp_sub.add_parser("doctor", help="Check MCP server health")
    doc.set_defaults(func=cmd_doctor)

    start = mcp_sub.add_parser("start", help="Start the MCP server")
    start.add_argument("-t", "--transport", choices=["stdio", "sse"], default="stdio")
    start.set_defaults(func=cmd_start)

    return mcp_parser


# EOF
