#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-08
# File: src/scitex_writer/_compile/content.py

"""Content/preview compilation for LaTeX snippets.

Compiles raw LaTeX content to PDF using the shell scripts layer:
  scripts/python/tex_snippet2full.py → builds .tex document
  scripts/shell/compile_content.sh → compiles to PDF via latexmk
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
from typing import Literal, Optional

from .._dataclasses import CompilationResult


def _get_scripts_dir(project_dir: Optional[str] = None) -> Path:
    """Get the scripts directory, preferring package scripts over project.

    Search order:
    1. repo/scripts/ (development mode - always up to date)
    2. package/_scripts/ (installed package fallback)
    3. project_dir/scripts/ (user's project - may be from old template)
    """
    # First priority: package/development scripts (always up to date)
    pkg_dir = Path(__file__).resolve().parent.parent  # src/scitex_writer/
    for candidate in [
        pkg_dir.parent.parent / "scripts",  # development: repo/scripts/
        pkg_dir / "_scripts",  # installed package fallback
    ]:
        if candidate.exists() and (candidate / "shell").exists():
            return candidate

    # Fallback: project's own scripts directory (may be outdated clone)
    if project_dir:
        proj_scripts = Path(project_dir) / "scripts"
        if proj_scripts.exists() and (proj_scripts / "shell").exists():
            return proj_scripts

    raise FileNotFoundError("Cannot find scripts directory")


def compile_content(
    latex_content: str,
    project_dir: Optional[str] = None,
    color_mode: Literal["light", "dark"] = "light",
    name: str = "content",
    timeout: int = 60,
    keep_aux: bool = False,
) -> CompilationResult:
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
    CompilationResult
        Unified compile-result dataclass. Always carries ``success``,
        ``exit_code``, ``stdout``, ``stderr``, ``output_pdf``,
        ``log_file``, ``color_mode``, ``temp_dir``, ``message`` —
        regardless of which code path (success / failure / timeout /
        internal exception) the call took.

        Migrated from the legacy ad-hoc dict return in 2026-06-10 (G1
        of the proj-scitex-hub triage, follow-up to G2 #124 atomic
        publish + G3 #125 flock serialization). Callers that previously
        did ``result["success"]`` now use ``result.success``;
        ``result.get("temp_dir")`` becomes ``result.temp_dir``; etc.
        The Django consumer can serialize the dataclass via
        ``dataclasses.asdict(result)`` if a dict-shaped JSON payload is
        still required on the wire.
    """
    # Sanitize name: strip .tex extension if present
    if name.endswith(".tex"):
        name = name[:-4]

    try:
        scripts_dir = _get_scripts_dir(project_dir)
        doc_builder = scripts_dir / "python" / "tex_snippet2full.py"
        compiler = scripts_dir / "shell" / "compile_content.sh"

        temp_dir = Path(tempfile.mkdtemp(prefix=f"scitex_content_{name}_"))
        body_file = temp_dir / "body.tex"
        tex_file = temp_dir / f"{name}.tex"
        pdf_file = temp_dir / f"{name}.pdf"
        log_path = temp_dir / f"{name}.log"

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
            return CompilationResult(
                success=False,
                exit_code=build_result.returncode,
                stdout=_truncate(build_result.stdout),
                stderr=_truncate(build_result.stderr),
                output_pdf=None,
                log_file=None,
                color_mode=color_mode,
                temp_dir=temp_dir,
                message=f"Document build failed: {_truncate(build_result.stderr, 200)}",
            )

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

        # Determine final PDF path
        final_pdf: Optional[Path] = pdf_file if pdf_file.exists() else None
        if compile_result.returncode == 0 and preview_dir:
            preview_pdf = preview_dir / f"{name}.pdf"
            if preview_pdf.exists():
                final_pdf = preview_pdf

        # log_file: the on-disk log path if it exists, else None.
        log_file: Optional[Path] = log_path if log_path.exists() else None

        if compile_result.returncode == 0 and pdf_file.exists():
            return CompilationResult(
                success=True,
                exit_code=0,
                stdout=_truncate(compile_result.stdout),
                stderr=_truncate(compile_result.stderr),
                output_pdf=final_pdf,
                log_file=log_file,
                color_mode=color_mode,
                temp_dir=temp_dir,
                message=f"Content compiled successfully: {name}",
            )
        return CompilationResult(
            success=False,
            exit_code=compile_result.returncode,
            stdout=_truncate(compile_result.stdout),
            stderr=_truncate(compile_result.stderr),
            output_pdf=None,
            log_file=log_file,
            color_mode=color_mode,
            temp_dir=temp_dir,
            message=f"Compilation failed with exit code {compile_result.returncode}",
        )

    except subprocess.TimeoutExpired:
        # exit_code 124 is the POSIX `timeout(1)` convention; preserves
        # caller's ability to distinguish "took too long" from "latexmk
        # rejected the source" (which surfaces as 1 / 12 etc.).
        return CompilationResult(
            success=False,
            exit_code=124,
            stdout="",
            stderr=f"Content compilation timed out after {timeout} seconds",
            output_pdf=None,
            log_file=None,
            color_mode=color_mode,
            temp_dir=None,
            message=f"Content compilation timed out after {timeout} seconds",
        )
    except Exception as e:
        # exit_code -1 = our own internal error wrapper, never produced
        # by latexmk or `timeout`. Lets the Django view branch on
        # `exit_code == -1` to render "internal error, retry" rather
        # than the latexmk-flavoured failure UX.
        return CompilationResult(
            success=False,
            exit_code=-1,
            stdout="",
            stderr=str(e),
            output_pdf=None,
            log_file=None,
            color_mode=color_mode,
            temp_dir=None,
            message=str(e),
        )


def _truncate(text: str, limit: int = 2000) -> str:
    """Truncate text to limit. Used for stdout/stderr capture so the
    CompilationResult never carries multi-MB blobs through the Django
    JSON layer. The full latexmk log stays available via
    ``CompilationResult.log_file`` (path to the on-disk .log)."""
    return text[-limit:] if len(text) > limit else text


__all__ = ["compile_content"]

# EOF
