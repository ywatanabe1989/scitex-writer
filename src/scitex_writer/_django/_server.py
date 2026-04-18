#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Standalone local-dev launcher for the writer editor.

Bootstraps Django with minimal `scitex_writer._django.settings` and serves
the editor on localhost. Cloud deployments do NOT use this — they mount
`scitex_writer._django.urls` into their own Django project.

This is what `scitex-writer gui` invokes.
"""

from __future__ import annotations

import os
import socket
import sys
import threading
import time
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
) -> None:
    """Launch the Django editor server locally."""
    project_path = Path(project_dir).resolve()
    if not project_path.exists():
        raise FileNotFoundError(f"Project directory not found: {project_path}")

    os.environ["WRITER_WORKING_DIR"] = str(project_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "scitex_writer._django.settings")

    import django

    django.setup()

    port = _find_available_port(host, port)
    url = f"http://{host}:{port}"
    print(f"SciTeX Writer GUI: {url}")
    print(f"Project: {project_path}")
    print("Press Ctrl+C to stop")

    if open_browser and not desktop:
        threading.Timer(1.0, webbrowser.open, args=[url]).start()

    from django.core.management import execute_from_command_line

    if desktop:
        try:
            import webview  # type: ignore

            def _serve():
                time.sleep(0.3)
                execute_from_command_line(
                    [sys.argv[0], "runserver", f"{host}:{port}", "--noreload"]
                )

            threading.Thread(target=_serve, daemon=True).start()
            webview.create_window("SciTeX Writer", url, width=1400, height=900)
            webview.start()
            return
        except ImportError:
            print("pywebview not installed. Falling back to browser mode.")

    execute_from_command_line(
        [sys.argv[0], "runserver", f"{host}:{port}", "--noreload"]
    )
