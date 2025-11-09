#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compilation functions for scitex-writer.

Provides Python wrappers around shell compilation scripts.
"""

from pathlib import Path
from typing import Optional
import subprocess
import os


def compile_manuscript(
    project_dir: Path,
    no_figs: bool = False,
    do_p2t: bool = False,
    crop_tif: bool = False,
    verbose: bool = False,
) -> "CompilationResult":
    """
    Compile manuscript document.

    Args:
        project_dir: Path to project directory
        no_figs: Skip figure processing
        do_p2t: Convert PPTX to TIF
        crop_tif: Crop TIF files
        verbose: Show verbose output

    Returns:
        CompilationResult with status and paths
    """
    from .writer import CompilationResult

    return _run_compilation(
        project_dir=project_dir,
        doc_type="manuscript",
        no_figs=no_figs,
        do_p2t=do_p2t,
        crop_tif=crop_tif,
        verbose=verbose,
    )


def compile_supplementary(
    project_dir: Path,
    no_figs: bool = False,
    do_p2t: bool = False,
    crop_tif: bool = False,
    verbose: bool = False,
) -> "CompilationResult":
    """
    Compile supplementary document.

    Args:
        project_dir: Path to project directory
        no_figs: Skip figure processing
        do_p2t: Convert PPTX to TIF
        crop_tif: Crop TIF files
        verbose: Show verbose output

    Returns:
        CompilationResult with status and paths
    """
    from .writer import CompilationResult

    return _run_compilation(
        project_dir=project_dir,
        doc_type="supplementary",
        no_figs=no_figs,
        do_p2t=do_p2t,
        crop_tif=crop_tif,
        verbose=verbose,
    )


def compile_revision(
    project_dir: Path,
    no_figs: bool = False,
    do_p2t: bool = False,
    crop_tif: bool = False,
    verbose: bool = False,
) -> "CompilationResult":
    """
    Compile revision document.

    Args:
        project_dir: Path to project directory
        no_figs: Skip figure processing
        do_p2t: Convert PPTX to TIF
        crop_tif: Crop TIF files
        verbose: Show verbose output

    Returns:
        CompilationResult with status and paths
    """
    from .writer import CompilationResult

    return _run_compilation(
        project_dir=project_dir,
        doc_type="revision",
        no_figs=no_figs,
        do_p2t=do_p2t,
        crop_tif=crop_tif,
        verbose=verbose,
    )


def _run_compilation(
    project_dir: Path,
    doc_type: str,
    no_figs: bool = False,
    do_p2t: bool = False,
    crop_tif: bool = False,
    verbose: bool = False,
) -> "CompilationResult":
    """
    Internal function to run compilation.

    Args:
        project_dir: Path to project directory
        doc_type: Document type (manuscript, supplementary, revision)
        no_figs: Skip figure processing
        do_p2t: Convert PPTX to TIF
        crop_tif: Crop TIF files
        verbose: Show verbose output

    Returns:
        CompilationResult with status and paths
    """
    from .writer import CompilationResult

    project_dir = Path(project_dir).resolve()
    script_path = project_dir / "scripts" / "shell" / f"compile_{doc_type}.sh"

    if not script_path.exists():
        return CompilationResult(
            success=False,
            error=f"Compilation script not found: {script_path}",
        )

    # Build command
    cmd = [str(script_path)]
    if no_figs:
        cmd.append("--no_figs")
    if do_p2t:
        cmd.append("--do_p2t")
    if crop_tif:
        cmd.append("--crop_tif")
    if verbose:
        cmd.append("--verbose")

    # Run compilation
    try:
        result = subprocess.run(
            cmd,
            cwd=project_dir,
            capture_output=not verbose,
            text=True,
            check=True,
        )

        # Determine output paths
        doc_dirs = {
            "manuscript": "01_manuscript",
            "supplementary": "02_supplementary",
            "revision": "03_revision",
        }
        doc_dir = doc_dirs.get(doc_type, f"01_{doc_type}")
        pdf_path = project_dir / doc_dir / f"{doc_type}.pdf"
        tex_path = project_dir / doc_dir / f"{doc_type}_compiled.tex"

        return CompilationResult(
            success=True,
            pdf_path=pdf_path if pdf_path.exists() else None,
            tex_path=tex_path if tex_path.exists() else None,
        )

    except subprocess.CalledProcessError as e:
        return CompilationResult(
            success=False,
            error=f"Compilation failed: {e.stderr if e.stderr else str(e)}",
        )
    except Exception as e:
        return CompilationResult(
            success=False,
            error=f"Unexpected error: {str(e)}",
        )


__all__ = [
    "compile_manuscript",
    "compile_supplementary",
    "compile_revision",
]
