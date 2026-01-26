#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/figures.py

"""Figure management functions.

Usage::

    import scitex_writer as sw

    # List figures in project
    result = sw.figures.list("./my-paper")

    # Add a figure
    sw.figures.add("./my-paper", "fig01", "./plot.png", "Results plot")

    # Convert figure format
    sw.figures.convert("input.pdf", "output.png")
"""

import shutil as _shutil
from pathlib import Path as _Path
from typing import List as _List
from typing import Literal as _Literal
from typing import Optional as _Optional
from typing import Union as _Union

from ._mcp.handlers import convert_figure as _convert_figure
from ._mcp.handlers import list_figures as _list_figures
from ._mcp.handlers import pdf_to_images as _pdf_to_images
from ._mcp.utils import resolve_project_path as _resolve_project_path


def list(
    project_dir: str,
    extensions: _Optional[_List[str]] = None,
) -> dict:
    """List all figures in a writer project.

    Args:
        project_dir: Path to scitex-writer project.
        extensions: File extensions to include (default: common image formats).

    Returns:
        Dict with figures list and count.
    """
    return _list_figures(project_dir, extensions)


def add(
    project_dir: str,
    name: str,
    image_path: str,
    caption: str,
    label: _Optional[str] = None,
    doc_type: _Literal["manuscript", "supplementary"] = "manuscript",
) -> dict:
    """Add a figure (copy image + create caption) to the project.

    Args:
        project_dir: Path to scitex-writer project.
        name: Figure name (without extension).
        image_path: Path to source image file.
        caption: Figure caption text.
        label: LaTeX label (default: fig:<name>).
        doc_type: Target document type.

    Returns:
        Dict with image_path, caption_path, label.
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

        fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
        fig_dir.mkdir(parents=True, exist_ok=True)

        src_image = _Path(image_path)
        if not src_image.exists():
            return {"success": False, "error": f"Image not found: {image_path}"}

        dest_image = fig_dir / f"{name}{src_image.suffix}"
        _shutil.copy2(src_image, dest_image)

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


def remove(
    project_dir: str,
    name: str,
    doc_type: _Literal["manuscript", "supplementary"] = "manuscript",
) -> dict:
    """Remove a figure (image + caption) from the project.

    Args:
        project_dir: Path to scitex-writer project.
        name: Figure name (without extension).
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

        fig_dir = doc_dir / "contents" / "figures" / "caption_and_media"
        caption_path = fig_dir / f"{name}.tex"

        removed = []
        for ext in [".png", ".jpg", ".jpeg", ".pdf", ".tif", ".tiff", ".eps", ".svg"]:
            img_path = fig_dir / f"{name}{ext}"
            if img_path.exists():
                img_path.unlink()
                removed.append(str(img_path))

        if caption_path.exists():
            caption_path.unlink()
            removed.append(str(caption_path))

        if not removed:
            return {"success": False, "error": f"Figure not found: {name}"}

        return {"success": True, "removed": removed}
    except Exception as e:
        return {"success": False, "error": str(e)}


def convert(
    input_path: str,
    output_path: str,
    dpi: int = 300,
    quality: int = 95,
) -> dict:
    """Convert figure between formats (e.g., PDF to PNG).

    Args:
        input_path: Source image path.
        output_path: Destination image path.
        dpi: Resolution for PDF conversion.
        quality: JPEG quality (1-100).

    Returns:
        Dict with input_path and output_path.
    """
    return _convert_figure(input_path, output_path, dpi, quality)


def pdf_to_images(
    pdf_path: str,
    output_dir: _Optional[str] = None,
    pages: _Optional[_Union[int, _List[int]]] = None,
    dpi: int = 150,
    format: _Literal["png", "jpg"] = "png",
) -> dict:
    """Render PDF pages as images.

    Args:
        pdf_path: Path to PDF file.
        output_dir: Output directory (default: temp dir).
        pages: Page numbers to render (0-indexed).
        dpi: Resolution.
        format: Output format.

    Returns:
        Dict with images list and output_dir.
    """
    return _pdf_to_images(pdf_path, output_dir, pages, dpi, format)


__all__ = ["list", "add", "remove", "convert", "pdf_to_images"]

# EOF
