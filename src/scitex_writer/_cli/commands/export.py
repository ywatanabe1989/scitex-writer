#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/export.py

"""export command group (submission bundles — arXiv/journal-ready)."""

from __future__ import annotations

from pathlib import Path

import click

from .._core import main_group
from .._helpers import _emit_json

# =========================================================================
# export group
# =========================================================================


@main_group.group("export", invoke_without_command=True, hidden=True)
@click.pass_context
def export_group(ctx):
    """Export manuscript for submission (arXiv/journal-ready bundles).

    \b
    Example:
        $ scitex-writer export manuscript
        $ scitex-writer export manuscript --format arxiv
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@export_group.command("manuscript")
@click.argument("project", default=".", required=False)
@click.option("--output-dir", default=None, help="Output directory.")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["arxiv"]),
    default="arxiv",
    help="Export format (default: arxiv).",
)
@click.option(
    "--dry-run", is_flag=True, default=False, help="Print actions, don't write."
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def export_manuscript(project, output_dir, fmt, dry_run, yes, as_json):
    """Export the manuscript as an arXiv-ready tarball.

    \b
    Example:
        $ scitex-writer export manuscript
        $ scitex-writer export manuscript . --output-dir build/
    """
    from ... import export as export_mod

    project_path = Path(project).resolve()
    if not project_path.exists():
        click.echo(f"Error: Project not found: {project_path}", err=True)
        return 1
    if dry_run:
        if as_json:
            _emit_json({"would_export": "manuscript", "format": fmt})
        else:
            click.echo(f"Would export {project_path} as {fmt}.")
        return 0
    result = export_mod.manuscript(str(project_path), output_dir=output_dir, format=fmt)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if result["success"]:
        click.echo(f"Tarball: {result['tarball_path']}")
        return 0
    click.echo(f"Error: {result['error']}", err=True)
    return 1


# EOF
