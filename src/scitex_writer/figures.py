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
from ._mcp.handlers._figures_pipeline import process as _process
from ._mcp.utils import resolve_project_path as _resolve_project_path

try:
    from scitex_dev.decorators import supports_return_as as _supports_return_as
except ImportError:

    def _supports_return_as(fn):
        return fn


@_supports_return_as
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


@_supports_return_as
def add(
    project_dir: str,
    name: str,
    image_path: str,
    caption: str,
    label: _Optional[str] = None,
    doc_type: _Literal["manuscript", "supplementary"] = "manuscript",
) -> dict:
    """Add a figure (copy image + create caption) to the project.

    Design note (2026-06-12, operator decision 1b):
        Figure *ingestion* (this function) keeps `shutil.copy2` — the
        source path is a user-owned file outside the project, and the
        project must remain self-contained after ingestion. Symlinking
        here would create a dangling reference if the user later moves
        or deletes the source.

        In contrast, figure *placement into jpg_for_compilation*
        (`scripts/shell/modules/process_figures_modules/02_format_conversion.src`)
        was switched to a symlink — that target lives entirely inside the
        project's derived tree and benefits from automatic propagation of
        upstream edits.

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


def _find_all_figure_files(fig_dir: _Path, name: str) -> list:
    """Find all files associated with a figure name across all subdirectories."""
    files = []
    extensions = [
        ".tex",
        ".png",
        ".jpg",
        ".jpeg",
        ".pdf",
        ".tif",
        ".tiff",
        ".eps",
        ".svg",
        ".mmd",
    ]
    # Base directory
    for ext in extensions:
        p = fig_dir / f"{name}{ext}"
        if p.exists() or p.is_symlink():
            files.append(p)
    # Subdirectories: jpg_for_compilation, mermaid_originals
    for subdir_name in ["jpg_for_compilation", "mermaid_originals"]:
        subdir = fig_dir / subdir_name
        if subdir.is_dir():
            for ext in extensions:
                p = subdir / f"{name}{ext}"
                if p.exists() or p.is_symlink():
                    files.append(p)
    return files


@_supports_return_as
def remove(
    project_dir: str,
    name: str,
    doc_type: _Literal["manuscript", "supplementary"] = "manuscript",
) -> dict:
    """Remove a figure (image + caption) from the project.

    Removes all associated files including those in subdirectories
    (jpg_for_compilation/, mermaid_originals/).

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
        all_files = _find_all_figure_files(fig_dir, name)

        removed = []
        for p in all_files:
            p.unlink()
            removed.append(str(p))

        if not removed:
            return {"success": False, "error": f"Figure not found: {name}"}

        return {"success": True, "removed": removed}
    except Exception as e:
        return {"success": False, "error": str(e)}


@_supports_return_as
def archive(
    project_dir: str,
    name: str,
    doc_type: _Literal["manuscript", "supplementary"] = "manuscript",
) -> dict:
    """Move a figure to legacy/ instead of deleting.

    Moves all associated files (tex, images, mermaid sources) from
    caption_and_media/ to legacy/, preserving them for potential reuse.

    Args:
        project_dir: Path to scitex-writer project.
        name: Figure name (without extension).
        doc_type: Document type.

    Returns:
        Dict with archived file paths.
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
        legacy_dir = doc_dir / "contents" / "figures" / "legacy"
        legacy_dir.mkdir(parents=True, exist_ok=True)

        all_files = _find_all_figure_files(fig_dir, name)

        archived = []
        for p in all_files:
            dest = legacy_dir / p.name
            _shutil.move(str(p), str(dest))
            archived.append({"from": str(p), "to": str(dest)})

        if not archived:
            return {"success": False, "error": f"Figure not found: {name}"}

        return {"success": True, "archived": archived}
    except Exception as e:
        return {"success": False, "error": str(e)}


@_supports_return_as
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


@_supports_return_as
def pdf_to_images(
    pdf_path: str,
    output_dir: _Optional[str] = None,
    pages: _Optional[_Union[int, _List[int]]] = None,
    dpi: int = 600,
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


@_supports_return_as
def render(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision"] = "manuscript",
    no_figs: bool = False,
    pptx: bool = False,
    crop: bool = False,
) -> dict:
    """Run the engine's figure pipeline for ``doc_type``.

    The pure-Python port of ``scripts/shell/modules/process_figures.sh``: tidies
    panel ids and captions, converts every source image through the single Pillow
    backend (TIF/MMD/PNG -> JPG), tiles multi-panel figures into one composite,
    links the results into ``jpg_for_compilation``, fills a declared-but-missing
    figure with a placeholder, and assembles the compiled ``FINAL.tex`` (each
    float also written to ``_placeable/<number>.tex`` for inline
    ``\\scitexfig{<number>}`` placement). With no figures at all it emits a
    comment-only fallback header -- never a placeholder float.

    ``no_figs=True`` skips all image work and disables figures (the shell's
    ``no_figs``); ``pptx=True`` also renders ``NN_*.pptx`` slides through
    LibreOffice; ``crop=True`` trims each compilation JPG's uniform border.
    Returns ``{success, figures_compiled, captions_created, panel_captions_removed,
    renamed_panels, converted, composed, placeholders_created, cropped, figures,
    compiled_file, figures_enabled, fallback_header, skipped, warnings, error}``.
    """
    return _process(project_dir, doc_type, no_figs, pptx, crop)


__all__ = [
    "list",
    "add",
    "remove",
    "archive",
    "convert",
    "pdf_to_images",
    "render",
]

# EOF
