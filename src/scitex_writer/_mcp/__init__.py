#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: src/scitex_writer/_mcp/__init__.py

"""
SciTeX Writer MCP module.

Re-exports from _server.py for backwards compatibility.
"""

from scitex_writer._server import INSTRUCTIONS, mcp, run_server

from .handlers import (
    clone_project,
    compile_manuscript,
    compile_revision,
    compile_supplementary,
    convert_figure,
    csv_to_latex,
    get_pdf,
    get_project_info,
    latex_to_csv,
    list_document_types,
    list_figures,
    pdf_to_images,
)
from .utils import resolve_project_path, run_compile_script

__all__ = [
    # Server exports
    "mcp",
    "INSTRUCTIONS",
    "run_server",
    # Handlers
    "clone_project",
    "compile_manuscript",
    "compile_supplementary",
    "compile_revision",
    "get_project_info",
    "get_pdf",
    "list_document_types",
    "csv_to_latex",
    "latex_to_csv",
    "pdf_to_images",
    "list_figures",
    "convert_figure",
    # Utils
    "resolve_project_path",
    "run_compile_script",
]

# EOF
