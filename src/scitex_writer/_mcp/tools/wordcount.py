#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/tools/wordcount.py

"""Word-count MCP tools."""

from fastmcp import FastMCP

from ..handlers._wordcount import count_words as _count_words


def register_tools(mcp: FastMCP) -> None:
    """Register word-count tools with the MCP server."""

    @mcp.tool()
    def writer_count_words(project_dir: str, doc_type: str = "manuscript") -> dict:
        """Count words + figure/table elements per section and write count files.

        doc_type: 'manuscript' (default), 'supplementary', or 'revision'.
        Writes one integer per key into the project's wordcount_dir (the files
        the manuscript's \\readwordcount reads). Returns
        {success, doc_type, counts, total, output_files, error}.
        """
        return _count_words(project_dir, doc_type)


# EOF
