#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/checks.py
# Purpose: Public Python API for pre-compilation project checks.
#
# Wraps the same handlers that MCP and check_project.sh use so that three
# interfaces (scripts, MCP, Python) share one implementation — writer
# issues #44 (float order) and #45 (cross-refs + citations).

"""Pre-compilation check functions.

Usage::

    import scitex_writer as sw

    # Validate every \\ref / \\cite / \\label resolves
    result = sw.checks.references("./my-paper")
    if result["summary"].get("errors"):
        raise SystemExit("Broken references — see result['stdout']")

    # Preview float renumbering
    sw.checks.float_order("./my-paper", dry_run=True)

    # Apply the renumbering
    sw.checks.float_order("./my-paper", fix=True)
"""

from typing import Literal as _Literal

from ._mcp.handlers import check_float_order as _check_float_order
from ._mcp.handlers import check_references as _check_references

try:
    from scitex_dev.decorators import supports_return_as as _supports_return_as
except ImportError:

    def _supports_return_as(fn):
        return fn


@_supports_return_as
def references(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "all"] = "all",
    parse_log: bool = False,
) -> dict:
    """Validate cross-references, citations, and labels (writer #45).

    Returns a dict with ``success``, ``exit_code``, ``stdout``,
    ``stderr``, and ``summary={passed, warnings, errors}``.
    """
    return _check_references(project_dir, doc_type, parse_log)


@_supports_return_as
def float_order(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "all"] = "manuscript",
    fix: bool = False,
    dry_run: bool = False,
) -> dict:
    """Validate / renumber figure + table reference order (writer #44).

    With ``fix=True`` renames files and updates ``\\ref{}`` / ``\\label{}``
    so floats appear in numerical order. ``dry_run=True`` previews.
    """
    return _check_float_order(project_dir, doc_type, fix, dry_run)


__all__ = ["references", "float_order"]

# EOF
