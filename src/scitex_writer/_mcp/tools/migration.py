#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/tools/migration.py

"""MCP tools: migration (import/export Overleaf)."""

from typing import Optional

from fastmcp import FastMCP


def register_tools(mcp: FastMCP) -> None:
    """Register migration tools."""

    @mcp.tool()
    def writer_import_overleaf(
        zip_path: str,
        output_dir: Optional[str] = None,
        project_name: Optional[str] = None,
        dry_run: bool = False,
        force: bool = False,
    ) -> dict:
        """[writer] Import an Overleaf ZIP export into a scitex-writer project.

        Analyzes the Overleaf project structure, maps sections to IMRAD format,
        and creates a complete scitex-writer project with figures, bibliography,
        and content properly placed.

        Args:
            zip_path: Path to the Overleaf ZIP file.
            output_dir: Where to create the project (default: ./<zip_name>).
            project_name: Name for the project (default: derived from ZIP).
            dry_run: If True, show mapping without creating files.
            force: If True, overwrite existing output directory.
        """
        from ...migration import from_overleaf

        return from_overleaf(zip_path, output_dir, project_name, dry_run, force)

    @mcp.tool()
    def writer_export_overleaf(
        project_dir: str = ".",
        output_path: Optional[str] = None,
        dry_run: bool = False,
    ) -> dict:
        """[writer] Export a scitex-writer project as Overleaf-compatible ZIP.

        Flattens the project structure into a format uploadable to Overleaf,
        with a single main.tex, images directory, and merged bibliography.

        Args:
            project_dir: Path to the scitex-writer project.
            output_path: Path for the output ZIP (default: overleaf_export.zip).
            dry_run: If True, list files without creating ZIP.
        """
        from ...migration import to_overleaf

        return to_overleaf(project_dir, output_path, dry_run)


# EOF
