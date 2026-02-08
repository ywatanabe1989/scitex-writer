#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-08
# File: src/scitex_writer/_compile/content.py

"""Content/preview compilation for LaTeX snippets.

Compiles raw LaTeX content to PDF using the shell scripts layer:
  scripts/python/compile_content_document.py → builds .tex document
  scripts/shell/compile_content.sh → compiles to PDF via latexmk
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Literal, Optional


def _get_scripts_dir() -> Path:
    """Get the scripts directory relative to the package root."""
    # Package structure: src/scitex_writer/_compile/content.py
    # Scripts at: scripts/shell/ and scripts/python/
    pkg_dir = Path(__file__).resolve().parent.parent  # src/scitex_writer/
    # In installed package, scripts are at the project root
    # Try: project_root/scripts/ (development) or find via package data
    for candidate in [
        pkg_dir.parent.parent / "scripts",  # development: repo/scripts/
        pkg_dir / "_scripts",  # installed package fallback
    ]:
        if candidate.exists():
            return candidate
    raise FileNotFoundError("Cannot find scripts directory")


def compile_content(
    latex_content: str,
    project_dir: Optional[str] = None,
    color_mode: Literal["light", "dark"] = "light",
    name: str = "content",
    timeout: int = 60,
    keep_aux: bool = False,
) -> dict:
    """Compile raw LaTeX content to PDF.

    Creates a standalone document from the provided LaTeX content and compiles
    it to PDF. Supports light/dark color modes for comfortable viewing.

    Parameters
    ----------
    latex_content : str
        Raw LaTeX content. Can be a complete document (with \\documentclass)
        or body-only content (will be wrapped automatically).
    project_dir : str, optional
        Path to scitex-writer project. If provided, PDF is copied to
        the project's .preview/ directory.
    color_mode : str
        Color theme: 'light' (default) or 'dark' (Monaco #1E1E1E).
    name : str
        Output filename (without extension).
    timeout : int
        Compilation timeout in seconds.
    keep_aux : bool
        Keep auxiliary files after compilation.

    Returns
    -------
    dict
        Result with keys: success, output_pdf, temp_dir, color_mode,
        log, message/error.
    """
    # Sanitize name: strip .tex extension if present
    if name.endswith(".tex"):
        name = name[:-4]

    try:
        scripts_dir = _get_scripts_dir()
        doc_builder = scripts_dir / "python" / "compile_content_document.py"
        compiler = scripts_dir / "shell" / "compile_content.sh"

        temp_dir = Path(tempfile.mkdtemp(prefix=f"scitex_content_{name}_"))
        body_file = temp_dir / "body.tex"
        tex_file = temp_dir / f"{name}.tex"
        pdf_file = temp_dir / f"{name}.pdf"

        # Write body content
        body_file.write_text(latex_content, encoding="utf-8")

        # Step 1: Build complete LaTeX document
        is_complete = "\\documentclass" in latex_content
        build_cmd = [
            "python3",
            str(doc_builder),
            "--body-file",
            str(body_file),
            "--output",
            str(tex_file),
            "--color-mode",
            color_mode,
        ]
        if is_complete:
            build_cmd.append("--complete-document")

        build_result = subprocess.run(
            build_cmd,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if build_result.returncode != 0:
            return {
                "success": False,
                "output_pdf": None,
                "error": f"Document build failed: {build_result.stderr}",
            }

        # Step 2: Compile to PDF
        compile_cmd = [
            "bash",
            str(compiler),
            "--tex-file",
            str(tex_file),
            "--output-dir",
            str(temp_dir),
            "--job-name",
            name,
            "--timeout",
            str(timeout),
        ]
        if keep_aux:
            compile_cmd.append("--keep-aux")
        compile_cmd.append("--quiet")

        # Add preview dir if project_dir is provided
        preview_dir = None
        if project_dir:
            preview_dir = Path(project_dir).resolve() / ".preview"
            compile_cmd.extend(["--preview-dir", str(preview_dir)])

        compile_result = subprocess.run(
            compile_cmd,
            capture_output=True,
            text=True,
            timeout=timeout + 10,
        )

        # Read log file
        log_content = _read_log(temp_dir, name)

        # Determine final PDF path
        final_pdf = pdf_file
        if compile_result.returncode == 0 and preview_dir:
            preview_pdf = preview_dir / f"{name}.pdf"
            if preview_pdf.exists():
                final_pdf = preview_pdf

        if compile_result.returncode == 0 and pdf_file.exists():
            return {
                "success": True,
                "output_pdf": str(final_pdf),
                "temp_dir": str(temp_dir),
                "color_mode": color_mode,
                "log": log_content,
                "message": f"Content compiled successfully: {name}",
            }
        else:
            return {
                "success": False,
                "output_pdf": None,
                "temp_dir": str(temp_dir),
                "color_mode": color_mode,
                "log": log_content,
                "stdout": _truncate(compile_result.stdout),
                "stderr": _truncate(compile_result.stderr),
                "error": f"Compilation failed with exit code {compile_result.returncode}",
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Content compilation timed out after {timeout} seconds",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def _read_log(temp_dir: Path, name: str) -> str:
    """Read and truncate log file."""
    log_file = temp_dir / f"{name}.log"
    if log_file.exists():
        content = log_file.read_text(encoding="utf-8", errors="replace")
        return content[-5000:] if len(content) > 5000 else content
    return ""


def _truncate(text: str, limit: int = 2000) -> str:
    """Truncate text to limit."""
    return text[-limit:] if len(text) > limit else text


__all__ = ["compile_content"]

# EOF
