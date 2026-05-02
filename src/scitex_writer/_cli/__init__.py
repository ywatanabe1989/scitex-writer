#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/__init__.py

"""scitex-writer CLI (Click-based, audit-compliant).

Subcommand groups:
    mcp        - MCP server commands
    guidelines - IMRAD writing guidelines (abstract/introduction/methods/...)
    prompts    - Action prompts (Asta)
    compile    - Compile LaTeX to PDF (manuscript/supplementary/revision/content)
    export     - Export manuscript for submission
    bib        - Bibliography management
    tables     - Table management
    figures    - Figure management
    gui        - Browser-based editor
    update     - Update engine files in a project
    migration  - Import/export Overleaf
    introspect - Python package introspection

Top-level convenience commands:
    list-python-apis   - alias for `introspect api scitex_writer`
    show-usage         - print the long usage guide

All LaTeX-domain command names (`compile manuscript`, `bib`, `figures`,
`tables`, etc.) are preserved verbatim — they are the canonical vocabulary
of the package and are referenced from skills, READMEs, and external docs.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from .. import __version__
from .._usage import get_usage

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
# Root group
# =========================================================================


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option(__version__, "-V", "--version", prog_name="scitex-writer")
@click.option(
    "--help-recursive",
    is_flag=True,
    is_eager=True,
    expose_value=False,
    callback=_print_help_recursive,
    help="Show help for the root command and every subcommand.",
)
@click.option(
    "--json",
    "as_json",
    is_flag=True,
    default=False,
    help="Emit machine-readable JSON output where supported.",
)
@click.pass_context
def main_group(ctx, as_json):
    """SciTeX Writer - LaTeX manuscript compilation system with MCP server.

    \b
    Configuration precedence (highest -> lowest):
      1. Explicit CLI flags
      2. ./config.yaml (project-local)
      3. $SCITEX_WRITER_CONFIG (path to a YAML file)
      4. ~/.scitex/writer/config.yaml (user-wide)
      5. Built-in defaults

    \b
    Example:
        $ scitex-writer compile manuscript
        $ scitex-writer bib list-entries --json
        $ scitex-writer mcp list-tools -vv
    """
    ctx.ensure_object(dict)
    ctx.obj["as_json"] = as_json
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# =========================================================================
# mcp group
# =========================================================================


@main_group.group("mcp", invoke_without_command=True)
@click.pass_context
def mcp_group(ctx):
    """MCP (Model Context Protocol) server commands.

    \b
    Example:
        $ scitex-writer mcp start
        $ scitex-writer mcp list-tools -vv
        $ scitex-writer mcp doctor
        $ scitex-writer mcp installation
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@mcp_group.command("show-installation")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def mcp_show_installation(as_json):
    """Show Claude Desktop installation guide for the scitex-writer MCP server.

    \b
    Example:
        $ scitex-writer mcp show-installation
    """
    from .mcp import cmd_config

    return cmd_config()


@mcp_group.command("list-tools")
@click.option(
    "-v", "--verbose", count=True, help="Verbosity: -v desc, -vv +params, -vvv full."
)
@click.option("-c", "--compact", is_flag=True, help="Compact signatures (single line).")
@click.option(
    "-m",
    "--module",
    "module_filter",
    default=None,
    help="Filter by module (bib/compile/figures/tables/project/guidelines/prompts/general).",
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON.")
def mcp_list_tools(verbose, compact, module_filter, as_json):
    """List all available MCP tools exposed by scitex-writer.

    \b
    Example:
        $ scitex-writer mcp list-tools
        $ scitex-writer mcp list-tools -vv
        $ scitex-writer mcp list-tools --module bib --json
    """
    from .mcp import cmd_list_tools

    return cmd_list_tools(
        verbose=verbose, compact=compact, module=module_filter, as_json=as_json
    )


@mcp_group.command("doctor")
@click.option("--json", "as_json", is_flag=True, default=False, help="Output as JSON.")
def mcp_doctor(as_json):
    """Check MCP server health and configuration.

    \b
    Example:
        $ scitex-writer mcp doctor
    """
    from .mcp import cmd_doctor

    return cmd_doctor()


@mcp_group.command("start")
@click.option(
    "-t",
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport: stdio (default) or sse.",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Print what would happen without starting the server.",
)
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def mcp_start(transport, dry_run, yes, as_json):
    """Start the scitex-writer MCP server.

    \b
    Example:
        $ scitex-writer mcp start
        $ scitex-writer mcp start --transport sse
        $ scitex-writer mcp start --dry-run
    """
    if dry_run:
        msg = {"would_start": True, "transport": transport}
        if as_json:
            _emit_json(msg)
        else:
            click.echo(f"Would start MCP server (transport={transport}).")
        return 0
    from .mcp import cmd_start

    return cmd_start(transport=transport)


# =========================================================================
# guidelines group
# =========================================================================


_GUIDELINE_SECTIONS = ["abstract", "introduction", "methods", "discussion", "proofread"]


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
        from ..guidelines import _get_source, build, get

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
    from ..prompts import generate_asta

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
    from .. import compile as compile_mod

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
    from .. import compile as compile_mod

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
    from .. import compile as compile_mod

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
    from .. import compile as compile_mod

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
    from .. import export as export_mod

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
    from .. import bib

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
    from .. import bib

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
    from .. import bib

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
    from .. import bib

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
    from .. import bib

    if dry_run:
        if as_json:
            _emit_json({"would_remove": key})
        else:
            click.echo(f"Would remove entry: {key}")
        return 0
    if not yes and not click.confirm(f"Remove entry {key}?", default=True):
        click.echo("Aborted.")
        return 1
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
    from .. import bib

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


# =========================================================================
# tables group
# =========================================================================


_DOC_TYPE = click.Choice(["manuscript", "supplementary", "revision"])
_DOC_TYPE_RW = click.Choice(["manuscript", "supplementary"])


@main_group.group("tables", invoke_without_command=True)
@click.pass_context
def tables_group(ctx):
    """Table management (CSV-backed LaTeX tables).

    \b
    Example:
        $ scitex-writer tables list
        $ scitex-writer tables add results data.csv "Results summary"
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
    from .. import tables

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
    from .. import tables

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
    from .. import tables

    if dry_run:
        if as_json:
            _emit_json({"would_remove_table": name})
        else:
            click.echo(f"Would remove table {name}.")
        return 0
    if not yes and not click.confirm(f"Remove table {name}?", default=True):
        click.echo("Aborted.")
        return 1
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
    from .. import tables

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
    from .. import figures

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
    from .. import figures

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
    from .. import figures

    if dry_run:
        if as_json:
            _emit_json({"would_remove_figure": name})
        else:
            click.echo(f"Would remove figure {name}.")
        return 0
    if not yes and not click.confirm(f"Remove figure {name}?", default=True):
        click.echo("Aborted.")
        return 1
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
    from .. import figures

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


# =========================================================================
# gui (renamed -> launch-gui at top level for §1, alias `gui` preserved)
# =========================================================================


@main_group.command("launch-gui")
@click.argument("project", default=".", required=False)
@click.option("--port", type=int, default=5050, help="Server port (default: 5050).")
@click.option("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1).")
@click.option("--no-browser", is_flag=True, default=False, help="Don't open browser.")
@click.option(
    "--desktop",
    is_flag=True,
    default=False,
    help="Launch as desktop window (requires pywebview).",
)
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't launch.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def launch_gui(project, port, host, no_browser, desktop, dry_run, yes, as_json):
    """Launch the browser-based editor for a scitex-writer project.

    \b
    Example:
        $ scitex-writer launch-gui
        $ scitex-writer launch-gui ~/proj/my-paper --port 5051
    """
    project_path = Path(project).resolve()
    if not project_path.exists():
        click.echo(f"Error: Project not found: {project_path}", err=True)
        return 1
    if dry_run:
        if as_json:
            _emit_json({"would_launch": True, "host": host, "port": port})
        else:
            click.echo(f"Would launch editor at http://{host}:{port}.")
        return 0
    try:
        from .._django._server import run as _run_editor

        _run_editor(
            project_dir=str(project_path),
            port=port,
            host=host,
            open_browser=not no_browser,
            desktop=desktop,
        )
    except ImportError as e:
        click.echo(
            f"Error: {e}\nInstall with: pip install scitex-writer[editor]", err=True
        )
        return 1
    return 0


# =========================================================================
# update (mutating top-level — needs object; keep `update` as alias via shim)
# =========================================================================


@main_group.command("update-project")
@click.argument("project", default=".", required=False)
@click.option("--branch", default=None, help="Pull from a specific template branch.")
@click.option("--tag", default=None, help="Pull from a specific template tag/version.")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Show what would be updated."
)
@click.option("--force", is_flag=True, default=False, help="Skip git safety check.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def update_project(project, branch, tag, dry_run, force, yes, as_json):
    """Update engine files in a scitex-writer project, preserving user content.

    \b
    Example:
        $ scitex-writer update-project
        $ scitex-writer update-project ~/proj/my-paper --dry-run
        $ scitex-writer update-project --tag v2.8.0
    """
    from .. import update

    project_path = Path(project).resolve()
    if not project_path.exists():
        click.echo(f"Error: Project not found: {project_path}", err=True)
        return 1
    result = update.project(
        str(project_path), branch=branch, tag=tag, dry_run=dry_run, force=force
    )
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    for w in result.get("warnings", []):
        click.echo(f"Warning: {w}", err=True)
    mode = " (dry run)" if dry_run else ""
    click.echo(f"\nSciTeX Writer Update{mode}")
    click.echo(f"Package version: {result.get('version', 'unknown')}")
    click.echo(f"Project: {project_path}\n")
    modified = result.get("modified", [])
    added = result.get("added", [])
    unchanged = result.get("unchanged", [])
    if modified or added or unchanged:
        click.echo("Files to update:" if dry_run else "Files updated:")
        for p in modified:
            click.echo(f"  M {p} (modified)")
        for p in added:
            click.echo(f"  A {p} (new)")
        for p in unchanged:
            click.echo(f"  = {p} (unchanged)")
        click.echo()
    click.echo(
        f"  {len(modified)} modified, {len(added)} new, {len(unchanged)} unchanged"
    )
    if result.get("backup_dir"):
        click.echo(f"\n  Backup: {result['backup_dir']}")
    if dry_run:
        click.echo("\nRun without --dry-run to apply changes.")
    return 0


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
    from .. import migration

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
    from .. import migration

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


# =========================================================================
# introspect group  (api -> show-api at leaf for §1; old name kept as alias)
# =========================================================================


@main_group.group("introspect", invoke_without_command=True, hidden=True)
@click.pass_context
def introspect_group(ctx):
    """Python package introspection utilities.

    \b
    Example:
        $ scitex-writer introspect show-api scitex_writer
        $ scitex-writer introspect show-api scitex_writer -v
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@introspect_group.command("show-api")
@click.argument("dotted_path")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc.")
@click.option(
    "-d", "--max-depth", type=int, default=5, help="Max recursion depth (default: 5)."
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def introspect_show_api(dotted_path, verbose, max_depth, as_json):
    """Print the public API tree of a Python package or module.

    \b
    Example:
        $ scitex-writer introspect show-api scitex_writer
        $ scitex-writer introspect show-api scitex_writer.bib -v
        $ scitex-writer introspect show-api scitex_writer --json
    """
    from .introspect import cmd_api

    return cmd_api(dotted_path, verbose=verbose, max_depth=max_depth, as_json=as_json)


@main_group.command("list-python-apis")
@click.option("-v", "--verbose", count=True, help="Verbosity: -v +doc, -vv full doc.")
@click.option(
    "-d", "--max-depth", type=int, default=5, help="Max recursion depth (default: 5)."
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def list_python_apis(verbose, max_depth, as_json):
    """List the public Python API surface of scitex_writer.

    \b
    Example:
        $ scitex-writer list-python-apis
        $ scitex-writer list-python-apis -v
        $ scitex-writer list-python-apis --json
    """
    from .introspect import cmd_list_python_apis

    return cmd_list_python_apis(verbose=verbose, max_depth=max_depth, as_json=as_json)


# =========================================================================
# show-usage (renamed from `usage` to satisfy §1 verb-leaf)
# =========================================================================


@main_group.command("show-usage")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def show_usage(as_json):
    """Print the long-form usage guide for scitex-writer projects.

    \b
    Example:
        $ scitex-writer show-usage
        $ scitex-writer show-usage --json
    """
    text = get_usage()
    if as_json:
        _emit_json({"usage": text})
    else:
        click.echo(text)
    return 0


# =========================================================================
# §1 flat top-level aliases — verb-shaped groups (compile/export/introspect)
# are kept as hidden back-compat shims; the canonical forms are flat
# `<verb>-<noun>` commands at the top level. Same Click Command objects are
# attached to two parents, so behaviour is identical.
# =========================================================================


def _alias_top_level(cmd: click.Command, new_name: str) -> None:
    """Re-attach a Click command at the top level under a flat verb-noun name.

    The `.name` attribute is updated so audit traversal (which classifies by
    `cmd.name`, not by the parent's commands-dict key) sees the canonical
    `<verb>-<noun>` form. The original group registration is preserved on
    the hidden back-compat group.
    """
    import copy as _copy

    clone = _copy.copy(cmd)
    clone.name = new_name
    main_group.add_command(clone, name=new_name)


_alias_top_level(compile_manuscript, "compile-manuscript")
_alias_top_level(compile_supplementary, "compile-supplementary")
_alias_top_level(compile_revision, "compile-revision")
_alias_top_level(compile_content, "compile-content")
_alias_top_level(export_manuscript, "export-manuscript")
_alias_top_level(introspect_show_api, "show-api")


# =========================================================================
# Optional: docs / skills subcommands (from scitex_dev) — mounted if available
# =========================================================================


def _mount_optional_subcommands():
    """Mount scitex_dev `docs` and `skills` subcommands if available.

    These come from scitex_dev as Click groups; if present, attach them to
    main_group so they show up under `scitex-writer docs ...` / `skills ...`.
    """
    try:
        from scitex_dev.cli import register_docs_subcommand_click

        register_docs_subcommand_click(main_group, package="scitex-writer")
    except Exception:
        pass
    try:
        from scitex_dev.cli import register_skills_subcommand_click

        register_skills_subcommand_click(main_group, package="scitex-writer")
    except Exception:
        pass


_mount_optional_subcommands()


# =========================================================================
# Backward-compat shim: translate deprecated argv tokens to canonical names
# =========================================================================


_TOP_RENAMES = {
    "gui": "launch-gui",
    "update": "update-project",
    "usage": "show-usage",
}

# old `<verb> <noun>` -> canonical flat `<verb>-<noun>`
# (groups are kept as hidden back-compat shims; this rewrite is so users
# typing the old form land on the canonical command path so help/usage
# reflects current naming).
_FLAT_RENAMES = {
    ("compile", "manuscript"): "compile-manuscript",
    ("compile", "supplementary"): "compile-supplementary",
    ("compile", "revision"): "compile-revision",
    ("compile", "content"): "compile-content",
    ("export", "manuscript"): "export-manuscript",
    ("introspect", "api"): "show-api",
    ("introspect", "show-api"): "show-api",
}

# old `<group> <leaf>` -> `<group> <new-leaf>` (group preserved)
_LEAF_RENAMES = {
    ("mcp", "installation"): "show-installation",
    ("guidelines", "introduction"): "show-introduction",
    ("guidelines", "methods"): "show-methods",
    ("guidelines", "discussion"): "show-discussion",
    ("guidelines", "abstract"): "show-abstract",
    ("guidelines", "proofread"): "show-proofread",
    ("prompts", "asta"): "show-asta",
}


def _rewrite_argv(argv):
    """Translate deprecated subcommand names to canonical Click names."""
    if not argv:
        return argv
    i = 0
    while i < len(argv) and argv[i].startswith("-"):
        i += 1
    if i >= len(argv):
        return argv
    sub = argv[i]
    if sub in _TOP_RENAMES:
        argv = argv[:i] + [_TOP_RENAMES[sub]] + argv[i + 1 :]
        return argv
    if i + 1 < len(argv):
        pair = (sub, argv[i + 1])
        if pair in _FLAT_RENAMES:
            return argv[:i] + [_FLAT_RENAMES[pair]] + argv[i + 2 :]
        if pair in _LEAF_RENAMES:
            return argv[: i + 1] + [_LEAF_RENAMES[pair]] + argv[i + 2 :]
    return argv


# =========================================================================
# Entry point
# =========================================================================


def main(argv: list = None) -> int:
    """Entry point. Returns exit code (0 on success).

    Wraps Click so callers (and tests) that pass argv lists keep working.
    Translates deprecated subcommand names to canonical Click names.
    """
    raw = list(sys.argv[1:]) if argv is None else list(argv)
    raw = _rewrite_argv(raw)
    try:
        result = main_group.main(
            args=raw, prog_name="scitex-writer", standalone_mode=False
        )
        # Click commands may return an int exit code from their callback
        if isinstance(result, int):
            return result
        return 0
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else (0 if e.code is None else 1)
        return code
    except click.exceptions.UsageError as e:
        click.echo(f"Error: {e.format_message()}", err=True)
        return 2
    except click.exceptions.Abort:
        click.echo("Aborted.", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())


# EOF
