#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/figures.py

"""figures command group (image files + caption + label)."""

from __future__ import annotations

from pathlib import Path

import click

from .._core import main_group
from .._helpers import _DOC_TYPE_RW, _emit_json

# =========================================================================
# figures group
# =========================================================================


@main_group.group("figures", invoke_without_command=True)
@click.pass_context
def figures_group(ctx):
    """Figure management (image files + caption + label).

    \b
    Example:
        $ scitex-writer figures list
        $ scitex-writer figures add fig01 plot.png "Results plot"
        $ scitex-writer figures archive fig01
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@figures_group.command("list")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option(
    "-e", "--extensions", default=None, help="Extensions to filter (comma-separated)."
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def figures_list(project, extensions, as_json):
    """List all figures registered in the project.

    \b
    Example:
        $ scitex-writer figures list
        $ scitex-writer figures list -e png,pdf --json
    """
    from ... import figures

    exts = extensions.split(",") if extensions else None
    result = figures.list(project, exts)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(f"# Figures ({result['count']})\n")
    if result["figures"]:
        click.echo("| Name | Format | Caption |")
        click.echo("|------|--------|---------|")
        for f in result["figures"]:
            fmt = Path(f["path"]).suffix
            has_cap = "yes" if f.get("has_caption") else ""
            click.echo(f"| {f['name']} | {fmt} | {has_cap} |")
    return 0


@figures_group.command("add")
@click.argument("name")
@click.argument("image")
@click.argument("caption")
@click.option("-l", "--label", default=None, help="LaTeX label (default: fig:<name>).")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE_RW, default="manuscript")
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't write.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def figures_add(name, image, caption, label, project, doc_type, dry_run, yes, as_json):
    """Add a figure (image file + caption + label) to the project.

    \b
    Example:
        $ scitex-writer figures add fig01 plot.png "Results plot"
    """
    from ... import figures

    image_path = Path(image)
    if not image_path.exists():
        click.echo(f"Error: Image not found: {image_path}", err=True)
        return 1
    if dry_run:
        if as_json:
            _emit_json({"would_add_figure": name})
        else:
            click.echo(f"Would add figure {name} from {image_path}.")
        return 0
    result = figures.add(project, name, str(image_path), caption, label, doc_type)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(f"Added figure: {name}")
    click.echo(f"  Image:   {result['image_path']}")
    click.echo(f"  Caption: {result['caption_path']}")
    click.echo(f"  Label:   {result['label']}")
    return 0


@figures_group.command("remove")
@click.argument("name")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE_RW, default="manuscript")
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't remove.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def figures_remove(name, project, doc_type, dry_run, yes, as_json):
    """Permanently delete a figure from the project.

    \b
    Example:
        $ scitex-writer figures remove fig01
    """
    from ... import figures

    if dry_run:
        if as_json:
            _emit_json({"would_remove_figure": name})
        else:
            click.echo(f"Would remove figure {name}.")
        return 0
    if not yes:
        click.echo(f"Refusing to remove figure {name} without --yes/-y.", err=True)
        raise SystemExit(2)
    result = figures.remove(project, name, doc_type)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(f"Removed: {', '.join(result['removed'])}")
    return 0


@figures_group.command("archive")
@click.argument("name")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE_RW, default="manuscript")
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't move.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def figures_archive(name, project, doc_type, dry_run, yes, as_json):
    """Move a figure to legacy/ instead of deleting it.

    \b
    Example:
        $ scitex-writer figures archive fig01
    """
    from ... import figures

    if dry_run:
        if as_json:
            _emit_json({"would_archive_figure": name})
        else:
            click.echo(f"Would archive figure {name}.")
        return 0
    result = figures.archive(project, name, doc_type)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    for entry in result["archived"]:
        click.echo(f"Archived: {entry['from']} -> {entry['to']}")
    return 0


# EOF
