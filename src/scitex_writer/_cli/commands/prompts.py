#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/prompts.py

"""prompts command group (action prompts, Asta)."""

from __future__ import annotations

from pathlib import Path

import click

from .._core import main_group
from .._helpers import _emit_json

# =========================================================================
# prompts group
# =========================================================================


@main_group.group("prompts", invoke_without_command=True)
@click.pass_context
def prompts_group(ctx):
    """Action prompts for manuscript workflows.

    \b
    Example:
        $ scitex-writer prompts asta
        $ scitex-writer prompts asta -t coauthors
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@prompts_group.command("show-asta")
@click.option(
    "-t",
    "--type",
    "search_type",
    type=click.Choice(["related", "coauthors"]),
    default="related",
    help="Search type (related papers or potential co-authors).",
)
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-i", "--info", is_flag=True, default=False, help="Show search info.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def prompts_asta(search_type, project, info, as_json):
    """Generate an AI2 Asta search prompt from the current manuscript.

    \b
    Example:
        $ scitex-writer prompts asta
        $ scitex-writer prompts asta -t coauthors
        $ scitex-writer prompts asta --json
    """
    from ...prompts import generate_asta

    project_path = Path(project).resolve()
    if not project_path.exists():
        click.echo(f"Error: Project path not found: {project_path}", err=True)
        return 1
    result = generate_asta(project_path, search_type=search_type)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        for step in result.get("next_steps", []) or []:
            click.echo(f"  - {step}", err=True)
        return 1
    if info:
        click.echo(f"Search type: {result['search_type']}\n")
        click.echo("Next steps:")
        for step in result["next_steps"]:
            click.echo(f"  - {step}")
        click.echo("\n--- Generated Prompt ---\n")
    click.echo(result["prompt"])
    return 0


# EOF
