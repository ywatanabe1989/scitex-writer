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


def _get_tool_module(name: str) -> str:
    """Get logical module for a tool name."""
    if name == "usage":
        return "general"
    if "bib" in name:
        return "bib"
    if "compile" in name:
        return "compile"
    if "figure" in name or "pdf_to_images" in name:
        return "figures"
    if "table" in name or "csv_to_latex" in name or "latex_to_csv" in name:
        return "tables"
    if (
        "project" in name
        or "clone" in name
        or "get_pdf" in name
        or "document_types" in name
    ):
        return "project"
    if "guideline" in name:
        return "guidelines"
    if "prompts" in name:
        return "prompts"
    return "general"


def _style(text: str, fg: str = None, bold: bool = False) -> str:
    """Apply ANSI color styling."""
    import sys

    if not sys.stdout.isatty():
        return text
    codes = {
        "green": "\033[32m",
        "cyan": "\033[36m",
        "yellow": "\033[33m",
        "magenta": "\033[35m",
        "white": "\033[37m",
        "bold": "\033[1m",
        "reset": "\033[0m",
    }
    prefix = ""
    if bold:
        prefix += codes["bold"]
    if fg and fg in codes:
        prefix += codes[fg]
    return f"{prefix}{text}{codes['reset']}" if prefix else text


def _format_tool_signature(tool, compact: bool = False, indent: str = "  ") -> str:
    """Format tool as Python-like function signature with colors."""
    import inspect
    import re

    params = []
    if hasattr(tool, "parameters") and tool.parameters:
        schema = tool.parameters
        props = schema.get("properties", {})
        required = schema.get("required", [])
        for name, info in props.items():
            ptype = info.get("type", "any")
            default = info.get("default")
            # Color: name in white bold, type in cyan, default in yellow
            name_s = _style(name, "white", bold=True)
            type_s = _style(ptype, "cyan")
            if name in required:
                params.append(f"{name_s}: {type_s}")
            elif default is not None:
                def_str = repr(default) if len(repr(default)) < 20 else "..."
                def_s = _style(f"= {def_str}", "yellow")
                params.append(f"{name_s}: {type_s} {def_s}")
            else:
                def_s = _style("= None", "yellow")
                params.append(f"{name_s}: {type_s} {def_s}")

    # Get return type with dict keys from docstring
    ret_type = ""
    if hasattr(tool, "fn") and tool.fn:
        try:
            sig = inspect.signature(tool.fn)
            if sig.return_annotation != inspect.Parameter.empty:
                ret = sig.return_annotation
                ret_name = ret.__name__ if hasattr(ret, "__name__") else str(ret)
                # Extract return dict keys from docstring
                keys = []
                if tool.description and "Returns" in tool.description:
                    match = re.search(
                        r"Returns\s*[-]+\s*\w+\s*(.+?)(?:Raises|Examples|Notes|\Z)",
                        tool.description,
                        re.DOTALL,
                    )
                    if match:
                        keys = re.findall(r"'([a-z_]+)'", match.group(1))
                keys_s = _style(f"{{{', '.join(keys)}}}", "yellow") if keys else ""
                ret_type = f" -> {_style(ret_name, 'magenta')}{keys_s}"
        except Exception:
            pass

    # Function name in green
    name_s = _style(tool.name, "green")
    if compact or len(params) <= 2:
        return f"{indent}{name_s}({', '.join(params)}){ret_type}"
    else:
        param_indent = indent + "    "
        params_str = ",\n".join(f"{param_indent}{p}" for p in params)
        return f"{indent}{name_s}(\n{params_str}\n{indent}){ret_type}"


def cmd_list_tools(args: argparse.Namespace) -> int:
    """List all available MCP tools (figrecipe-compatible format)."""
    from .._mcp import mcp

    verbose = getattr(args, "verbose", 0)
    compact = getattr(args, "compact", False)
    module_filter = getattr(args, "module", None)
    as_json = getattr(args, "json", False)

    tools = list(mcp._tool_manager._tools.keys())
    total = len(tools)

    # Group by logical module
    modules = {}
    for tool_name in sorted(tools):
        module = _get_tool_module(tool_name)
        if module not in modules:
            modules[module] = []
        modules[module].append(tool_name)

    # Filter by module if specified
    if module_filter:
        module_filter = module_filter.lower()
        if module_filter not in modules:
            print(f"ERROR: Unknown module '{module_filter}'")
            print(f"Available modules: {', '.join(sorted(modules.keys()))}")
            return 1
        modules = {module_filter: modules[module_filter]}

    if as_json:
        import json

        output = {
            "name": "scitex-writer",
            "total": sum(len(t) for t in modules.values()),
            "modules": {},
        }
        for mod, tool_list in modules.items():
            output["modules"][mod] = {
                "count": len(tool_list),
                "tools": tool_list,
            }
        print(json.dumps(output, indent=2))
        return 0

    print(_style("SciTeX Writer MCP: scitex-writer", "cyan", bold=True))
    print(f"Tools: {total} ({len(modules)} modules)\n")

    for module in sorted(modules.keys()):
        mod_tools = sorted(modules[module])
        print(_style(f"{module}: {len(mod_tools)} tools", "green", bold=True))
        for tool_name in mod_tools:
            tool_obj = mcp._tool_manager._tools.get(tool_name)

            if verbose == 0:
                # Names only
                print(f"  {tool_name}")
            elif verbose == 1:
                # Signatures
                sig = (
                    _format_tool_signature(tool_obj, compact=compact)
                    if tool_obj
                    else f"  {tool_name}"
                )
                print(sig)
            elif verbose == 2:
                # Signature + one-line description
                sig = (
                    _format_tool_signature(tool_obj, compact=compact)
                    if tool_obj
                    else f"  {tool_name}"
                )
                print(sig)
                if tool_obj and tool_obj.description:
                    desc = tool_obj.description.split("\n")[0].strip()
                    print(f"    {desc}")
                print()
            else:
                # Signature + full description
                sig = (
                    _format_tool_signature(tool_obj, compact=compact)
                    if tool_obj
                    else f"  {tool_name}"
                )
                print(sig)
                if tool_obj and tool_obj.description:
                    for line in tool_obj.description.strip().split("\n"):
                        print(f"    {line}")
                print()
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

    lst = mcp_sub.add_parser(
        "list-tools",
        help="List all available MCP tools",
        description="Verbosity: (none) names, -v signatures, -vv +description, -vvv full",
    )
    lst.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity: -v sig, -vv +desc, -vvv full",
    )
    lst.add_argument(
        "-c", "--compact", action="store_true", help="Compact signatures (single line)"
    )
    lst.add_argument(
        "-m",
        "--module",
        type=str,
        default=None,
        help="Filter by module (bib, compile, figures, tables, project, guidelines, prompts)",
    )
    lst.add_argument(
        "--json", action="store_true", default=False, help="Output as JSON"
    )
    lst.set_defaults(func=cmd_list_tools)

    doc = mcp_sub.add_parser("doctor", help="Check MCP server health")
    doc.set_defaults(func=cmd_doctor)

    start = mcp_sub.add_parser("start", help="Start the MCP server")
    start.add_argument("-t", "--transport", choices=["stdio", "sse"], default="stdio")
    start.set_defaults(func=cmd_start)

    return mcp_parser


# EOF
