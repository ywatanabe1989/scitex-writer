#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/tools/cleanup.py

"""Cleanup MCP tools."""

from fastmcp import FastMCP

from ..handlers._cleanup import clean as _clean


def register_tools(mcp: FastMCP) -> None:
    """Register cleanup tools with the MCP server."""

    @mcp.tool()
    def writer_clean_artifacts(
        project_dir: str, doc_type: str = "manuscript", dry_run: bool = False
    ) -> dict:
        """Sweep LaTeX build artefacts for a document type.

        Removes *bak* and Emacs temp (#*#) files recursively, moves top-level
        aux/log files into the project's doc_log_dir, removes progress.log
        files, and removes versioned *_v*.pdf / *_v*.tex files -- never touching
        anything outside the project root. doc_type: 'manuscript' (default),
        'supplementary', or 'revision'. dry_run=True previews (nothing mutated).
        Returns {success, bak_removed, emacs_removed, aux_moved,
        progress_removed, versioned_removed, log_dir, dry_run, error}.
        """
        return _clean(project_dir, doc_type, dry_run)


# EOF
