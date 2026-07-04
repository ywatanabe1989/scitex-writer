#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/project.py

"""update-project command (update engine files in a project)."""

from __future__ import annotations

from pathlib import Path

import click

from .._core import main_group
from .._helpers import _emit_json

# =========================================================================
# update (mutating top-level — needs object; keep `update` as alias via shim)
# =========================================================================


@main_group.command("update-project")
@click.argument("project", default=".", required=False)
@click.option("--branch", default=None, help="Pull from a specific template branch.")
@click.option("--tag", default=None, help="Pull from a specific template tag/version.")
@click.option(
    "--dry-run", is_flag=True, default=False, help="Preview only (this is the default)."
)
@click.option("--force", is_flag=True, default=False, help="Skip git safety check.")
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="Apply the update (default is a safe preview).",
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def update_project(project, branch, tag, dry_run, force, yes, as_json):
    """Update engine files in a scitex-writer project, preserving user content.

    \b
    Example:
        $ scitex-writer update-project
        $ scitex-writer update-project ~/proj/my-paper --dry-run
        $ scitex-writer update-project --tag v2.8.0
    """
    from ... import update

    project_path = Path(project).resolve()
    if not project_path.exists():
        click.echo(f"Error: Project not found: {project_path}", err=True)
        return 1
    # Safe by default: preview unless --yes is given (--dry-run forces preview).
    preview = dry_run or not yes
    result = update.project(
        str(project_path), branch=branch, tag=tag, dry_run=preview, force=force
    )
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    if not result["success"]:
        click.echo(f"Error: {result['error']}", err=True)
        return 1
    for w in result.get("warnings", []):
        click.echo(f"Warning: {w}", err=True)
    mode = " (preview)" if preview else ""
    click.echo(f"\nSciTeX Writer Update{mode}")
    click.echo(f"Template version: {result.get('version', 'unknown')}")
    click.echo(f"Project: {project_path}\n")
    modified = result.get("modified", [])
    added = result.get("added", [])
    unchanged = result.get("unchanged", [])
    if modified or added:
        click.echo("Engine files drifted from the template:" if preview else "Updated:")
        for p in modified:
            click.echo(f"  M {p} (drifted)")
        for p in added:
            click.echo(f"  A {p} (missing)")
        click.echo()
    click.echo(
        f"  {len(modified)} drifted, {len(added)} missing, {len(unchanged)} in sync"
    )
    if result.get("backup_dir"):
        click.echo(f"\n  Backup: {result['backup_dir']}")
    if preview and (modified or added):
        click.echo(
            "\nPreview only — nothing changed. To apply (a timestamped backup is "
            f"made first):\n  scitex-writer update-project {project} --yes"
        )
    return 0


# EOF
