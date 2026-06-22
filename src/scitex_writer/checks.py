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

from typing import Callable as _Callable
from typing import Literal as _Literal
from typing import Optional as _Optional

from ._mcp.handlers import check_float_order as _check_float_order
from ._mcp.handlers import check_limits as _check_limits
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
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Validate cross-references, citations, and labels (writer #45).

    Returns a dict with ``success``, ``exit_code``, ``stdout``,
    ``stderr``, and ``summary={passed, warnings, errors}``.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_references`. Exposed so
    callers (and tests) can supply an alternate implementation without
    patching module internals.
    """
    handler = handler or _check_references
    return handler(project_dir, doc_type, parse_log)


@_supports_return_as
def float_order(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "all"] = "manuscript",
    fix: bool = False,
    dry_run: bool = False,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Validate / renumber figure + table reference order (writer #44).

    With ``fix=True`` renames files and updates ``\\ref{}`` / ``\\label{}``
    so floats appear in numerical order. ``dry_run=True`` previews.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_float_order`. Exposed so
    callers (and tests) can supply an alternate implementation without
    patching module internals.
    """
    handler = handler or _check_float_order
    return handler(project_dir, doc_type, fix, dry_run)


@_supports_return_as
def limits(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision"] = "manuscript",
    strict: bool = False,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Validate section word limits + the reference cap (the ``limits:`` block).

    Fast pre-compile check — the same one ``compile`` runs as a gate. Reads the
    ``limits:`` block from ``config/config_<doc_type>.yaml`` and compares it
    against ``texcount`` word counts + unique ``\\cite`` keys. Over-limit is a
    warning by default; ``strict=True`` (or ``limits.strict`` /
    ``SCITEX_WRITER_LINT_STRICT=1``) makes breaches errors with a non-zero
    ``exit_code``.

    Returns a dict with ``success``, ``exit_code``, ``stdout``, ``stderr``,
    and ``summary={passed, warnings, errors}``.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_limits`. Exposed so callers (and
    tests) can supply an alternate implementation without patching module
    internals.
    """
    handler = handler or _check_limits
    return handler(project_dir, doc_type, strict)


__all__ = ["references", "float_order", "limits"]

# EOF
