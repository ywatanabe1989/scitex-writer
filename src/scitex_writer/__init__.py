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
    __version__ = "2.3.0"  # fallback for development

# Import modules for convenient access
from . import bib, compile, figures, guidelines, project, prompts, tables

# Top-level convenience functions
from .guidelines import build as build_guideline
from .guidelines import get as get_guideline
from .guidelines import list_sections as list_guidelines
from .prompts import generate_ai2_prompt, generate_asta

__all__ = [
    "__version__",
    # Modules
    "compile",
    "project",
    "tables",
    "figures",
    "bib",
    "guidelines",
    "prompts",
    # Guidelines functions
    "get_guideline",
    "build_guideline",
    "list_guidelines",
    # Prompts functions
    "generate_ai2_prompt",
    "generate_asta",
]

# EOF
