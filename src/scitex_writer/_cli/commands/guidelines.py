#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/guidelines.py

"""guidelines command group (IMRAD writing guidelines)."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .._core import main_group
from .._helpers import _GUIDELINE_SECTIONS, _emit_json

# =========================================================================
# guidelines group
# =========================================================================


@main_group.group("guidelines", invoke_without_command=True)
@click.pass_context
def guidelines_group(ctx):
    """IMRAD writing guidelines for scientific manuscripts.

    \b
    Example:
        $ scitex-writer guidelines list
        $ scitex-writer guidelines abstract
        $ scitex-writer guidelines abstract -d draft.tex
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@guidelines_group.command("list")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON.")
def guidelines_list(as_json):
    """List available IMRAD guideline sections.

    \b
    Example:
        $ scitex-writer guidelines list
        $ scitex-writer guidelines list --json
    """
    if as_json:
        _emit_json({"sections": _GUIDELINE_SECTIONS})
        return 0
    click.echo("Available sections:")
    for s in _GUIDELINE_SECTIONS:
        click.echo(f"  - {s}")
    return 0


def _make_guideline_cmd(section: str):
    @click.option(
        "-d",
        "--draft",
        default=None,
        help="Path to draft file (use '-' for stdin) - builds full prompt.",
    )
    @click.option(
        "-i", "--info", is_flag=True, default=False, help="Show guideline source info."
    )
    @click.option(
        "--json", "as_json", is_flag=True, default=False, help="Emit JSON envelope."
    )
    def _impl(draft, info, as_json):
        from ...guidelines import _get_source, build, get

        try:
            source = _get_source(section)
            if info and not as_json:
                click.echo(f"Section: {section}")
                click.echo(f"Source:  {source['source']}")
                click.echo(f"Path:    {source['path']}\n")

            if draft:
                if draft == "-":
                    draft_text = sys.stdin.read()
                else:
                    p = Path(draft)
                    if not p.exists():
                        click.echo(f"Error: Draft file not found: {p}", err=True)
                        return 1
                    draft_text = p.read_text(encoding="utf-8")
                output = build(section, draft_text)
            else:
                output = get(section)

            if as_json:
                _emit_json({"section": section, "source": source, "content": output})
            else:
                click.echo(output)
            return 0
        except (ValueError, FileNotFoundError) as e:
            click.echo(f"Error: {e}", err=True)
            return 1

    _impl.__name__ = f"guidelines_{section}"
    _impl.__doc__ = (
        f"Show or build the {section} writing guidelines.\n\n"
        f"\b\nExample:\n"
        f"    $ scitex-writer guidelines show-{section}\n"
        f"    $ scitex-writer guidelines show-{section} -d draft.tex\n"
        f"    $ scitex-writer guidelines show-{section} --json\n"
    )
    return _impl


for _sec in _GUIDELINE_SECTIONS:
    # Canonical: verb-leaf form (§1 compliant). Old `<section>` form is
    # transparently translated to `show-<section>` by `_rewrite_argv`.
    guidelines_group.command(f"show-{_sec}")(_make_guideline_cmd(_sec))


# EOF
