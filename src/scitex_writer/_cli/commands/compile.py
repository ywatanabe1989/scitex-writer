#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/compile.py

"""compile command group (LaTeX domain — names preserved verbatim)."""

from __future__ import annotations

import sys
from pathlib import Path

import click

from .._core import main_group
from .._helpers import _ENGINE_CHOICES, _emit_json, _print_compile_result

# =========================================================================
# compile group  (LaTeX domain — names preserved verbatim)
# =========================================================================


@main_group.group("compile", invoke_without_command=True)
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


# EOF
