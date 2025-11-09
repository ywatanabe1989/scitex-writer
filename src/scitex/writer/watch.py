#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
File watching and auto-compilation for scitex-writer.

Provides functions to watch for file changes and auto-compile.
"""

from pathlib import Path
from typing import Optional, Callable
import subprocess


def watch_manuscript(
    project_dir: Path,
    doc_type: str = "manuscript",
    callback: Optional[Callable] = None,
):
    """
    Watch for file changes and auto-compile.

    Args:
        project_dir: Path to project directory
        doc_type: Document type (manuscript, supplementary, revision)
        callback: Optional callback function called after each compilation

    Example:
        >>> from scitex.writer import watch_manuscript
        >>> watch_manuscript("/path/to/manuscript")
    """
    project_dir = Path(project_dir).resolve()
    script_path = project_dir / "scripts" / "shell" / "watch_compile.sh"

    if not script_path.exists():
        raise FileNotFoundError(f"Watch script not found: {script_path}")

    try:
        # Run watch script
        env = {"SCITEX_WRITER_DOC_TYPE": doc_type}
        subprocess.run(
            [str(script_path)],
            cwd=project_dir,
            env={**dict(os.environ), **env},
            check=True,
        )
    except KeyboardInterrupt:
        print("\nStopped watching.")
    except subprocess.CalledProcessError as e:
        print(f"Watch failed: {e}")


__all__ = ["watch_manuscript"]
