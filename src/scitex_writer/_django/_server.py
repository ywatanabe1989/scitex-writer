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
import socket
import threading
import webbrowser
from pathlib import Path


def _find_available_port(host: str, start_port: int) -> int:
    port = start_port
    for _ in range(100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return port
        except OSError:
            port += 1
    return start_port


def run(
    project_dir: str,
    port: int = 5050,
    host: str = "127.0.0.1",
    open_browser: bool = True,
    desktop: bool = False,
    hot_reload: bool = False,
) -> None:
    """Launch the Django editor server locally.

    Tries `scitex_app._standalone.run_standalone` first (gets the full
    workspace shell from scitex-ui). Falls back to a bare runserver
    bootstrap if scitex-app is not installed.
    """
    project_path = Path(project_dir).resolve()
    if not project_path.exists():
        raise FileNotFoundError(f"Project directory not found: {project_path}")

    os.environ["WRITER_WORKING_DIR"] = str(project_path)
    os.environ["SCITEX_WORKING_DIR"] = str(project_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scitex_writer._django.settings")

    port = _find_available_port(host, port)
    print(f"SciTeX Writer GUI: http://{host}:{port}")
    print(f"Project: {project_path}")
    print("Press Ctrl+C to stop")

    try:
        import django

        django.setup()

        from django.core.management import call_command

        call_command("migrate", "--run-syncdb", verbosity=0)

        from scitex_app._standalone import run_standalone

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
    except ImportError:
        pass

    # Fallback: no scitex-app available, run bare Django
    import django

    django.setup()
    from django.core.management import call_command

    if open_browser and not desktop:
        threading.Timer(1.0, webbrowser.open, args=[f"http://{host}:{port}"]).start()

    noreload = [] if hot_reload else ["--noreload"]
    call_command("runserver", f"{host}:{port}", *noreload)
