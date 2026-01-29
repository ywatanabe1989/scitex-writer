#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-30
# File: src/scitex_writer/_cli/introspect.py

"""Introspection CLI commands for scitex-writer (figrecipe-compatible format)."""

import argparse
import importlib
import inspect
import sys

# Color mapping for types (matching figrecipe)
TYPE_COLORS = {"M": "blue", "C": "magenta", "F": "green", "V": "cyan"}

# ANSI color codes
ANSI = {
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "green": "\033[32m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "yellow": "\033[33m",
    "reset": "\033[0m",
    "bold": "\033[1m",
}


def _style(text: str, fg: str = None, bold: bool = False) -> str:
    """Apply ANSI styling to text."""
    if not sys.stdout.isatty():
        return text
    prefix = ""
    if bold:
        prefix += ANSI["bold"]
    if fg and fg in ANSI:
        prefix += ANSI[fg]
    if prefix:
        return f"{prefix}{text}{ANSI['reset']}"
    return text


def _get_api_tree(module, max_depth: int = 5, docstring: bool = False) -> list[dict]:
    """Get API tree for a module with types and signatures.

    Returns list of dicts with: Name, Type, Depth, Docstring (optional)
    """
    results = []

    def _visit(obj, name: str, depth: int, visited: set):
        if depth > max_depth:
            return
        obj_id = id(obj)
        if obj_id in visited:
            return
        visited.add(obj_id)

        # Determine type
        if inspect.ismodule(obj):
            obj_type = "M"
        elif inspect.isclass(obj):
            obj_type = "C"
        elif callable(obj):
            obj_type = "F"
        else:
            obj_type = "V"

        entry = {"Name": name, "Type": obj_type, "Depth": depth}
        if docstring:
            entry["Docstring"] = inspect.getdoc(obj) or ""
        results.append(entry)

        # Recurse into modules
        if inspect.ismodule(obj) and depth < max_depth:
            if hasattr(obj, "__all__"):
                members = [(n, getattr(obj, n, None)) for n in obj.__all__]
            else:
                members = [
                    (n, v) for n, v in inspect.getmembers(obj) if not n.startswith("_")
                ]
            for member_name, member_obj in members:
                if member_obj is not None:
                    _visit(member_obj, f"{name}.{member_name}", depth + 1, visited)

    _visit(module, module.__name__.split(".")[-1], 0, set())
    return results


def cmd_api(args: argparse.Namespace) -> int:
    """List API tree of a Python module."""
    dotted_path = args.dotted_path.replace("-", "_")

    try:
        module = importlib.import_module(dotted_path)
    except ImportError as e:
        print(f"Error importing {dotted_path}: {e}", file=sys.stderr)
        return 1

    df = _get_api_tree(module, max_depth=args.max_depth, docstring=(args.verbose >= 1))

    if args.json:
        import json

        print(json.dumps(df, indent=2))
        return 0

    print(_style(f"API tree of {dotted_path} ({len(df)} items):", fg="cyan"))
    legend = " ".join(
        _style(f"[{t}]={n}", fg=TYPE_COLORS[t])
        for t, n in [
            ("M", "Module"),
            ("C", "Class"),
            ("F", "Function"),
            ("V", "Variable"),
        ]
    )
    print(f"Legend: {legend}")

    for row in df:
        indent = "  " * row["Depth"]
        t = row["Type"]
        type_s = _style(f"[{t}]", fg=TYPE_COLORS.get(t, "yellow"))
        name = row["Name"].split(".")[-1]
        sig_s = ""

        if t == "F":
            try:
                # Get the actual function
                parts = row["Name"].split(".")
                obj = module
                for part in parts[1:]:  # Skip module name
                    obj = getattr(obj, part, None)
                    if obj is None:
                        break
                if obj and callable(obj):
                    sig = str(inspect.signature(obj))
                    ret = sig[sig.rfind(" -> ") :] if " -> " in sig else ""
                    pstr = sig[: sig.rfind(" -> ")] if ret else sig
                    params = [
                        p.strip() for p in pstr.strip("()").split(",") if p.strip()
                    ]
                    if len(params) > 2:  # Multiline for 3+ params
                        sig_lines = [f"{indent}    {p}," for p in params[:-1]]
                        sig_lines.append(f"{indent}    {params[-1]}")
                        sig_s = "(\n" + "\n".join(sig_lines) + f"\n{indent}){ret}"
                    else:
                        sig_s = sig
            except Exception:
                pass

        name_s = _style(name, fg=TYPE_COLORS.get(t, "white"), bold=True)
        sig_styled = _style(sig_s, fg=TYPE_COLORS.get(t, "white"), bold=True)
        print(f"{indent}{type_s} {name_s}{sig_styled}")

        if args.verbose >= 1 and row.get("Docstring"):
            if args.verbose == 1:
                doc = row["Docstring"].split("\n")[0][:60]
                print(f"{indent}    - {doc}")
            else:
                for ln in row["Docstring"].split("\n"):
                    print(f"{indent}    {ln}")

    return 0


def cmd_list_python_apis(args: argparse.Namespace) -> int:
    """List Python APIs (alias for introspect api scitex_writer)."""
    args.dotted_path = "scitex_writer"
    return cmd_api(args)


def register_parser(subparsers) -> argparse.ArgumentParser:
    """Register introspect subcommand parser."""
    intro_help = """Python package introspection utilities.

Quick start:
  scitex-writer introspect api scitex_writer       # Full API tree
  scitex-writer introspect api scitex_writer -v    # With docstrings
  scitex-writer introspect api scitex_writer --json  # JSON output
"""
    intro_parser = subparsers.add_parser(
        "introspect",
        help="Python package introspection",
        description=intro_help,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    intro_sub = intro_parser.add_subparsers(dest="introspect_command", title="Commands")

    api_parser = intro_sub.add_parser("api", help="List API tree of a module")
    api_parser.add_argument(
        "dotted_path", help="Python dotted path (e.g., scitex_writer)"
    )
    api_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity: -v +doc, -vv full doc",
    )
    api_parser.add_argument(
        "-d",
        "--max-depth",
        type=int,
        default=5,
        help="Max recursion depth (default: 5)",
    )
    api_parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output as JSON",
    )
    api_parser.set_defaults(func=cmd_api)

    return intro_parser


def register_list_python_apis(parent_parser) -> None:
    """Register list-python-apis command on a parent parser."""
    lst_parser = parent_parser.add_parser(
        "list-python-apis",
        help="List Python APIs (alias for: scitex-writer introspect api scitex_writer)",
    )
    lst_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity: -v +doc, -vv full doc",
    )
    lst_parser.add_argument(
        "-d", "--max-depth", type=int, default=5, help="Max recursion depth"
    )
    lst_parser.add_argument(
        "--json",
        action="store_true",
        default=False,
        help="Output as JSON",
    )
    lst_parser.set_defaults(func=cmd_list_python_apis)


# EOF
