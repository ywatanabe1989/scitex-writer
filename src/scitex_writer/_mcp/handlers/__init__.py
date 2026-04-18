#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/__init__.py

"""MCP Handler implementations for SciTeX Writer."""

from ._checks import check_float_order, check_references
from ._claim import (
    add_claim,
    format_claim,
    get_claim,
    list_claims,
    remove_claim,
    render_claims,
)
from ._compile import compile_manuscript, compile_revision, compile_supplementary
from ._export import export_manuscript
from ._figures import convert_figure, list_figures, pdf_to_images
from ._project import clone_project, get_pdf, get_project_info, list_document_types
from ._tables import csv_to_latex, latex_to_csv
from ._update import update_project  # noqa: F401 -- now a package

__all__ = [
    "add_claim",
    "check_float_order",
    "check_references",
    "clone_project",
    "compile_manuscript",
    "compile_supplementary",
    "compile_revision",
    "csv_to_latex",
    "convert_figure",
    "export_manuscript",
    "format_claim",
    "get_claim",
    "get_pdf",
    "get_project_info",
    "latex_to_csv",
    "list_claims",
    "list_document_types",
    "list_figures",
    "pdf_to_images",
    "remove_claim",
    "render_claims",
    "update_project",
]

# EOF
