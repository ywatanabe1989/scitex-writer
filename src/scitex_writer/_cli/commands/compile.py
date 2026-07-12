#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/compile.py

"""compile command group (LaTeX domain — names preserved verbatim)."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .._core import main_group
from .._helpers import (
    _DOC_TYPE,
    _ENGINE_CHOICES,
    _emit_json,
    _print_compile_result,
)

# =========================================================================
# compile group  (LaTeX domain — names preserved verbatim)
# =========================================================================


@main_group.group("compile", invoke_without_command=True, hidden=True)
@click.pass_context
def compile_group(ctx):
    """Compile LaTeX documents to PDF (manuscript / supplementary / revision / content).

    \b
    Example:
        $ scitex-writer compile manuscript
        $ scitex-writer compile manuscript --draft
        $ scitex-writer compile supplementary
        $ scitex-writer compile revision --track-changes
        $ echo '\\section{Test}' | scitex-writer compile content
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@compile_group.command("manuscript")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("--draft", is_flag=True, default=False, help="Fast single-pass mode.")
@click.option("--no-figs", is_flag=True, default=False, help="Skip figures.")
@click.option("--no-tables", is_flag=True, default=False, help="Skip tables.")
@click.option("--no-diff", is_flag=True, default=False, help="Skip diff generation.")
@click.option("--engine", type=_ENGINE_CHOICES, default=None, help="LaTeX engine.")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Print actions, don't compile."
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def compile_manuscript(
    project, draft, no_figs, no_tables, no_diff, engine, dry_run, yes, as_json
):
    """Compile the main manuscript to PDF.

    \b
    Example:
        $ scitex-writer compile manuscript
        $ scitex-writer compile manuscript --draft --engine tectonic
    """
    from ... import compile as compile_mod

    project_path = Path(project).resolve()
    if not project_path.exists():
        click.echo(f"Error: Project not found: {project_path}", err=True)
        return 1
    if dry_run:
        msg = {
            "would_compile": "manuscript",
            "project": str(project_path),
            "draft": draft,
            "engine": engine,
        }
        if as_json:
            _emit_json(msg)
        else:
            click.echo(f"Would compile manuscript at {project_path} (engine={engine}).")
        return 0
    result = compile_mod.manuscript(
        str(project_path),
        draft=draft,
        no_figs=no_figs,
        no_tables=no_tables,
        no_diff=no_diff,
        engine=engine,
    )
    return _print_compile_result(result, as_json)


@compile_group.command("supplementary")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("--draft", is_flag=True, default=False, help="Fast single-pass mode.")
@click.option("--engine", type=_ENGINE_CHOICES, default=None, help="LaTeX engine.")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Print actions, don't compile."
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def compile_supplementary(project, draft, engine, dry_run, yes, as_json):
    """Compile supplementary materials to PDF.

    \b
    Example:
        $ scitex-writer compile supplementary
        $ scitex-writer compile supplementary --draft
    """
    from ... import compile as compile_mod

    project_path = Path(project).resolve()
    if not project_path.exists():
        click.echo(f"Error: Project not found: {project_path}", err=True)
        return 1
    if dry_run:
        if as_json:
            _emit_json({"would_compile": "supplementary", "project": str(project_path)})
        else:
            click.echo(f"Would compile supplementary at {project_path}.")
        return 0
    result = compile_mod.supplementary(str(project_path), draft=draft, engine=engine)
    return _print_compile_result(result, as_json)


@compile_group.command("revision")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option(
    "--track-changes", is_flag=True, default=False, help="Include track changes."
)
@click.option("--engine", type=_ENGINE_CHOICES, default=None, help="LaTeX engine.")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Print actions, don't compile."
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def compile_revision(project, track_changes, engine, dry_run, yes, as_json):
    """Compile a revision letter (response to reviewers) to PDF.

    \b
    Example:
        $ scitex-writer compile revision
        $ scitex-writer compile revision --track-changes
    """
    from ... import compile as compile_mod

    project_path = Path(project).resolve()
    if not project_path.exists():
        click.echo(f"Error: Project not found: {project_path}", err=True)
        return 1
    if dry_run:
        if as_json:
            _emit_json({"would_compile": "revision", "project": str(project_path)})
        else:
            click.echo(f"Would compile revision at {project_path}.")
        return 0
    result = compile_mod.revision(
        str(project_path), track_changes=track_changes, engine=engine
    )
    return _print_compile_result(result, as_json)


@compile_group.command("content")
@click.option("-f", "--file", "src_file", default=None, help="LaTeX file (or stdin).")
@click.option("-p", "--project", default=None, help="Project path for bib access.")
@click.option("-n", "--name", default="content", help="Output base name.")
@click.option(
    "-c",
    "--color-mode",
    type=click.Choice(["light", "dark", "sepia", "paper"]),
    default="light",
    help="Color mode (default: light).",
)
@click.option("-t", "--timeout", type=int, default=60, help="Timeout in seconds.")
@click.option("--keep-aux", is_flag=True, default=False, help="Keep auxiliary files.")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Print actions, don't compile."
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def compile_content(
    src_file, project, name, color_mode, timeout, keep_aux, dry_run, yes, as_json
):
    """Compile raw LaTeX content (file or stdin) to PDF with a color theme.

    \b
    Example:
        $ scitex-writer compile content -f intro.tex
        $ echo '\\section{Test}' | scitex-writer compile content --color-mode dark
    """
    from ... import compile as compile_mod

    if src_file:
        p = Path(src_file)
        if not p.exists():
            click.echo(f"Error: File not found: {p}", err=True)
            return 1
        latex = p.read_text(encoding="utf-8")
    else:
        latex = sys.stdin.read()

    project_dir = str(Path(project).resolve()) if project else None
    if dry_run:
        if as_json:
            _emit_json({"would_compile": "content", "name": name})
        else:
            click.echo(f"Would compile content (name={name}).")
        return 0
    result = compile_mod.content(
        latex,
        project_dir=project_dir,
        color_mode=color_mode,
        name=name,
        timeout=timeout,
        keep_aux=keep_aux,
    )
    return _print_compile_result(result, as_json)


# =========================================================================
# The two pipelines ported from the shell engine in slice 6. They live under
# `compile` (not as their own groups) because `diff` and `archive` are VERBS:
# they are leaves of a noun group, and this keeps CLI / Python API / MCP
# aligned -- `compile diff` <-> `sw.compile.diff` <-> `writer_compile_diff`.
# =========================================================================


@compile_group.command("diff")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE, default="manuscript")
@click.option(
    "--from",
    "diff_from",
    default=None,
    help="Commit-ish to diff FROM (default: the previous commit touching the tex).",
)
@click.option("--no-diff", is_flag=True, default=False, help="Skip the diff pipeline.")
@click.option(
    "--timeout",
    "timeout_sec",
    type=int,
    default=120,
    show_default=True,
    help="Bound on the latexmk run, in seconds.",
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def compile_diff(project, doc_type, diff_from, no_diff, timeout_sec, as_json):
    """Build the version-diff PDF (latexdiff markup vs the previous version).

    The pure-Python diff engine (port of process_diff.sh): reads the previous
    version of the compiled .tex from git, runs latexdiff, stamps a signature
    block, and compiles the result with latexmk. With NO previous version it FAILS
    rather than emitting an unmarked PDF that looks like "nothing changed".

    \b
    Example:
        $ scitex-writer compile diff
        $ scitex-writer compile diff --from v1.0 -t supplementary --json
    """
    from ... import compile as compile_api

    result = compile_api.diff(project, doc_type, no_diff, diff_from, timeout_sec)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result.get("success"):
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    if result["skipped"]:
        click.echo("Skipped the diff pipeline (--no-diff).")
        return 0
    click.echo(
        f"Diff {result['from_hash']} -> {result['to_hash']} "
        f"({result['pdf_bytes']} bytes) -> {result['diff_pdf']}"
    )
    return 0


@compile_group.command("archive")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE, default="manuscript")
@click.option(
    "--no-archive", is_flag=True, default=False, help="Skip the archive pipeline."
)
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't archive.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def compile_archive(project, doc_type, no_archive, dry_run, yes, as_json):
    """Snapshot the compiled outputs into the versions directory.

    The pure-Python archive engine (port of process_archive.sh): copies the
    compiled PDF/TeX and the diff PDF/TeX to <archive_dir>/<stem>_<timestamp>_
    <commit>.<ext>, plus an un-stamped "current" copy of each. A DIRTY working
    tree is skipped -- a snapshot stamped with a commit it does not hold is a lie.

    \b
    Example:
        $ scitex-writer compile archive
        $ scitex-writer compile archive --dry-run
    """
    from ... import compile as compile_api

    if dry_run:
        if as_json:
            _emit_json({"would_archive": doc_type, "project": project})
        else:
            click.echo(f"Would archive the compiled {doc_type} outputs.")
        return 0
    result = compile_api.archive(project, doc_type, no_archive)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result.get("success"):
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    if result["skipped"]:
        click.echo(f"Skipped: {result['skip_reason']}")
        return 0
    click.echo(f"Archive {result['archive_id']} -> {result['versions_dir']}")
    for entry in result["archived"]:
        click.echo(f"  {entry['source']} -> {entry['archived']}")
    return 0


# EOF
