#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/gui.py

"""launch-gui command (browser-based editor)."""

from __future__ import annotations

from pathlib import Path

import click

from .._core import main_group
from .._helpers import _emit_json

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
        from ..._django._server import run as _run_editor

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


# EOF
