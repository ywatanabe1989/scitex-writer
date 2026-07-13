#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Standalone local-dev launcher for the writer editor.

Delegates to `scitex_app._standalone.run_standalone`, which pre-wires
scitex-ui static assets + the workspace shell so the same local server
looks like scitex.ai/apps/writer.

Cloud deployments do NOT use this — they mount `scitex_writer._django.urls`
into their own Django project.
"""

from __future__ import annotations

import os
import threading
import webbrowser
from pathlib import Path

from .._core._gui_runtime import DEFAULT_PORT


def run(
    project_dir: str,
    port: int = DEFAULT_PORT,
    host: str = "127.0.0.1",
    open_browser: bool = True,
    desktop: bool = False,
    hot_reload: bool = False,
) -> None:
    """Launch the Django editor server locally on exactly ``port``.

    Uses `scitex_app._standalone.run_standalone` (gets the full workspace
    shell from scitex-ui). When scitex-app is not installed, says so and
    serves bare Django instead; every other error propagates.

    The requested port is bound as given: when it is already in use the
    server fails instead of drifting to the next free port (which used to
    leave a stack of duplicate instances behind).
    """
    project_path = Path(project_dir).resolve()
    if not project_path.exists():
        raise FileNotFoundError(f"Project directory not found: {project_path}")

    os.environ["SCITEX_WRITER_WORKING_DIR"] = str(project_path)
    # Deprecated unprefixed spelling — kept for one cycle so external
    # launchers/readers keep working while they migrate.
    os.environ["WRITER_WORKING_DIR"] = str(project_path)
    os.environ["SCITEX_WORKING_DIR"] = str(project_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scitex_writer._django.settings")

    print(f"SciTeX Writer GUI: http://{host}:{port}")
    print(f"Project: {project_path}")
    print("Press Ctrl+C to stop")

    try:
        from scitex_app.embed import run_standalone
    except ImportError:
        run_standalone = None
        print(
            "Note: scitex-app is not installed, so the workspace shell is "
            "unavailable; serving bare Django instead.\n"
            "      Get it with: uv pip install 'scitex-writer[all]'"
        )

    import django

    django.setup()

    from django.core.management import call_command

    call_command("migrate", "--run-syncdb", verbosity=0)

    if run_standalone is not None:
        run_standalone(
            app_module="scitex_writer._django",
            port=port,
            host=host,
            open_browser=open_browser,
            hot_reload=hot_reload,
            working_dir=str(project_path),
            desktop=desktop,
        )
        return

    if open_browser and not desktop:
        threading.Timer(1.0, webbrowser.open, args=[f"http://{host}:{port}"]).start()

    noreload = [] if hot_reload else ["--noreload"]
    call_command("runserver", f"{host}:{port}", *noreload)
