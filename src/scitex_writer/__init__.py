#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/__init__.py

"""SciTeX Writer - LaTeX manuscript compilation system with MCP server.

Three Interfaces:
    - Python API: import scitex_writer as sw
    - CLI: scitex-writer <command>
    - MCP: 28 tools for AI agents

Modules:
    - compile: Compile manuscripts to PDF
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
    __version__ = "2.4.0"  # fallback for development

# Branding support (set SCITEX_WRITER_BRAND and SCITEX_WRITER_ALIAS env vars before import)
# Import modules for convenient access
from . import bib, compile, figures, guidelines, project, prompts, tables
from ._branding import BRAND_ALIAS, BRAND_NAME
from ._dataclasses import (
    CompilationResult,
    ManuscriptTree,
    RevisionTree,
    SupplementaryTree,
)

# Import Writer class and dataclasses
from .writer import Writer

__all__ = [
    "__version__",
    # Branding
    "BRAND_NAME",
    "BRAND_ALIAS",
    # Modules
    "compile",
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
