#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/introspect.py

"""introspect command group (Python package introspection)."""

from __future__ import annotations

import click

from .._core import main_group

# =========================================================================
# introspect group  (api -> show-api at leaf for §1; old name kept as alias)
# =========================================================================


@main_group.group("introspect", invoke_without_command=True, hidden=True)
@click.pass_context
def introspect_group(ctx):
    """Python package introspection utilities.

    \b
    Example:
        $ scitex-writer introspect show-api scitex_writer
        $ scitex-writer introspect show-api scitex_writer -v
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@introspect_group.command("show-api")
@click.argument("dotted_path")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc.")
@click.option(
    "-d", "--max-depth", type=int, default=5, help="Max recursion depth (default: 5)."
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def introspect_show_api(dotted_path, verbose, max_depth, as_json):
    """Print the public API tree of a Python package or module.

    \b
    Example:
        $ scitex-writer introspect show-api scitex_writer
        $ scitex-writer introspect show-api scitex_writer.bib -v
        $ scitex-writer introspect show-api scitex_writer --json
    """
    from ..introspect import cmd_api

    return cmd_api(dotted_path, verbose=verbose, max_depth=max_depth, as_json=as_json)


# EOF
