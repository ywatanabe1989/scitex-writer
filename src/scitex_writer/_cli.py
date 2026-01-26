#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_cli.py

"""CLI entry point for scitex-writer."""

import argparse
import sys
from pathlib import Path

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


def cmd_mcp_list_tools(args: argparse.Namespace) -> int:
    """List all available MCP tools."""
    from ._mcp import mcp

    print(f"scitex-writer {__version__}")
    print()
    print("Available MCP tools:")
    print()

    for tool in mcp._tool_manager._tools.values():
        name = tool.name
        desc = (tool.description or "").split("\n")[0]
        print(f"  {name}")
        if desc:
            print(f"    {desc}")
        print()

    return 0


def cmd_mcp_doctor(args: argparse.Namespace) -> int:
    """Check MCP server health and configuration."""
    import shutil

    print(f"scitex-writer {__version__}")
    print()
    print("Health Check")
    print("=" * 40)

    # Check Python dependencies
    checks = []

    try:
        import fastmcp

        checks.append(("fastmcp", True, fastmcp.__version__))
    except ImportError:
        checks.append(("fastmcp", False, "not installed"))

    try:
        from ._mcp import mcp

        tool_count = len(mcp._tool_manager._tools)
        checks.append(("MCP server", True, f"{tool_count} tools"))
    except Exception as e:
        checks.append(("MCP server", False, str(e)))

    # Check CLI availability
    scitex_path = shutil.which("scitex-writer")
    if scitex_path:
        checks.append(("CLI", True, scitex_path))
    else:
        checks.append(("CLI", False, "not in PATH"))

    # Print results
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


# Guidelines commands


def cmd_guidelines(args: argparse.Namespace) -> int:
    """Get IMRAD writing guidelines for a section."""
    from .guidelines import build, get, get_source

    try:
        source = get_source(args.section)

        if args.info:
            print(f"Section: {args.section}")
            print(f"Source: {source['source']}")
            print(f"Path: {source['path']}")
            print()

        if args.draft:
            if args.draft == "-":
                draft = sys.stdin.read()
            else:
                draft_path = Path(args.draft)
                if not draft_path.exists():
                    print(f"Error: Draft file not found: {draft_path}", file=sys.stderr)
                    return 1
                draft = draft_path.read_text(encoding="utf-8")

            prompt = build(args.section, draft)
            print(prompt)
        else:
            guidelines = get(args.section)
            print(guidelines)

        return 0
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_guidelines_list(args: argparse.Namespace) -> int:
    """List available guidelines sections."""
    from .guidelines import SECTIONS

    print("Available sections:")
    for section in SECTIONS:
        print(f"  - {section}")
    return 0


# Prompts commands


def cmd_prompts_asta(args: argparse.Namespace) -> int:
    """Generate AI2 Asta prompt from manuscript."""
    from .prompts import generate_ai2_prompt

    project_path = Path(args.project).resolve()

    if not project_path.exists():
        print(f"Error: Project path not found: {project_path}", file=sys.stderr)
        return 1

    result = generate_ai2_prompt(project_path, search_type=args.type)

    if not result["success"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        if result["next_steps"]:
            print("\nSuggested next steps:", file=sys.stderr)
            for step in result["next_steps"]:
                print(f"  - {step}", file=sys.stderr)
        return 1

    if args.info:
        print(f"Search type: {result['search_type']}")
        print()
        print("Next steps:")
        for step in result["next_steps"]:
            print(f"  - {step}")
        print()
        print("--- Generated Prompt ---")
        print()

    print(result["prompt"])
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
        add_help=True,
    )
    mcp_subparsers = mcp_parser.add_subparsers(dest="mcp_command", title="Commands")

    mcp_installation = mcp_subparsers.add_parser(
        "installation",
        help="Show Claude Desktop installation guide",
    )
    mcp_installation.set_defaults(func=cmd_mcp_config)

    mcp_list_tools = mcp_subparsers.add_parser(
        "list-tools",
        help="List all available MCP tools",
    )
    mcp_list_tools.set_defaults(func=cmd_mcp_list_tools)

    mcp_doctor = mcp_subparsers.add_parser(
        "doctor",
        help="Check MCP server health and configuration",
    )
    mcp_doctor.set_defaults(func=cmd_mcp_doctor)

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

    # Guidelines command
    guidelines_help = """IMRAD writing guidelines for scientific manuscripts.

Quick start:
  scitex-writer guidelines list              # List available sections
  scitex-writer guidelines abstract          # Get abstract guidelines
  scitex-writer guidelines abstract -d draft.tex  # Build with draft

Environment variables:
  SCITEX_WRITER_GUIDELINE_ABSTRACT  Custom abstract guidelines path
  SCITEX_WRITER_GUIDELINE_DIR       Custom guidelines directory
"""
    guidelines_parser = subparsers.add_parser(
        "guidelines",
        help="IMRAD writing guidelines",
        description=guidelines_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True,
    )
    guidelines_subparsers = guidelines_parser.add_subparsers(
        dest="guidelines_command", title="Commands"
    )

    # guidelines list
    guidelines_list = guidelines_subparsers.add_parser(
        "list",
        help="List available sections",
    )
    guidelines_list.set_defaults(func=cmd_guidelines_list)

    # guidelines <section>
    for section in ["abstract", "introduction", "methods", "discussion", "proofread"]:
        section_parser = guidelines_subparsers.add_parser(
            section,
            help=f"Get {section} guidelines",
        )
        section_parser.add_argument(
            "-d",
            "--draft",
            help="Path to draft file to build prompt (use '-' for stdin)",
        )
        section_parser.add_argument(
            "-i",
            "--info",
            action="store_true",
            help="Show source info",
        )
        section_parser.set_defaults(func=cmd_guidelines, section=section)

    # Prompts command group
    prompts_help = """Action prompts for manuscript workflows.

Quick start:
  scitex-writer prompts asta                 # Generate AI2 Asta prompt
  scitex-writer prompts asta -t coauthors    # Find collaborators
"""
    prompts_parser = subparsers.add_parser(
        "prompts",
        help="Action prompts (Asta)",
        description=prompts_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=True,
    )
    prompts_subparsers = prompts_parser.add_subparsers(
        dest="prompts_command", title="Commands"
    )

    # prompts asta
    prompts_asta = prompts_subparsers.add_parser(
        "asta",
        help="Generate AI2 Asta prompt from manuscript",
    )
    prompts_asta.add_argument(
        "-t",
        "--type",
        choices=["related", "coauthors"],
        default="related",
        help="Search type (default: related)",
    )
    prompts_asta.add_argument(
        "-p",
        "--project",
        default=".",
        help="Path to scitex-writer project (default: current directory)",
    )
    prompts_asta.add_argument(
        "-i",
        "--info",
        action="store_true",
        help="Show search info and next steps",
    )
    prompts_asta.set_defaults(func=cmd_prompts_asta)

    args = parser.parse_args()

    # Handle command dispatch
    if hasattr(args, "func"):
        return args.func(args)

    # No subcommand - show help
    if args.command == "mcp":
        mcp_parser.print_help()
        return 0

    if args.command == "guidelines":
        guidelines_parser.print_help()
        return 0

    if args.command == "prompts":
        prompts_parser.print_help()
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

# EOF
