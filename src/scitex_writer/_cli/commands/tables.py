#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/tables.py

"""tables command group (CSV-backed LaTeX tables)."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .._core import main_group
from .._helpers import _DOC_TYPE, _DOC_TYPE_RW, _emit_json

# =========================================================================
# tables group
# =========================================================================


@main_group.group("tables", invoke_without_command=True)
@click.pass_context
def tables_group(ctx):
    """Table management (CSV-backed LaTeX tables).

    \b
    Example:
        $ scitex-writer tables list
        $ scitex-writer tables add results data.csv "Results summary"
        $ scitex-writer tables render
        $ scitex-writer tables archive results
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@tables_group.command("list")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE, default="manuscript")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def tables_list(project, doc_type, as_json):
    """List all tables registered for the manuscript or supplementary.

    \b
    Example:
        $ scitex-writer tables list
        $ scitex-writer tables list -t supplementary --json
    """
    from ... import tables

    result = tables.list(project, doc_type)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(f"# Tables ({result['count']})\n")
    click.echo("| Name | CSV | Caption |")
    click.echo("|------|-----|---------|")
    for t in result["tables"]:
        has_cap = "yes" if t["has_caption"] else ""
        click.echo(f"| {t['name']} | yes | {has_cap} |")
    return 0


@tables_group.command("add")
@click.argument("name")
@click.argument("csv_src")
@click.argument("caption")
@click.option("-l", "--label", default=None, help="LaTeX label (default: tab:<name>).")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE_RW, default="manuscript")
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't write.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def tables_add(name, csv_src, caption, label, project, doc_type, dry_run, yes, as_json):
    """Add a table from CSV content, file path, or '-' (stdin).

    \b
    Example:
        $ scitex-writer tables add results data.csv "Results summary"
        $ cat data.csv | scitex-writer tables add results - "Results"
    """
    from ... import tables

    if csv_src == "-":
        csv_text = sys.stdin.read()
    else:
        p = Path(csv_src)
        csv_text = p.read_text(encoding="utf-8") if p.exists() else csv_src
    if dry_run:
        if as_json:
            _emit_json({"would_add_table": name})
        else:
            click.echo(f"Would add table {name}.")
        return 0
    result = tables.add(project, name, csv_text, caption, label, doc_type)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(f"Added table: {name}")
    click.echo(f"  CSV:     {result['csv_path']}")
    click.echo(f"  Caption: {result['caption_path']}")
    click.echo(f"  Label:   {result['label']}")
    return 0


@tables_group.command("render")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE, default="manuscript")
@click.option(
    "--no-tables", is_flag=True, default=False, help="Skip all table processing."
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def tables_render(project, doc_type, no_tables, as_json):
    """Render every CSV table to LaTeX and gather them into FINAL.tex.

    The pure-Python table engine (port of process_tables.sh): refreshes CSVs from
    newer Excel sources, writes a default caption where none exists, renders each
    NN_*.csv through the single pandas backend, and gathers the results. With no
    tables it emits a comment-only fallback header (never a placeholder float).

    \b
    Example:
        $ scitex-writer tables render
        $ scitex-writer tables render -t supplementary --json
    """
    from ... import tables

    result = tables.render(project, doc_type, no_tables)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result.get("success"):
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    if result["skipped"]:
        click.echo("Skipped all table processing (--no-tables).")
        return 0
    if result["fallback_header"]:
        click.echo("No tables found: emitted comment-only fallback header.")
        return 0
    click.echo(
        f"Compiled {result['tables_compiled']} tables "
        f"(captions_created={result['captions_created']}, "
        f"xlsx_converted={result['xlsx_converted']}) -> {result['compiled_file']}"
    )
    return 0


@tables_group.command("remove")
@click.argument("name")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE_RW, default="manuscript")
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't remove.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def tables_remove(name, project, doc_type, dry_run, yes, as_json):
    """Permanently delete a table from the project.

    \b
    Example:
        $ scitex-writer tables remove results
        $ scitex-writer tables remove results --dry-run
    """
    from ... import tables

    if dry_run:
        if as_json:
            _emit_json({"would_remove_table": name})
        else:
            click.echo(f"Would remove table {name}.")
        return 0
    if not yes:
        click.echo(f"Refusing to remove table {name} without --yes/-y.", err=True)
        raise SystemExit(2)
    result = tables.remove(project, name, doc_type)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    click.echo(f"Removed: {', '.join(result['removed'])}")
    return 0


@tables_group.command("archive")
@click.argument("name")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE_RW, default="manuscript")
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't move.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def tables_archive(name, project, doc_type, dry_run, yes, as_json):
    """Move a table to legacy/ instead of deleting it.

    \b
    Example:
        $ scitex-writer tables archive results
    """
    from ... import tables

    if dry_run:
        if as_json:
            _emit_json({"would_archive_table": name})
        else:
            click.echo(f"Would archive table {name}.")
        return 0
    result = tables.archive(project, name, doc_type)
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
