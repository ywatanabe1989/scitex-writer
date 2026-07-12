#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/gui.py

"""`gui` command group (browser-based editor): open / serve / status / stop.

Follows the fleet CLI canon (scitex-dev 19_gui-commands.md): one `gui`
group with fixed verbs. `serve` runs in the FOREGROUND; `open` auto-serves
a detached server when none is running, then opens the browser. Runtime
state lives in `_core/_gui_runtime` so status/stop work from a fresh shell.

`launch-gui` remains as a hidden warn-forward alias for one deprecation
cycle.
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

import click

from ..._core import _gui_runtime
from .._core import main_group
from .._helpers import _emit_json

DEFAULT_PORT = _gui_runtime.DEFAULT_PORT


def _resolve_project(project: str) -> Path | None:
    project_path = Path(project).resolve()
    if not project_path.exists():
        click.echo(f"Error: Project not found: {project_path}", err=True)
        return None
    return project_path


def _port_is_free(host: str, port: int) -> bool:
    """True when ``host:port`` can be bound right now."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


def _port_taken_message(host: str, port: int) -> str:
    """Explain who holds ``port`` and give paste-ready commands to fix it.

    This path means the port is held by something we do NOT track — an
    orphaned editor, or an unrelated process. `--force` only stops the editor
    recorded in our own runtime state, so it is deliberately NOT offered here:
    a hint that does not work is worse than no hint.
    """
    holder = _gui_runtime.port_holder(port)
    lines = [f"Error: port {port} is already in use on {host}."]
    if holder and holder.get("pid"):
        lines.append(f"Held by: {holder['name']} (pid {holder['pid']})")
    elif holder:
        lines.append("Held by: a process owned by another user.")
    else:
        lines.append("Held by: unknown (the listening process could not be read).")

    lines += ["", "Fix it with one of:"]
    lines.append(
        f"  scitex-writer gui serve --port {port + 1}   # serve on a free port"
    )
    if holder and holder.get("pid"):
        lines.append(f"  kill {holder['pid']}{' ' * 26}# stop it, then serve again")
    return "\n".join(lines)


@main_group.group("gui")
def gui_group():
    """Browser-based editor: open, serve, status, stop."""


# =========================================================================
# gui serve — run the server in the foreground
# =========================================================================


@gui_group.command("serve")
@click.argument("project", default=".", required=False)
@click.option(
    "--port",
    type=int,
    default=DEFAULT_PORT,
    help=f"Server port (default: {DEFAULT_PORT}).",
)
@click.option("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1).")
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Stop a previous editor holding the port, then serve.",
)
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't launch.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def gui_serve(project, port, host, force, dry_run, as_json):
    """Run the editor server in the foreground (Ctrl-C to stop).

    Binds exactly the requested port, and refuses to start when that port is
    taken or when an editor server is already running. `--force` stops a
    previous editor of ours and takes the port back; it never kills a process
    that is not ours.

    \b
    Example:
        $ scitex-writer gui serve
        $ scitex-writer gui serve ~/proj/my-paper --port 31299
        $ scitex-writer gui serve --force
    """
    project_path = _resolve_project(project)
    if project_path is None:
        return 1
    if dry_run:
        if as_json:
            _emit_json({"would_serve": True, "host": host, "port": port})
        else:
            click.echo(f"Would serve editor at http://{host}:{port}.")
        return 0
    current = _gui_runtime.status()
    if current.get("running"):
        if not force:
            click.echo(
                f"Error: editor already running at {current['url']} "
                f"(pid {current['pid']}).\n"
                "\nFix it with one of:\n"
                f"  open {current['url']}\n"
                "  scitex-writer gui stop -y             # stop it\n"
                "  scitex-writer gui serve --force       # stop it and serve here",
                err=True,
            )
            return 1
        click.echo(f"Stopping the editor at {current['url']} (pid {current['pid']}).")
        _gui_runtime.stop()
    if not _port_is_free(host, port):
        click.echo(_port_taken_message(host, port), err=True)
        return 1
    try:
        from ..._django._server import run as _run_editor
    except ImportError as e:
        click.echo(
            f"Error: {e}\nInstall with: pip install scitex-writer[editor]", err=True
        )
        return 1
    _gui_runtime.write_state(os.getpid(), port, host, str(project_path))
    try:
        _run_editor(
            project_dir=str(project_path),
            port=port,
            host=host,
            open_browser=False,
        )
    finally:
        _gui_runtime.clear_state()
    return 0


# =========================================================================
# gui open — ensure a server is running, then open the browser
# =========================================================================


def _autoserve(project_path: Path, port: int, host: str) -> dict:
    """Spawn a detached `gui serve` and wait for its state file."""
    log_path = _gui_runtime.state_path().with_name("gui.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "scitex_writer",
        "gui",
        "serve",
        str(project_path),
        "--port",
        str(port),
        "--host",
        host,
    ]
    with open(log_path, "ab") as log:
        subprocess.Popen(cmd, stdout=log, stderr=log, start_new_session=True)
    deadline = time.monotonic() + 30.0
    while time.monotonic() < deadline:
        current = _gui_runtime.status()
        if current.get("running"):
            return current
        time.sleep(0.3)
    return {"running": False, "log": str(log_path)}


@gui_group.command("open")
@click.argument("project", default=".", required=False)
@click.option(
    "--port",
    type=int,
    default=DEFAULT_PORT,
    help=f"Server port (default: {DEFAULT_PORT}).",
)
@click.option("--host", default="127.0.0.1", help="Host to bind (default: 127.0.0.1).")
@click.option("--no-browser", is_flag=True, default=False, help="Don't open browser.")
@click.option(
    "--desktop",
    is_flag=True,
    default=False,
    help="Launch as desktop window (requires pywebview).",
)
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't launch.")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def gui_open(project, port, host, no_browser, desktop, dry_run, as_json):
    """Open the editor, auto-starting a background server when needed.

    \b
    Example:
        $ scitex-writer gui open
        $ scitex-writer gui open ~/proj/my-paper --port 31299
    """
    project_path = _resolve_project(project)
    if project_path is None:
        return 1
    if dry_run:
        if as_json:
            _emit_json({"would_open": True, "host": host, "port": port})
        else:
            click.echo(f"Would open editor at http://{host}:{port}.")
        return 0
    if desktop:
        try:
            from ..._django._server import run as _run_editor
        except ImportError as e:
            click.echo(
                f"Error: {e}\nInstall with: pip install scitex-writer[editor]",
                err=True,
            )
            return 1
        _run_editor(
            project_dir=str(project_path),
            port=port,
            host=host,
            open_browser=False,
            desktop=True,
        )
        return 0
    current = _gui_runtime.status()
    if not current.get("running"):
        current = _autoserve(project_path, port, host)
        if not current.get("running"):
            click.echo(
                f"Error: server did not come up within 30s; see {current.get('log')}",
                err=True,
            )
            return 1
    url = current["url"]
    if not no_browser:
        webbrowser.open(url)
    if as_json:
        _emit_json(current)
    else:
        click.echo(f"Editor running at {url}.")
    return 0


# =========================================================================
# gui status / gui stop
# =========================================================================


@gui_group.command("status")
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def gui_status(as_json):
    """Report whether the editor server is running.

    \b
    Example:
        $ scitex-writer gui status
        $ scitex-writer gui status --json
    """
    current = _gui_runtime.status()
    if as_json:
        _emit_json(current)
    elif current.get("running"):
        click.echo(f"Running at {current['url']} (pid {current['pid']}).")
    else:
        click.echo("Not running.")
    return 0


@gui_group.command("stop")
@click.option("--dry-run", is_flag=True, default=False, help="Print, don't stop.")
@click.option(
    "--yes", "-y", is_flag=True, default=False, help="Stop without confirmation."
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def gui_stop(dry_run, yes, as_json):
    """Stop the editor server started by `gui serve` / `gui open`.

    \b
    Example:
        $ scitex-writer gui stop -y
        $ scitex-writer gui stop --dry-run
    """
    current = _gui_runtime.status()
    if not current.get("running"):
        if as_json:
            _emit_json({"stopped": False, "running": False})
        else:
            click.echo("Not running.")
        return 0
    if dry_run:
        would = {"would_stop": True, "pid": current["pid"], "url": current["url"]}
        if as_json:
            _emit_json(would)
        else:
            click.echo(f"Would stop {current['url']} (pid {current['pid']}).")
        return 0
    if not yes:
        click.echo(
            f"Refusing to stop {current['url']} (pid {current['pid']}) "
            "without --yes/-y.",
            err=True,
        )
        return 2
    result = _gui_runtime.stop()
    if as_json:
        _emit_json(result)
    elif result.get("stopped"):
        click.echo(f"Stopped (pid {result['pid']}).")
    else:
        click.echo("Not running.")
    return 0


# =========================================================================
# launch-gui — hidden warn-forward alias (one deprecation cycle)
# =========================================================================


@main_group.command("launch-gui", hidden=True)
@click.argument("project", default=".", required=False)
@click.option("--port", type=int, default=DEFAULT_PORT)
@click.option("--host", default="127.0.0.1")
@click.option("--no-browser", is_flag=True, default=False)
@click.option("--desktop", is_flag=True, default=False)
@click.option("--dry-run", is_flag=True, default=False)
@click.option("--yes", "-y", is_flag=True, default=False)
@click.option("--json", "as_json", is_flag=True, default=False)
@click.pass_context
def launch_gui(ctx, project, port, host, no_browser, desktop, dry_run, yes, as_json):
    """Deprecated alias for `gui open`."""
    click.echo("Warning: `launch-gui` is deprecated; use `gui open` instead.", err=True)
    return ctx.invoke(
        gui_open,
        project=project,
        port=port,
        host=host,
        no_browser=no_browser,
        desktop=desktop,
        dry_run=dry_run,
        as_json=as_json,
    )


# EOF
