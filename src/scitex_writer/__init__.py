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
    - gui: Browser-based editor (Django)
"""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError as _PackageNotFoundError
from importlib.metadata import version as _version

try:
    __version__ = _version("scitex-writer")
except _PackageNotFoundError:
    # Fallback: parse pyproject.toml (single source of truth)
    from pathlib import Path as _Path

    _pyproject = _Path(__file__).parent.parent.parent / "pyproject.toml"
    __version__ = "0.0.0+local"
    if _pyproject.exists():
        with open(_pyproject) as _f:
            for _line in _f:
                if _line.startswith("version"):
                    __version__ = _line.split("=")[1].strip().strip('"')
                    break

# ---------------------------------------------------------------------------
# Lazy public surface (PEP 562 module __getattr__).
#
# `import scitex_writer` must stay cheap: a bare import that eagerly pulled in
# every submodule (Django, fastmcp, scitex-dev, …) cost ~700ms over the
# bare-interpreter baseline, tripping the audit-cli §10 startup-speed rule and
# slowing Click tab-completion (the CLI re-runs the program once per Tab). We
# defer each name to first access instead; `sw.Writer`, `sw.compile`,
# `from scitex_writer import migration`, etc. all resolve on demand with no
# change to the public API.
# ---------------------------------------------------------------------------

# Submodules exposed directly as attributes (`sw.<name>`); imported on demand.
# Dict (name -> relative module path) so the API auditor's PA-102 dispatch-
# table detector recognises every key as a bound name (PEP 562 lazy-load).
_LAZY_SUBMODULES = {
    "bib": ".bib",
    "checks": ".checks",
    "claim": ".claim",
    "compile": ".compile",
    "export": ".export",
    "figures": ".figures",
    "guidelines": ".guidelines",
    "migration": ".migration",
    "project": ".project",
    "prompts": ".prompts",
    "tables": ".tables",
    "update": ".update",
}

# Public symbols → (submodule, attribute-in-submodule).
_LAZY_SYMBOLS = {
    "Writer": (".writer", "Writer"),
    "gui": ("._django._server", "run"),
    "usage": ("._usage", "get_usage"),
    # Re-exported dataclasses (kept for introspection / back-compat).
    "_CompilationResult": ("._dataclasses", "CompilationResult"),
    "_ManuscriptTree": ("._dataclasses", "ManuscriptTree"),
    "_RevisionTree": ("._dataclasses", "RevisionTree"),
    "_SupplementaryTree": ("._dataclasses", "SupplementaryTree"),
}


def __getattr__(name):
    import importlib

    submodule_path = _LAZY_SUBMODULES.get(name)
    if submodule_path is not None:
        module = importlib.import_module(submodule_path, __name__)
        globals()[name] = module  # cache so subsequent access skips __getattr__
        return module
    target = _LAZY_SYMBOLS.get(name)
    if target is not None:
        submodule, attr = target
        value = getattr(importlib.import_module(submodule, __name__), attr)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(set(globals()) | set(__all__) | set(_LAZY_SUBMODULES))


def ensure_workspace(project_dir, git_strategy="child", **kwargs):
    """Ensure writer workspace exists at {project_dir}/.scitex/writer/.

    If the directory already exists, returns the path without modification.
    If not, clones the full scitex-writer template.

    Parameters
    ----------
    project_dir : str or Path
        Root project directory. Writer workspace will be at
        ``{project_dir}/.scitex/writer/`` (hidden, dotfile convention).
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

    from .writer import Writer

    writer_path = Path(project_dir) / ".scitex" / "writer"
    if writer_path.exists() and any(writer_path.iterdir()):
        return writer_path
    Writer(str(writer_path), git_strategy=git_strategy, **kwargs)
    return writer_path


__all__ = [
    "__version__",
    "usage",
    # Modules
    "checks",
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
