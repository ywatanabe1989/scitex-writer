#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/__init__.py

"""Standalone Flask GUI editor for scitex-writer projects.

Launch a browser-based LaTeX editor with PDF preview, file tree,
and compilation controls. No database or authentication needed.

Usage
-----
>>> import scitex_writer as sw
>>> sw.gui("./my-paper")  # Opens browser with interactive editor

Or from CLI:
    scitex-writer gui ./my-paper
"""

from pathlib import Path


def gui(
    project_dir: str = ".",
    port: int = 5050,
    host: str = "127.0.0.1",
    open_browser: bool = True,
    desktop: bool = False,
) -> None:
    """Launch interactive GUI editor for a scitex-writer project.

    Parameters
    ----------
    project_dir : str
        Path to scitex-writer project directory (default: current directory).
    port : int
        Flask server port (default: 5050).
    host : str
        Host to bind (default: 127.0.0.1).
    open_browser : bool
        Whether to open browser automatically (default: True).
    desktop : bool
        Launch as native desktop window using pywebview (default: False).
    """
    import importlib.util

    if importlib.util.find_spec("flask") is None:
        raise ImportError(
            "Flask is required for the GUI editor. "
            "Install with: pip install scitex-writer[editor] or pip install flask"
        )

    project_path = Path(project_dir).resolve()
    if not project_path.exists():
        raise FileNotFoundError(f"Project directory not found: {project_path}")

    from ._flask_app import WriterEditor

    editor = WriterEditor(
        project_dir=project_path,
        port=port,
        host=host,
        desktop=desktop,
    )
    editor.run(open_browser=open_browser)


__all__ = ["gui"]

# EOF
