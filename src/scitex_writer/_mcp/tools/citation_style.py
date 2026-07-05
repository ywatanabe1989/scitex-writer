#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/tools/citation_style.py

"""Citation-style MCP tools."""

from typing import Optional

from fastmcp import FastMCP

from ..handlers._citation_style import apply as _apply


def register_tools(mcp: FastMCP) -> None:
    """Register citation-style tools with the MCP server."""

    @mcp.tool()
    def writer_apply_citation_style(
        project_dir: str,
        doc_type: str = "manuscript",
        style: Optional[str] = None,
    ) -> dict:
        """Set the active \\bibliographystyle in bibliography.tex.

        style: e.g. 'nature', 'ieee', 'apa'. When omitted, resolved from
        config/config_<doc_type>.yaml (citation.style) or
        SCITEX_WRITER_CITATION_STYLE. doc_type: 'manuscript' (default),
        'supplementary', 'revision'. Returns
        {success, changed, current_style, new_style, backup_path, message}.
        """
        return _apply(project_dir, doc_type, style)


# EOF
