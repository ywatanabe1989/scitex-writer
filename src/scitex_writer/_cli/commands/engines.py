#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/engines.py

"""``list-engines`` command — which LaTeX compilation engines are available.

Pure-Python introspection over ``_core._engines`` (a port of
``scripts/shell/modules/select_compilation_engine.sh``'s detection logic).
Read-only: it does not select an engine for a compile, only reports what is
installed. Sibling to ``list-deps`` (same flat verb-noun house style, per §1).
"""

from __future__ import annotations

import click

from .._core import main_group
from .._helpers import _emit_json

# =========================================================================
# list-engines  (flat verb-noun top-level command, per §1 — same house
# style as list-deps / compile-manuscript / check-limits)
# =========================================================================


@main_group.command("list-engines")
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Emit JSON (engine/available/version/info) instead of a table.",
)
def list_engines_cmd(as_json):
    """List the LaTeX compilation engines (tectonic / latexmk / 3pass) and
    whether each is installed on this machine.

    Read-only introspection — does not affect which engine a compile picks
    (that stays ``--engine`` / auto-detect at compile time).

    \b
    Example:
        $ scitex-writer list-engines
        $ scitex-writer list-engines --json
    """
    from ..._core._engines import list_available_engines

    engines = list_available_engines()
    if as_json:
        _emit_json(engines)
        return 0
    for e in engines:
        mark = "✓" if e["available"] else "✗"
        version = e["version"] or ("not available" if not e["available"] else "")
        click.echo(f"  {mark} {e['engine']:<10} ({version:<10}) {e['info']}")
    return 0


# EOF
