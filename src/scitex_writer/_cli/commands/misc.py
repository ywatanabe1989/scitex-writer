#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/misc.py

"""Top-level convenience commands: list-python-apis and show-usage."""

from __future__ import annotations

import click

from .._core import main_group
from .._helpers import _emit_json


@main_group.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc.")
@click.option(
    "-d", "--max-depth", type=int, default=5, help="Max recursion depth (default: 5)."
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def list_python_apis(verbose, max_depth, as_json):
    """List the public Python API surface of scitex_writer.

    \b
    Example:
        $ scitex-writer list-python-apis
        $ scitex-writer list-python-apis -v
        $ scitex-writer list-python-apis --json
    """
    from ..introspect import cmd_list_python_apis

    return cmd_list_python_apis(verbose=verbose, max_depth=max_depth, as_json=as_json)


# =========================================================================
# show-usage (renamed from `usage` to satisfy §1 verb-leaf)
# =========================================================================


@main_group.command("show-usage")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def show_usage(as_json):
    """Print the long-form usage guide for scitex-writer projects.

    \b
    Example:
        $ scitex-writer show-usage
        $ scitex-writer show-usage --json
    """
    from ..._usage import get_usage

    text = get_usage()
    if as_json:
        _emit_json({"usage": text})
    else:
        click.echo(text)
    return 0


# EOF
