#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_flask_app.py

"""Flask-based GUI editor for scitex-writer projects.

Provides a browser-based interface for editing LaTeX manuscripts
with PDF preview, file tree, and compilation controls.
"""

import logging
import socket
import webbrowser
from pathlib import Path
from threading import Timer

from flask import Flask

logger = logging.getLogger(__name__)


def _find_available_port(host: str, start_port: int) -> int:
    """Find an available port starting from start_port."""
    port = start_port
    for _ in range(100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((host, port))
                return port
        except OSError:
            port += 1
    return start_port


class WriterEditor:
    """Browser-based LaTeX manuscript editor using Flask.

    Features:
    - File tree sidebar with project structure
    - LaTeX editor with syntax highlighting (CodeMirror)
    - PDF preview panel (pdf.js)
    - One-click compilation (manuscript/supplementary/revision)
    - Dark/light theme toggle
    - Compilation log viewer
    """

    def __init__(
        self,
        project_dir: Path,
        port: int = 5050,
        host: str = "127.0.0.1",
        desktop: bool = False,
    ):
        self.project_dir = Path(project_dir).resolve()
        self.port = port
        self.host = host
        self.desktop = desktop
        self.dark_mode = False

        # Compilation state
        self._compiling = False
        self._compile_result = None
        self._compile_log = ""

        self.app = self._create_app()

    def _create_app(self) -> Flask:
        """Create and configure the Flask application."""
        app = Flask(__name__)
        app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max

        from ._routes_bib import register_bib_routes
        from ._routes_compile import register_compile_routes
        from ._routes_core import register_core_routes
        from ._routes_files import register_file_routes

        register_core_routes(app, self)
        register_file_routes(app, self)
        register_compile_routes(app, self)
        register_bib_routes(app, self)

        return app

    def run(self, open_browser: bool = True) -> None:
        """Start the Flask server."""
        self.port = _find_available_port(self.host, self.port)
        url = f"http://{self.host}:{self.port}"

        if open_browser and not self.desktop:
            Timer(1.0, webbrowser.open, args=[url]).start()

        print(f"SciTeX Writer GUI: {url}")
        print(f"Project: {self.project_dir}")
        print("Press Ctrl+C to stop")

        if self.desktop:
            try:
                import webview

                webview.create_window(
                    "SciTeX Writer",
                    url,
                    width=1400,
                    height=900,
                )
                Timer(
                    0.5,
                    lambda: self.app.run(
                        host=self.host, port=self.port, debug=False, use_reloader=False
                    ),
                ).start()
                webview.start()
            except ImportError:
                print("pywebview not installed. Falling back to browser mode.")
                self.app.run(
                    host=self.host, port=self.port, debug=False, use_reloader=False
                )
        else:
            self.app.run(
                host=self.host, port=self.port, debug=False, use_reloader=False
            )


# EOF
