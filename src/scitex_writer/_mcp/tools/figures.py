#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_mcp/tools/figures.py

"""Figure MCP tools."""

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
from ..handlers._figures_pipeline import process as _process
from ..utils import resolve_project_path


def register_tools(mcp: FastMCP) -> None:
    """Register figure tools."""

    @mcp.tool()
    def writer_figures_render(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
        no_figs: bool = False,
        pptx: bool = False,
        crop: bool = False,
    ) -> dict:
        """Run the figure pipeline: image sources -> JPG -> gathered FINAL.tex.

        Tidies panel ids and captions, converts every source through the single
        Pillow backend (TIF/MMD/PNG -> JPG), tiles multi-panel figures into one
        composite, links the JPGs into jpg_for_compilation, fills a
        declared-but-missing figure with a placeholder, and assembles the compiled
        FINAL.tex (each float also written to _placeable/<number>.tex for inline
        \\scitexfig{<number>} placement). With no figures it emits a comment-only
        fallback header -- never a placeholder float. no_figs=True skips all image
        work; pptx=True also renders .pptx slides via LibreOffice; crop=True trims
        each JPG's uniform border. Returns {success, figures_compiled,
        captions_created, panel_captions_removed, renamed_panels, converted,
        composed, placeholders_created, cropped, figures, compiled_file,
        figures_enabled, fallback_header, skipped, warnings, error}.
        """
        return _process(project_dir, doc_type, no_figs, pptx, crop)

    @mcp.tool()
    def writer_figures_list(
        project_dir: str,
        extensions: Optional[List[str]] = None,
    ) -> dict:
        """List all figures in a writer project directory."""
        return _list_figures(project_dir, extensions)

    @mcp.tool()
    def writer_figures_convert(
        input_path: str,
        output_path: str,
        dpi: int = 300,
        quality: int = 95,
    ) -> dict:
        """Convert figure between formats (e.g., PDF to PNG)."""
        return _convert_figure(input_path, output_path, dpi, quality)

    @mcp.tool()
    def writer_figures_pdf_to_images(
        pdf_path: str,
        output_dir: Optional[str] = None,
        pages: Optional[Union[int, List[int]]] = None,
        dpi: int = 600,
        format: Literal["png", "jpg"] = "png",
    ) -> dict:
        """Render PDF pages as images."""
        return _pdf_to_images(pdf_path, output_dir, pages, dpi, format)

    @mcp.tool()
    def writer_figures_add(
        project_dir: str,
        name: str,
        image_path: str,
        caption: str,
        label: Optional[str] = None,
        doc_type: Literal["manuscript", "supplementary"] = "manuscript",
    ) -> dict:
        """Add a figure (copy image + create caption) to the project."""
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
    def writer_figures_remove(
        project_dir: str,
        name: str,
        doc_type: Literal["manuscript", "supplementary"] = "manuscript",
    ) -> dict:
        """Remove a figure (image + caption) from the project.

        Removes all associated files including those in subdirectories
        (jpg_for_compilation/, mermaid_originals/).
        """
        from scitex_writer.figures import remove

        return remove(project_dir, name, doc_type)

    @mcp.tool()
    def writer_figures_archive(
        project_dir: str,
        name: str,
        doc_type: Literal["manuscript", "supplementary"] = "manuscript",
    ) -> dict:
        """Move a figure to legacy/ instead of deleting.

        Moves all associated files (tex, images, mermaid sources) from
        caption_and_media/ to legacy/, preserving them for potential reuse.
        """
        from scitex_writer.figures import archive

        return archive(project_dir, name, doc_type)


# EOF
