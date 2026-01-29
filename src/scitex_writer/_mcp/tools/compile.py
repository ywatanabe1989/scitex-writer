#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_mcp/tools/compile.py

"""Compilation MCP tools."""

from __future__ import annotations

from fastmcp import FastMCP

from ..handlers import (
    compile_manuscript as _compile_manuscript,
)
from ..handlers import (
    compile_revision as _compile_revision,
)
from ..handlers import (
    compile_supplementary as _compile_supplementary,
)


def register_tools(mcp: FastMCP) -> None:
    """Register compilation tools."""

    @mcp.tool()
    def writer_compile_manuscript(
        project_dir: str,
        timeout: int = 300,
        no_figs: bool = False,
        no_tables: bool = False,
        no_diff: bool = False,
        draft: bool = False,
        dark_mode: bool = False,
        quiet: bool = False,
        verbose: bool = False,
        force: bool = False,
    ) -> dict:
        """[writer] Compile manuscript LaTeX document to PDF."""
        return _compile_manuscript(
            project_dir,
            timeout,
            no_figs,
            no_tables,
            no_diff,
            draft,
            dark_mode,
            quiet,
            verbose,
            force,
        )

    @mcp.tool()
    def writer_compile_supplementary(
        project_dir: str,
        timeout: int = 300,
        no_figs: bool = False,
        no_tables: bool = False,
        no_diff: bool = False,
        draft: bool = False,
        quiet: bool = False,
    ) -> dict:
        """[writer] Compile supplementary materials LaTeX document to PDF."""
        return _compile_supplementary(
            project_dir,
            timeout,
            no_figs,
            no_tables,
            no_diff,
            draft,
            quiet,
        )

    @mcp.tool()
    def writer_compile_revision(
        project_dir: str,
        track_changes: bool = False,
        timeout: int = 300,
        no_diff: bool = True,
        draft: bool = False,
        quiet: bool = False,
    ) -> dict:
        """[writer] Compile revision document to PDF with optional change tracking."""
        return _compile_revision(
            project_dir,
            track_changes,
            timeout,
            no_diff,
            draft,
            quiet,
        )

    @mcp.tool()
    def writer_compile_content(
        latex_content: str,
        project_dir: str | None = None,
        color_mode: str = "light",
        name: str = "content",
        timeout: int = 60,
        keep_aux: bool = False,
    ) -> dict:
        """[writer] Compile raw LaTeX content to PDF with color mode support.

        Compiles provided LaTeX content to PDF. Supports color modes:
        'light', 'dark', 'sepia', 'paper'.
        """
        from ..content import compile_content as _compile_content

        return _compile_content(
            latex_content,
            project_dir,
            color_mode,
            name,
            timeout,
            keep_aux,
        )


# EOF
