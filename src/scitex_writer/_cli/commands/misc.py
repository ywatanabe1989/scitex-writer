#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/misc.py

"""Top-level convenience commands: list-python-apis and show-usage."""

from __future__ import annotations

import click

from .._core import main_group
from .._helpers import _DOC_TYPE, _emit_json


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
    from ..introspect import cmd_list_python_apis

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
    from ..._usage import get_usage

    text = get_usage()
    if as_json:
        _emit_json({"usage": text})
    else:
        click.echo(text)
    return 0


# =========================================================================
# clean-artifacts (pure-Python port of scripts/shell/modules/cleanup.sh)
# =========================================================================


@main_group.command("clean-artifacts")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE, default="manuscript")
@click.option("--dry-run", is_flag=True, default=False, help="Preview, don't touch.")
@click.option("--yes", "-y", is_flag=True, default=False, help="Skip confirmations.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def clean_artifacts(project, doc_type, dry_run, yes, as_json):
    """Sweep LaTeX build artefacts (bak, Emacs temp, aux/log, versioned).

    Removes ``*bak*`` and Emacs temp (``#*#``) files recursively, moves
    top-level aux/log files into the project's ``doc_log_dir``, removes
    ``progress.log`` files, and removes versioned ``*_v*.pdf`` / ``*_v*.tex``
    files -- never touching anything outside the project root. This deletes
    files, so it refuses to run without --yes/-y (use --dry-run to preview).

    \b
    Example:
        $ scitex-writer clean-artifacts --dry-run
        $ scitex-writer clean-artifacts -t supplementary --yes
        $ scitex-writer clean-artifacts --yes --json
    """
    from ... import cleanup

    if not dry_run and not yes:
        click.echo(
            "Refusing to delete build artefacts without --yes/-y "
            "(use --dry-run to preview).",
            err=True,
        )
        raise SystemExit(2)

    result = cleanup.run(project, doc_type=doc_type, dry_run=dry_run)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result.get("success"):
        click.echo(result.get("error", "cleanup failed"), err=True)
        return 1
    prefix = "Would clean" if result.get("dry_run") else "Cleaned"
    click.echo(
        f"{prefix}: "
        f"bak={result['bak_removed']}, emacs={result['emacs_removed']}, "
        f"aux_moved={result['aux_moved']}, progress={result['progress_removed']}, "
        f"versioned={result['versioned_removed']} -> log_dir {result['log_dir']}"
    )
    return 0


# EOF
