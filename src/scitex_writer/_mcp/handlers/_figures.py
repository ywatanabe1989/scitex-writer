#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_figures.py

"""Figure handlers: pdf_to_images, list_figures, convert_figure."""


import tempfile
from pathlib import Path
from typing import List, Literal, Optional, Union

from ..utils import resolve_project_path


def pdf_to_images(
    pdf_path: str,
    output_dir: Optional[str] = None,
    pages: Optional[Union[int, List[int]]] = None,
    dpi: int = 600,
    format: Literal["png", "jpg"] = "png",
) -> dict:
    """Render PDF pages as images."""
    try:
        from pdf2image import convert_from_path

        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            return {"success": False, "error": f"PDF not found: {pdf_path}"}

        out_dir = (
            Path(output_dir)
            if output_dir
            else Path(tempfile.mkdtemp(prefix="pdf_images_"))
        )
        out_dir.mkdir(parents=True, exist_ok=True)

        if pages is not None:
            if isinstance(pages, int):
                pages = [pages]
            first_page, last_page = min(pages) + 1, max(pages) + 1
        else:
            first_page = last_page = None

        images = convert_from_path(
            pdf_file, dpi=dpi, first_page=first_page, last_page=last_page
        )
        image_paths = []
        for i, image in enumerate(images):
            page_num = pages[i] if pages else i
            filename = f"{pdf_file.stem}_page_{page_num:03d}.{format}"
            image_path = out_dir / filename
            image.save(str(image_path), format.upper())
            image_paths.append(str(image_path))

        return {
            "success": True,
            "images": image_paths,
            "count": len(image_paths),
            "output_dir": str(out_dir),
        }
    except ImportError:
        return {"success": False, "error": "pdf2image required: pip install pdf2image"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_figures(project_dir: str, extensions: Optional[List[str]] = None) -> dict:
    """List figures in project."""
    try:
        project_path = resolve_project_path(project_dir)
        if extensions is None:
            extensions = [
                ".png",
                ".pdf",
                ".jpg",
                ".jpeg",
                ".tif",
                ".tiff",
                ".eps",
                ".svg",
            ]
        extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]

        figure_dirs = [
            project_path / "01_manuscript" / "contents" / "figures",
            project_path / "02_supplementary" / "contents" / "figures",
            project_path / "00_shared" / "figures",
        ]

        figures = []
        for fig_dir in figure_dirs:
            if fig_dir.exists():
                for ext in extensions:
                    for fig_path in fig_dir.rglob(f"*{ext}"):
                        figures.append(
                            {
                                "path": str(fig_path),
                                "name": fig_path.name,
                                "extension": fig_path.suffix,
                                "size_bytes": fig_path.stat().st_size,
                            }
                        )

        return {"success": True, "figures": figures, "count": len(figures)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def convert_figure(
    input_path: str, output_path: str, dpi: int = 300, quality: int = 95
) -> dict:
    """Convert figure between formats."""
    try:
        from PIL import Image

        input_file, output_file = Path(input_path), Path(output_path)
        if not input_file.exists():
            return {"success": False, "error": f"Input not found: {input_path}"}

        output_file.parent.mkdir(parents=True, exist_ok=True)

        if input_file.suffix.lower() == ".pdf":
            try:
                from pdf2image import convert_from_path

                images = convert_from_path(input_file, dpi=dpi)
                img = images[0] if images else None
                if not img:
                    return {"success": False, "error": "Could not read PDF"}
            except ImportError:
                return {
                    "success": False,
                    "error": "pdf2image required for PDF conversion",
                }
        else:
            img = Image.open(input_file)

        if output_file.suffix.lower() in [".jpg", ".jpeg"] and img.mode in [
            "RGBA",
            "P",
        ]:
            img = img.convert("RGB")

        if output_file.suffix.lower() in [".jpg", ".jpeg"]:
            img.save(output_file, quality=quality)
        else:
            img.save(output_file)

        return {
            "success": True,
            "input_path": str(input_file),
            "output_path": str(output_file),
        }
    except ImportError:
        return {"success": False, "error": "Pillow required: pip install Pillow"}
    except Exception as e:
        return {"success": False, "error": str(e)}


# EOF
