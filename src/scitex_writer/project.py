#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/project.py

"""Project management functions.

Usage::

    import scitex_writer as sw

    # Create new project from template
    result = sw.project.clone("./my-new-paper")

    # Get project info
    info = sw.project.info("./my-paper")

    # Get path to compiled PDF
    pdf = sw.project.get_pdf("./my-paper", "manuscript")
"""

from typing import Literal, Optional

from ._mcp.handlers import clone_project as _clone_project
from ._mcp.handlers import get_pdf as _get_pdf
from ._mcp.handlers import get_project_info as _get_project_info
from ._mcp.handlers import list_document_types as _list_document_types


def clone(
    project_dir: str,
    git_strategy: Literal["child", "parent", "origin", "none"] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
) -> dict:
    """Create a new writer project from template.

    Args:
        project_dir: Path for the new project.
        git_strategy: How to handle git:
            - "child": Fresh git repo (default)
            - "parent": Keep template history
            - "origin": Keep as clone of template
            - "none": No git initialization
        branch: Clone specific branch.
        tag: Clone specific tag.

    Returns:
        Dict with success status and project_path.
    """
    return _clone_project(project_dir, git_strategy, branch, tag)


def info(project_dir: str) -> dict:
    """Get writer project information.

    Args:
        project_dir: Path to scitex-writer project.

    Returns:
        Dict with project_name, documents, compiled_pdfs.
    """
    return _get_project_info(project_dir)


def get_pdf(
    project_dir: str,
    doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
) -> dict:
    """Get path to compiled PDF.

    Args:
        project_dir: Path to scitex-writer project.
        doc_type: Document type.

    Returns:
        Dict with pdf_path if exists.
    """
    return _get_pdf(project_dir, doc_type)


def list_document_types() -> dict:
    """List available document types.

    Returns:
        Dict with document_types list.
    """
    return _list_document_types()


__all__ = ["clone", "info", "get_pdf", "list_document_types"]

# EOF
