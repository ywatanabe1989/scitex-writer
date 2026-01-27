#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/tables.py

"""Table management functions.

Usage::

    import scitex_writer as sw

    # List tables in project
    result = sw.tables.list("./my-paper")

    # Add a table
    sw.tables.add("./my-paper", "results", "col1,col2\\n1,2", "Results summary")

    # Convert CSV to LaTeX
    result = sw.tables.csv_to_latex("data.csv", "table.tex")
"""

from typing import Literal as _Literal
from typing import Optional as _Optional

from ._mcp.handlers import csv_to_latex as _csv_to_latex
from ._mcp.handlers import latex_to_csv as _latex_to_csv
from ._mcp.utils import resolve_project_path as _resolve_project_path


def list(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision"] = "manuscript",
) -> dict:
    """List all tables in a writer project.

    Args:
        project_dir: Path to scitex-writer project.
        doc_type: Document type to search.

    Returns:
        Dict with tables list and count.
    """
    try:
        project_path = _resolve_project_path(project_dir)
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
                    "caption_path": str(caption_file)
                    if caption_file.exists()
                    else None,
                    "has_caption": caption_file.exists(),
                }
            )

        return {"success": True, "tables": tables, "count": len(tables)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def add(
    project_dir: str,
    name: str,
    csv_content: str,
    caption: str,
    label: _Optional[str] = None,
    doc_type: _Literal["manuscript", "supplementary"] = "manuscript",
) -> dict:
    """Add a new table (CSV + caption) to the project.

    Args:
        project_dir: Path to scitex-writer project.
        name: Table name (without extension).
        csv_content: CSV content as string.
        caption: Table caption text.
        label: LaTeX label (default: tab:<name>).
        doc_type: Target document type.

    Returns:
        Dict with csv_path, caption_path, label.
    """
    try:
        project_path = _resolve_project_path(project_dir)
        doc_dirs = {
            "manuscript": project_path / "01_manuscript",
            "supplementary": project_path / "02_supplementary",
        }
        doc_dir = doc_dirs.get(doc_type)
        if not doc_dir:
            return {"success": False, "error": f"Invalid doc_type: {doc_type}"}

        table_dir = doc_dir / "contents" / "tables" / "caption_and_media"
        table_dir.mkdir(parents=True, exist_ok=True)

        csv_path = table_dir / f"{name}.csv"
        csv_path.write_text(csv_content, encoding="utf-8")

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


def remove(
    project_dir: str,
    name: str,
    doc_type: _Literal["manuscript", "supplementary"] = "manuscript",
) -> dict:
    """Remove a table (CSV + caption) from the project.

    Args:
        project_dir: Path to scitex-writer project.
        name: Table name (without extension).
        doc_type: Document type.

    Returns:
        Dict with removed file paths.
    """
    try:
        project_path = _resolve_project_path(project_dir)
        doc_dirs = {
            "manuscript": project_path / "01_manuscript",
            "supplementary": project_path / "02_supplementary",
        }
        doc_dir = doc_dirs.get(doc_type)
        if not doc_dir:
            return {"success": False, "error": f"Invalid doc_type: {doc_type}"}

        table_dir = doc_dir / "contents" / "tables" / "caption_and_media"
        csv_path = table_dir / f"{name}.csv"
        caption_path = table_dir / f"{name}.tex"

        removed = []
        if csv_path.exists():
            csv_path.unlink()
            removed.append(str(csv_path))
        if caption_path.exists():
            caption_path.unlink()
            removed.append(str(caption_path))

        if not removed:
            return {"success": False, "error": f"Table not found: {name}"}

        return {"success": True, "removed": removed}
    except Exception as e:
        return {"success": False, "error": str(e)}


def csv_to_latex(
    csv_path: str,
    output_path: _Optional[str] = None,
    caption: _Optional[str] = None,
    label: _Optional[str] = None,
    longtable: bool = False,
) -> dict:
    """Convert CSV file to LaTeX table format.

    Args:
        csv_path: Path to CSV file.
        output_path: Output .tex file path (optional).
        caption: Table caption.
        label: LaTeX label.
        longtable: Use longtable environment.

    Returns:
        Dict with latex_content and output_path.
    """
    return _csv_to_latex(csv_path, output_path, caption, label, longtable)


def latex_to_csv(
    latex_path: str,
    output_path: _Optional[str] = None,
    table_index: int = 0,
) -> dict:
    """Convert LaTeX table to CSV format.

    Args:
        latex_path: Path to LaTeX file.
        output_path: Output .csv file path (optional).
        table_index: Which table to extract (0-indexed).

    Returns:
        Dict with preview and output_path.
    """
    return _latex_to_csv(latex_path, output_path, table_index)


__all__ = ["list", "add", "remove", "csv_to_latex", "latex_to_csv"]

# EOF
