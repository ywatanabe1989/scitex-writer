#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: src/scitex_writer/_mcp/handlers.py

"""
MCP Handler implementations for SciTeX Writer.

Provides handlers for LaTeX manuscript operations:
- clone_project: Create new writer project
- compile_manuscript/supplementary/revision: Compile documents
- get_project_info: Get project structure
- get_pdf: Get compiled PDF path
- list_document_types: List document types
- csv_to_latex/latex_to_csv: Table conversions
- pdf_to_images: Render PDF pages
- list_figures: List project figures
- convert_figure: Convert figure formats
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Literal, Optional, Union

from .utils import resolve_project_path, run_compile_script


def clone_project(
    project_dir: str,
    git_strategy: Literal["child", "parent", "origin", "none"] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
) -> dict:
    """Create a new writer project from template."""
    try:
        project_path = resolve_project_path(project_dir)

        if project_path.exists():
            return {
                "success": False,
                "error": f"Directory already exists: {project_path}",
            }

        repo_url = "https://github.com/ywatanabe1989/scitex-writer.git"
        cmd = ["git", "clone"]

        if branch:
            cmd.extend(["--branch", branch])
        elif tag:
            cmd.extend(["--branch", tag])

        cmd.extend([repo_url, str(project_path)])
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return {"success": False, "error": f"Git clone failed: {result.stderr}"}

        if git_strategy == "none":
            git_dir = project_path / ".git"
            if git_dir.exists():
                shutil.rmtree(git_dir)
        elif git_strategy == "child":
            git_dir = project_path / ".git"
            if git_dir.exists():
                shutil.rmtree(git_dir)
            subprocess.run(["git", "init"], cwd=str(project_path), capture_output=True)
            subprocess.run(
                ["git", "add", "."], cwd=str(project_path), capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit from scitex-writer template"],
                cwd=str(project_path),
                capture_output=True,
            )

        return {
            "success": True,
            "project_path": str(project_path),
            "git_strategy": git_strategy,
            "structure": {
                "00_shared": "Shared resources",
                "01_manuscript": "Main manuscript",
                "02_supplementary": "Supplementary materials",
                "03_revision": "Revision documents",
            },
            "message": f"Successfully created writer project at {project_path}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def compile_manuscript(
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
    """Compile manuscript to PDF."""
    project_path = resolve_project_path(project_dir)
    return run_compile_script(
        project_path,
        "manuscript",
        timeout=timeout,
        no_figs=no_figs,
        no_tables=no_tables,
        no_diff=no_diff,
        draft=draft,
        dark_mode=dark_mode,
        quiet=quiet,
        verbose=verbose,
    )


def compile_supplementary(
    project_dir: str,
    timeout: int = 300,
    no_figs: bool = False,
    no_tables: bool = False,
    no_diff: bool = False,
    draft: bool = False,
    quiet: bool = False,
) -> dict:
    """Compile supplementary materials to PDF."""
    project_path = resolve_project_path(project_dir)
    return run_compile_script(
        project_path,
        "supplementary",
        timeout=timeout,
        no_figs=no_figs,
        no_tables=no_tables,
        no_diff=no_diff,
        draft=draft,
        quiet=quiet,
    )


def compile_revision(
    project_dir: str,
    track_changes: bool = False,
    timeout: int = 300,
    no_diff: bool = True,
    draft: bool = False,
    quiet: bool = False,
) -> dict:
    """Compile revision document to PDF."""
    project_path = resolve_project_path(project_dir)
    return run_compile_script(
        project_path,
        "revision",
        timeout=timeout,
        no_diff=no_diff,
        draft=draft,
        quiet=quiet,
        track_changes=track_changes,
    )


def get_project_info(project_dir: str) -> dict:
    """Get writer project information."""
    try:
        project_path = resolve_project_path(project_dir)

        if not project_path.exists():
            return {"success": False, "error": f"Project not found: {project_path}"}

        dirs = {
            "shared": project_path / "00_shared",
            "manuscript": project_path / "01_manuscript",
            "supplementary": project_path / "02_supplementary",
            "revision": project_path / "03_revision",
            "scripts": project_path / "scripts",
        }

        pdfs = {
            "manuscript": project_path / "01_manuscript" / "manuscript.pdf",
            "supplementary": project_path / "02_supplementary" / "supplementary.pdf",
            "revision": project_path / "03_revision" / "revision.pdf",
        }

        compiled_pdfs = {k: str(v) if v.exists() else None for k, v in pdfs.items()}

        git_root = None
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"],
                cwd=str(project_path),
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                git_root = result.stdout.strip()
        except Exception:
            pass

        return {
            "success": True,
            "project_name": project_path.name,
            "project_dir": str(project_path),
            "git_root": git_root,
            "documents": {k: str(v) for k, v in dirs.items() if v.exists()},
            "compiled_pdfs": compiled_pdfs,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_pdf(
    project_dir: str,
    doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
) -> dict:
    """Get path to compiled PDF."""
    try:
        project_path = resolve_project_path(project_dir)
        pdf_paths = {
            "manuscript": project_path / "01_manuscript" / "manuscript.pdf",
            "supplementary": project_path / "02_supplementary" / "supplementary.pdf",
            "revision": project_path / "03_revision" / "revision.pdf",
        }

        pdf_path = pdf_paths.get(doc_type)
        if pdf_path and pdf_path.exists():
            return {
                "success": True,
                "exists": True,
                "doc_type": doc_type,
                "pdf_path": str(pdf_path),
            }
        else:
            return {
                "success": True,
                "exists": False,
                "doc_type": doc_type,
                "pdf_path": None,
                "message": f"No compiled PDF found for {doc_type}",
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_document_types() -> dict:
    """List available document types."""
    return {
        "success": True,
        "document_types": [
            {"id": "manuscript", "name": "Manuscript", "directory": "01_manuscript"},
            {
                "id": "supplementary",
                "name": "Supplementary",
                "directory": "02_supplementary",
            },
            {
                "id": "revision",
                "name": "Revision",
                "directory": "03_revision",
                "supports_track_changes": True,
            },
        ],
        "shared_directory": {"id": "shared", "directory": "00_shared"},
    }


def csv_to_latex(
    csv_path: str,
    output_path: Optional[str] = None,
    caption: Optional[str] = None,
    label: Optional[str] = None,
    longtable: bool = False,
) -> dict:
    """Convert CSV file to LaTeX table."""
    try:
        import pandas as pd

        csv_file = Path(csv_path)
        if not csv_file.exists():
            return {"success": False, "error": f"CSV file not found: {csv_path}"}

        df = pd.read_csv(csv_file)
        base_name = csv_file.stem

        alignments = []
        for col in df.columns:
            try:
                pd.to_numeric(df[col], errors="raise")
                alignments.append("r")
            except Exception:
                alignments.append("l")

        lines = []
        if longtable:
            lines.append("\\begin{longtable}{" + "".join(alignments) + "}")
        else:
            lines.extend(
                [
                    "\\begin{table}[htbp]",
                    "\\centering",
                    "\\begin{tabular}{" + "".join(alignments) + "}",
                ]
            )

        lines.append("\\toprule")
        lines.append(" & ".join([f"\\textbf{{{col}}}" for col in df.columns]) + " \\\\")
        lines.append("\\midrule")

        for _, row in df.iterrows():
            values = [str(v) if pd.notna(v) else "--" for v in row]
            lines.append(" & ".join(values) + " \\\\")

        lines.append("\\bottomrule")

        if longtable:
            if caption:
                lines.append(f"\\caption{{{caption}}}")
            if label:
                lines.append(f"\\label{{{label}}}")
            lines.append("\\end{longtable}")
        else:
            lines.append("\\end{tabular}")
            if caption:
                lines.append(f"\\caption{{{caption}}}")
            lines.append(f"\\label{{{label or 'tab:' + base_name}}}")
            lines.append("\\end{table}")

        latex_content = "\n".join(lines)
        if output_path:
            Path(output_path).write_text(latex_content, encoding="utf-8")

        return {
            "success": True,
            "latex_content": latex_content,
            "output_path": output_path,
            "rows": len(df),
            "columns": len(df.columns),
        }
    except ImportError:
        return {"success": False, "error": "pandas required: pip install pandas"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def latex_to_csv(
    latex_path: str,
    output_path: Optional[str] = None,
    table_index: int = 0,
) -> dict:
    """Convert LaTeX table to CSV."""
    try:
        import pandas as pd

        latex_file = Path(latex_path)
        if not latex_file.exists():
            return {"success": False, "error": f"LaTeX file not found: {latex_path}"}

        content = latex_file.read_text(encoding="utf-8")
        pattern = r"\\begin\{tabular\}.*?\\end\{tabular\}"
        matches = list(re.finditer(pattern, content, re.DOTALL))

        if not matches:
            return {"success": False, "error": "No tabular environment found"}
        if table_index >= len(matches):
            return {
                "success": False,
                "error": f"Table index {table_index} out of range",
            }

        table_content = matches[table_index].group()
        rows = []
        for line in table_content.split("\\\\"):
            if any(
                x in line
                for x in ["\\begin", "\\end", "\\toprule", "\\midrule", "\\bottomrule"]
            ):
                continue
            cells = [
                re.sub(r"\\[a-zA-Z]+\{([^}]*)\}", r"\1", c.strip())
                for c in line.split("&")
            ]
            if any(cells):
                rows.append(cells)

        if not rows:
            return {"success": False, "error": "Could not parse table"}

        df = pd.DataFrame(rows[1:], columns=rows[0] if rows else None)
        if output_path:
            df.to_csv(output_path, index=False)

        return {
            "success": True,
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(5).to_dict(),
            "output_path": output_path,
        }
    except ImportError:
        return {"success": False, "error": "pandas required: pip install pandas"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def pdf_to_images(
    pdf_path: str,
    output_dir: Optional[str] = None,
    pages: Optional[Union[int, List[int]]] = None,
    dpi: int = 150,
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


__all__ = [
    "clone_project",
    "compile_manuscript",
    "compile_supplementary",
    "compile_revision",
    "get_project_info",
    "get_pdf",
    "list_document_types",
    "csv_to_latex",
    "latex_to_csv",
    "pdf_to_images",
    "list_figures",
    "convert_figure",
]

# EOF
