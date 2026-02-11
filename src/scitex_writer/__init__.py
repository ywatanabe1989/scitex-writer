#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/__init__.py

"""SciTeX Writer - LaTeX manuscript compilation system with MCP server.

Three Interfaces:
    - Python API: import scitex_writer as sw
    - CLI: scitex-writer <command>
    - MCP: 30 tools for AI agents

Modules:
    - compile: Compile manuscripts to PDF
    - export: Export manuscript for arXiv submission
    - project: Clone, info, get_pdf
    - tables: List, add, remove, csv_to_latex
    - figures: List, add, remove, convert
    - bib: List, add, remove, merge
    - guidelines: IMRAD writing tips
    - prompts: AI2 Asta integration
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

# Branding support (set SCITEX_WRITER_BRAND and SCITEX_WRITER_ALIAS env vars before import)
# Import modules for convenient access
from . import bib, compile, export, figures, guidelines, project, prompts, tables
from ._branding import BRAND_ALIAS, BRAND_NAME
from ._dataclasses import (
    CompilationResult,
    ManuscriptTree,
    RevisionTree,
    SupplementaryTree,
)
from ._usage import get_usage as usage

# Import Writer class and dataclasses
from .writer import Writer

__all__ = [
    "__version__",
    # Branding
    "BRAND_NAME",
    "BRAND_ALIAS",
    # Usage
    "usage",
    # Modules
    "compile",
    "export",
    "project",
    "tables",
    "figures",
    "bib",
    "guidelines",
    "prompts",
    # Writer class
    "Writer",
    # Dataclasses
    "CompilationResult",
    "ManuscriptTree",
    "SupplementaryTree",
    "RevisionTree",
]

# EOF
