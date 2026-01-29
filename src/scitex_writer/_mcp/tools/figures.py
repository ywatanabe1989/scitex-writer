#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_mcp/tools/figures.py

"""Figure MCP tools."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Literal, Optional, Union

from fastmcp import FastMCP

from ..handlers import (
    convert_figure as _convert_figure,
)
from ..handlers import (
    list_figures as _list_figures,
)
from ..handlers import (
    pdf_to_images as _pdf_to_images,
)
from ..utils import resolve_project_path


def register_tools(mcp: FastMCP) -> None:
    """Register figure tools."""

    @mcp.tool()
    def writer_list_figures(
        project_dir: str,
        extensions: Optional[List[str]] = None,
    ) -> dict:
        """[writer] List all figures in a writer project directory."""
        return _list_figures(project_dir, extensions)

    @mcp.tool()
    def writer_convert_figure(
        input_path: str,
        output_path: str,
        dpi: int = 300,
        quality: int = 95,
    ) -> dict:
        """[writer] Convert figure between formats (e.g., PDF to PNG)."""
        return _convert_figure(input_path, output_path, dpi, quality)

    @mcp.tool()
    def writer_pdf_to_images(
        pdf_path: str,
        output_dir: Optional[str] = None,
        pages: Optional[Union[int, List[int]]] = None,
        dpi: int = 150,
        format: Literal["png", "jpg"] = "png",
    ) -> dict:
        """[writer] Render PDF pages as images."""
        return _pdf_to_images(pdf_path, output_dir, pages, dpi, format)

    @mcp.tool()
    def writer_add_figure(
        project_dir: str,
        name: str,
        image_path: str,
        caption: str,
        label: Optional[str] = None,
        doc_type: Literal["manuscript", "supplementary"] = "manuscript",
    ) -> dict:
        """[writer] Add a figure (copy image + create caption) to the project."""
        try:
            project_path = resolve_project_path(project_dir)
            doc_dirs = {
                "manuscript": project_path / "01_manuscript",
                "supplementary": project_path / "02_supplementary",
            }
            doc_dir = doc_dirs.get(doc_type)
            if not doc_dir:
                return {"success": False, "error": f"Invalid doc_type: {doc_type}"}

            fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
            fig_dir.mkdir(parents=True, exist_ok=True)

            # Copy image
            src_image = Path(image_path)
            if not src_image.exists():
                return {"success": False, "error": f"Image not found: {image_path}"}

            dest_image = fig_dir / f"{name}{src_image.suffix}"
            shutil.copy2(src_image, dest_image)

            # Write caption
            if label is None:
                label = f"fig:{name.replace(' ', '_')}"
            caption_content = f"\\caption{{{caption}}}\n\\label{{{label}}}\n"
            caption_path = fig_dir / f"{name}.tex"
            caption_path.write_text(caption_content, encoding="utf-8")

            return {
                "success": True,
                "image_path": str(dest_image),
                "caption_path": str(caption_path),
                "label": label,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    @mcp.tool()
    def writer_remove_figure(
        project_dir: str,
        name: str,
        doc_type: Literal["manuscript", "supplementary"] = "manuscript",
    ) -> dict:
        """[writer] Remove a figure (image + caption) from the project."""
        try:
            project_path = resolve_project_path(project_dir)
            doc_dirs = {
                "manuscript": project_path / "01_manuscript",
                "supplementary": project_path / "02_supplementary",
            }
            doc_dir = doc_dirs.get(doc_type)
            if not doc_dir:
                return {"success": False, "error": f"Invalid doc_type: {doc_type}"}

            fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
            caption_path = fig_dir / f"{name}.tex"

            removed = []
            # Remove all image files with this name
            for ext in [
                ".png",
                ".jpg",
                ".jpeg",
                ".pdf",
                ".tif",
                ".tiff",
                ".eps",
                ".svg",
            ]:
                img_path = fig_dir / f"{name}{ext}"
                if img_path.exists():
                    img_path.unlink()
                    removed.append(str(img_path))

            # Remove caption
            if caption_path.exists():
                caption_path.unlink()
                removed.append(str(caption_path))

            if not removed:
                return {"success": False, "error": f"Figure not found: {name}"}

            return {"success": True, "removed": removed}
        except Exception as e:
            return {"success": False, "error": str(e)}


# EOF
