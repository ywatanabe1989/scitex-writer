#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/__init__.py

"""SciTeX Writer - LaTeX manuscript compilation system with MCP server.

Four Interfaces:
    - Python API: import scitex_writer as sw
    - CLI: scitex-writer <command>
    - GUI: scitex-writer gui (browser-based editor)
    - MCP: 38 tools for AI agents

Modules:
    - claim: Traceable scientific assertions (stats, figures, citations)
    - compile: Compile manuscripts to PDF
    - export: Export manuscript for arXiv submission
    - migration: Import from / export to external platforms (Overleaf)
    - project: Clone, info, get_pdf
    - tables: List, add, remove, csv_to_latex
    - figures: List, add, remove, convert
    - bib: List, add, remove, merge
    - guidelines: IMRAD writing tips
    - prompts: AI2 Asta integration
    - gui: Browser-based editor (requires Flask)
"""

from importlib.metadata import PackageNotFoundError as _PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__ = _version("scitex-writer")
except _PackageNotFoundError:
    # Fallback: parse pyproject.toml (single source of truth)
    from pathlib import Path as _Path

    _pyproject = _Path(__file__).parent.parent.parent / "pyproject.toml"
    __version__ = "0.0.0"
    if _pyproject.exists():
        with open(_pyproject) as _f:
            for _line in _f:
                if _line.startswith("version"):
                    __version__ = _line.split("=")[1].strip().strip('"')
                    break

# Import modules for convenient access
from . import (
    bib,
    claim,
    compile,
    export,
    figures,
    guidelines,
    migration,
    project,
    prompts,
    tables,
    update,
)
from ._dataclasses import CompilationResult as _CompilationResult  # noqa: F401
from ._dataclasses import ManuscriptTree as _ManuscriptTree  # noqa: F401
from ._dataclasses import RevisionTree as _RevisionTree  # noqa: F401
from ._dataclasses import SupplementaryTree as _SupplementaryTree  # noqa: F401
from ._editor import gui
from ._usage import get_usage as usage
from .writer import Writer


def ensure_workspace(project_dir, git_strategy="child", **kwargs):
    """Ensure writer workspace exists at {project_dir}/scitex/writer/.

    If the directory already exists, returns the path without modification.
    If not, clones the full scitex-writer template.

    Parameters
    ----------
    project_dir : str or Path
        Root project directory. Writer workspace will be at
        ``{project_dir}/scitex/writer/``.
    git_strategy : str, optional
        Git initialization strategy ('child', 'parent', 'origin', None).
    **kwargs
        Forwarded to Writer constructor (branch, tag, etc.).

    Returns
    -------
    pathlib.Path
        Path to the writer workspace directory.
    """
    from pathlib import Path

    writer_path = Path(project_dir) / "scitex" / "writer"
    if writer_path.exists() and any(writer_path.iterdir()):
        return writer_path
    Writer(str(writer_path), git_strategy=git_strategy, **kwargs)
    return writer_path


__all__ = [
    "__version__",
    "usage",
    # Modules
    "claim",
    "compile",
    "export",
    "project",
    "tables",
    "figures",
    "bib",
    "guidelines",
    "prompts",
    "migration",
    "update",
    # Writer class
    "Writer",
    "ensure_workspace",
    # GUI
    "gui",
]

# EOF
