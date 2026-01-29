#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_mcp/tools/project.py

"""Project management MCP tools."""

from __future__ import annotations

from typing import Literal, Optional

from fastmcp import FastMCP

from ..handlers import (
    clone_project as _clone_project,
)
from ..handlers import (
    get_pdf as _get_pdf,
)
from ..handlers import (
    get_project_info as _get_project_info,
)
from ..handlers import (
    list_document_types as _list_document_types,
)


def register_tools(mcp: FastMCP) -> None:
    """Register project management tools."""

    @mcp.tool()
    def writer_clone_project(
        project_dir: str,
        git_strategy: Literal["child", "parent", "origin", "none"] = "child",
        branch: Optional[str] = None,
        tag: Optional[str] = None,
    ) -> dict:
        """[writer] Create a new LaTeX manuscript project from template."""
        return _clone_project(project_dir, git_strategy, branch, tag)

    @mcp.tool()
    def writer_get_project_info(project_dir: str) -> dict:
        """[writer] Get writer project structure and status information."""
        return _get_project_info(project_dir)

    @mcp.tool()
    def writer_get_pdf(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
    ) -> dict:
        """[writer] Get path to compiled PDF for a document type."""
        return _get_pdf(project_dir, doc_type)

    @mcp.tool()
    def writer_list_document_types() -> dict:
        """[writer] List available document types in a writer project."""
        return _list_document_types()


# EOF
