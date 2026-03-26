#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_mcp/tools/tables.py

"""Table MCP tools."""

from typing import Literal, Optional

from fastmcp import FastMCP

from ..handlers import csv_to_latex as _csv_to_latex
from ..handlers import latex_to_csv as _latex_to_csv
from ..utils import resolve_project_path


def register_tools(mcp: FastMCP) -> None:
    """Register table tools."""

    @mcp.tool()
    def writer_csv_to_latex(
        csv_path: str,
        output_path: Optional[str] = None,
        caption: Optional[str] = None,
        label: Optional[str] = None,
        longtable: bool = False,
    ) -> dict:
        """Convert CSV file to LaTeX table format."""
        return _csv_to_latex(csv_path, output_path, caption, label, longtable)

    @mcp.tool()
    def writer_latex_to_csv(
        latex_path: str,
        output_path: Optional[str] = None,
        table_index: int = 0,
    ) -> dict:
        """Convert LaTeX table to CSV format."""
        return _latex_to_csv(latex_path, output_path, table_index)

    @mcp.tool()
    def writer_list_tables(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
    ) -> dict:
        """List all tables in a writer project."""
        try:
            project_path = resolve_project_path(project_dir)
            doc_dirs = {
                "manuscript": project_path / "01_manuscript",
                "supplementary": project_path / "02_supplementary",
                "revision": project_path / "03_revision",
            }
            doc_dir = doc_dirs.get(doc_type)
            if not doc_dir or not doc_dir.exists():
                return {
                    "success": False,
                    "error": f"Document directory not found: {doc_type}",
                }

            table_dir = doc_dir / "contents" / "tables" / "caption_and_media"
            if not table_dir.exists():
                return {"success": True, "tables": [], "count": 0}

            tables = []
            for csv_file in sorted(table_dir.glob("*.csv")):
                caption_file = csv_file.with_suffix(".tex")
                tables.append(
                    {
                        "name": csv_file.stem,
                        "csv_path": str(csv_file),
                        "caption_path": (
                            str(caption_file) if caption_file.exists() else None
                        ),
                        "has_caption": caption_file.exists(),
                    }
                )

            return {"success": True, "tables": tables, "count": len(tables)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def writer_add_table(
        project_dir: str,
        name: str,
        csv_content: str,
        caption: str,
        label: Optional[str] = None,
        doc_type: Literal["manuscript", "supplementary"] = "manuscript",
    ) -> dict:
        """Add a new table (CSV + caption) to the project."""
        try:
            project_path = resolve_project_path(project_dir)
            doc_dirs = {
                "manuscript": project_path / "01_manuscript",
                "supplementary": project_path / "02_supplementary",
            }
            doc_dir = doc_dirs.get(doc_type)
            if not doc_dir:
                return {"success": False, "error": f"Invalid doc_type: {doc_type}"}

            table_dir = doc_dir / "contents" / "tables" / "caption_and_media"
            table_dir.mkdir(parents=True, exist_ok=True)

            # Write CSV
            csv_path = table_dir / f"{name}.csv"
            csv_path.write_text(csv_content, encoding="utf-8")

            # Write caption
            if label is None:
                label = f"tab:{name.replace(' ', '_')}"
            caption_content = f"\\caption{{{caption}}}\n\\label{{{label}}}\n"
            caption_path = table_dir / f"{name}.tex"
            caption_path.write_text(caption_content, encoding="utf-8")

            return {
                "success": True,
                "csv_path": str(csv_path),
                "caption_path": str(caption_path),
                "label": label,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def writer_remove_table(
        project_dir: str,
        name: str,
        doc_type: Literal["manuscript", "supplementary"] = "manuscript",
    ) -> dict:
        """Remove a table (CSV + caption) from the project."""
        from scitex_writer.tables import remove

        return remove(project_dir, name, doc_type)

    @mcp.tool()
    def writer_archive_table(
        project_dir: str,
        name: str,
        doc_type: Literal["manuscript", "supplementary"] = "manuscript",
    ) -> dict:
        """Move a table to legacy/ instead of deleting.

        Moves CSV and caption files from caption_and_media/ to legacy/,
        preserving them for potential reuse or supplementary materials.
        """
        from scitex_writer.tables import archive

        return archive(project_dir, name, doc_type)


# EOF
