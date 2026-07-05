#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/bib.py

"""bib command group (bibliography management)."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .._core import main_group
from .._helpers import _emit_json

# =========================================================================
# bib group
# =========================================================================


@main_group.group("bib", invoke_without_command=True)
@click.pass_context
def bib_group(ctx):
    """Bibliography management (.bib files and entries).

    \b
    Example:
        $ scitex-writer bib list-files
        $ scitex-writer bib list-entries
        $ scitex-writer bib get Smith2024
        $ scitex-writer bib add '@article{...}'
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@bib_group.command("list-files")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def bib_list_files(project, as_json):
    """List bibliography (.bib) files in the project.

    \b
    Example:
        $ scitex-writer bib list-files
        $ scitex-writer bib list-files --json
    """
    from ... import bib

    result = bib.list_files(project)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(f"# Bibliography Files ({result['count']})\n")
    click.echo("| File | Entries | Merged |")
    click.echo("|------|---------|--------|")
    for f in result["bibfiles"]:
        merged = "yes" if f["is_merged"] else ""
        click.echo(f"| {f['name']} | {f['entry_count']} | {merged} |")
    return 0


@bib_group.command("list-entries")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-f", "--file", "bibfile", default=None, help="Specific .bib file.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def bib_list_entries(project, bibfile, as_json):
    """List bibliography entries across one or all .bib files.

    \b
    Example:
        $ scitex-writer bib list-entries
        $ scitex-writer bib list-entries -f custom.bib --json
    """
    from ... import bib

    result = bib.list_entries(project, bibfile)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(f"# Bibliography Entries ({result['count']})\n")
    click.echo("| Key | Type | File |")
    click.echo("|-----|------|------|")
    for e in result["entries"]:
        click.echo(f"| {e['citation_key']} | {e['entry_type']} | {e['bibfile']} |")
    return 0


@bib_group.command("get")
@click.argument("key")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def bib_get(key, project, as_json):
    """Print a single bibliography entry by citation key.

    \b
    Example:
        $ scitex-writer bib get Smith2024
        $ scitex-writer bib get Smith2024 --json
    """
    from ... import bib

    result = bib.get(project, key)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(result["entry"])
    return 0


@bib_group.command("add")
@click.argument("entry")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-f", "--file", "bibfile", default="custom.bib", help="Target .bib file.")
@click.option(
    "--allow-duplicates", is_flag=True, default=False, help="Allow duplicate keys."
)
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't write.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def bib_add(entry, project, bibfile, allow_duplicates, dry_run, yes, as_json):
    """Add a bibliography entry (BibTeX text, file path, or '-' for stdin).

    \b
    Example:
        $ scitex-writer bib add '@article{Foo,...}'
        $ scitex-writer bib add entry.bib -f custom.bib
        $ cat entry.bib | scitex-writer bib add -
    """
    from ... import bib

    if entry == "-":
        text = sys.stdin.read()
    elif entry.startswith("@"):
        text = entry
    else:
        p = Path(entry)
        text = p.read_text(encoding="utf-8") if p.exists() else entry

    if dry_run:
        if as_json:
            _emit_json({"would_add": True, "bibfile": bibfile})
        else:
            click.echo(f"Would add entry to {bibfile}.")
        return 0
    result = bib.add(project, text, bibfile, not allow_duplicates)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(f"Added: {result['citation_key']} to {result['bibfile']}")
    return 0


@bib_group.command("remove")
@click.argument("key")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't remove.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def bib_remove(key, project, dry_run, yes, as_json):
    """Remove a bibliography entry by citation key.

    \b
    Example:
        $ scitex-writer bib remove Smith2024
        $ scitex-writer bib remove Smith2024 --dry-run
    """
    from ... import bib

    if dry_run:
        if as_json:
            _emit_json({"would_remove": key})
        else:
            click.echo(f"Would remove entry: {key}")
        return 0
    if not yes:
        click.echo(f"Refusing to remove entry {key} without --yes/-y.", err=True)
        raise SystemExit(2)
    result = bib.remove(project, key)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(f"Removed: {result['citation_key']} from {result['removed_from']}")
    return 0


@bib_group.command("merge")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-o", "--output", default="bibliography.bib", help="Merged output file.")
@click.option(
    "--keep-duplicates", is_flag=True, default=False, help="Keep duplicate entries."
)
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't write.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def bib_merge(project, output, keep_duplicates, dry_run, yes, as_json):
    """Merge all .bib files in the project into one (deduplicated by default).

    \b
    Example:
        $ scitex-writer bib merge
        $ scitex-writer bib merge -o merged.bib --keep-duplicates
    """
    from ... import bib

    if dry_run:
        if as_json:
            _emit_json({"would_merge_to": output})
        else:
            click.echo(f"Would merge .bib files into {output}.")
        return 0
    result = bib.merge(project, output, not keep_duplicates)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(f"Merged {result['entry_count']} entries to {result['output_file']}")
    if result["duplicates_skipped"] > 0:
        click.echo(f"Skipped {result['duplicates_skipped']} duplicates")
    return 0


# EOF
