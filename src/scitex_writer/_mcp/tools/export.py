#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/tools/export.py

"""Export MCP tools."""


from fastmcp import FastMCP

from ..handlers import export_manuscript as _export_manuscript


def register_tools(mcp: FastMCP) -> None:
    """Register export tools."""

    @mcp.tool()
    def writer_export_manuscript(
        project_dir: str,
        output_dir: str | None = None,
        format: str = "arxiv",
    ) -> dict:
        """[writer] Export manuscript as arXiv-ready tarball."""
        return _export_manuscript(project_dir, output_dir, format)


# EOF
