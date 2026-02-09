#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/__init__.py

"""MCP Handler implementations for SciTeX Writer."""

from ._compile import compile_manuscript, compile_revision, compile_supplementary
from ._export import export_manuscript
from ._figures import convert_figure, list_figures, pdf_to_images
from ._project import clone_project, get_pdf, get_project_info, list_document_types
from ._tables import csv_to_latex, latex_to_csv

__all__ = [
    "clone_project",
    "compile_manuscript",
    "compile_supplementary",
    "compile_revision",
    "export_manuscript",
    "get_project_info",
    "get_pdf",
    "list_document_types",
    "csv_to_latex",
    "latex_to_csv",
    "pdf_to_images",
    "list_figures",
    "convert_figure",
]

# EOF
