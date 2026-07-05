#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/_helpers.py

"""Pure shared helpers + constants for the scitex-writer CLI.

Moved verbatim from the former `_cli/__init__.py` monolith. These have no
dependency on the root group, so command modules import them freely.
"""

from __future__ import annotations

import json

import click

# =========================================================================
# Helpers
# =========================================================================


def _print_help_recursive(ctx: click.Context, _param, value):
    """Eager callback for --help-recursive: walk the whole tree and dump help."""
    if not value or ctx.resilient_parsing:
        return
    cmd = ctx.command
    click.echo(cmd.get_help(ctx))

    def _walk(c, parent_ctx, prefix):
        if isinstance(c, click.Group):
            for name in sorted(c.commands):
                sub = c.commands[name]
                sub_ctx = click.Context(sub, info_name=name, parent=parent_ctx)
                click.echo("\n---\n")
                click.echo(f"Command: {prefix}{name}\n")
                click.echo(sub.get_help(sub_ctx))
                _walk(sub, sub_ctx, f"{prefix}{name} ")

    _walk(cmd, ctx, "")
    ctx.exit(0)


def _emit_json(payload) -> None:
    click.echo(json.dumps(payload, indent=2, default=str))


# =========================================================================
# guidelines constants
# =========================================================================

_GUIDELINE_SECTIONS = ["abstract", "introduction", "methods", "discussion", "proofread"]


# =========================================================================
# compile constants + result printer
# =========================================================================

_ENGINE_CHOICES = click.Choice(["tectonic", "latexmk", "3pass"])


def _print_compile_result(result, as_json) -> int:
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if result.get("success"):
        path = result.get("pdf_path") or result.get("output_pdf")
        click.echo(f"PDF: {path}")
        return 0
    click.echo(f"Error: {result.get('error', 'Unknown error')}", err=True)
    if result.get("log"):
        click.echo(f"Log: {result['log'][-500:]}", err=True)
    return 1


# =========================================================================
# tables / figures / checks constants
# =========================================================================

_DOC_TYPE = click.Choice(["manuscript", "supplementary", "revision"])
_DOC_TYPE_RW = click.Choice(["manuscript", "supplementary"])


# EOF
