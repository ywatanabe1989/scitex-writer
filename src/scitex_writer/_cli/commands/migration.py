#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/migration.py

"""migration command group (import from / export to Overleaf)."""

from __future__ import annotations

import click

from .._core import main_group
from .._helpers import _emit_json

# =========================================================================
# migration group
# =========================================================================


@main_group.group("migration", invoke_without_command=True)
@click.pass_context
def migration_group(ctx):
    """Import from / export to external platforms (Overleaf).

    \b
    Example:
        $ scitex-writer migration import project.zip
        $ scitex-writer migration export . --output paper.zip
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@migration_group.command("import")
@click.argument("zip_path")
@click.option("-o", "--output", default=None, help="Output directory.")
@click.option("--name", default=None, help="Project name.")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Inspect ZIP without writing files."
)
@click.option(
    "--force", is_flag=True, default=False, help="Overwrite existing output dir."
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def migration_import(zip_path, output, name, dry_run, force, yes, as_json):
    """Import an Overleaf ZIP into a scitex-writer project.

    \b
    Example:
        $ scitex-writer migration import project.zip
        $ scitex-writer migration import project.zip --output ./my-paper
        $ scitex-writer migration import project.zip --dry-run
    """
    from ... import migration

    result = migration.from_overleaf(
        zip_path,
        output_dir=output,
        project_name=name,
        dry_run=dry_run,
        force=force,
    )
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    for w in result.get("warnings", []):
        click.echo(f"Warning: {w}", err=True)
    if dry_run:
        click.echo("Dry run - no files created.\n")
        report = result.get("mapping_report", {})
        if report.get("sections"):
            click.echo("Section mapping:")
            for section, files in report["sections"].items():
                click.echo(f"  {section}: {', '.join(files)}")
        if report.get("bib_files"):
            click.echo(f"\nBibliography: {', '.join(report['bib_files'])}")
        if report.get("images"):
            click.echo(f"Images: {len(report['images'])} file(s)")
        if report.get("unmapped_tex"):
            click.echo(f"Unmapped .tex: {', '.join(report['unmapped_tex'])}")
    click.echo(f"\n{result['message']}")
    return 0


@migration_group.command("export")
@click.argument("project", default=".", required=False)
@click.option("-o", "--output", default=None, help="Output ZIP path.")
@click.option(
    "--dry-run", is_flag=True, default=False, help="List files without writing ZIP."
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def migration_export(project, output, dry_run, yes, as_json):
    """Export a scitex-writer project as an Overleaf-compatible ZIP.

    \b
    Example:
        $ scitex-writer migration export
        $ scitex-writer migration export . --output paper.zip
        $ scitex-writer migration export --dry-run
    """
    from ... import migration

    result = migration.to_overleaf(project, output_path=output, dry_run=dry_run)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    for w in result.get("warnings", []):
        click.echo(f"Warning: {w}", err=True)
    if dry_run:
        click.echo("Dry run - no ZIP created.\n")
        for f in result.get("files_included", []):
            click.echo(f"  {f}")
    click.echo(f"\n{result['message']}")
    return 0


# EOF
