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
    no_tables: bool = False,
    no_diff: bool = False,
    draft: bool = False,
    dark_mode: bool = False,
    do_p2t: bool = False,
    crop_tif: bool = False,
    verbose: bool = False,
    force: bool = False,
) -> "CompilationResult":
    """
    Compile manuscript document.

    Args:
        project_dir: Path to project directory
        no_figs: Skip figure processing (~4s faster)
        no_tables: Skip table processing (~4s faster)
        no_diff: Skip diff generation (~17s faster)
        draft: Single-pass compilation (~5s faster)
        dark_mode: Dark mode (black background, white text)
        do_p2t: Convert PPTX to TIF
        crop_tif: Crop TIF files
        verbose: Show verbose output
        force: Force full recompilation

    Returns:
        CompilationResult with status and paths
    """
    from .writer import CompilationResult

    return _run_compilation(
        project_dir=project_dir,
        doc_type="manuscript",
        no_figs=no_figs,
        no_tables=no_tables,
        no_diff=no_diff,
        draft=draft,
        dark_mode=dark_mode,
        do_p2t=do_p2t,
        crop_tif=crop_tif,
        verbose=verbose,
        force=force,
    )


def compile_supplementary(
    project_dir: Path,
    no_figs: bool = False,
    no_tables: bool = False,
    no_diff: bool = False,
    draft: bool = False,
    dark_mode: bool = False,
    do_p2t: bool = False,
    crop_tif: bool = False,
    verbose: bool = False,
    force: bool = False,
) -> "CompilationResult":
    """
    Compile supplementary document.

    Args:
        project_dir: Path to project directory
        no_figs: Skip figure processing (~4s faster)
        no_tables: Skip table processing (~4s faster)
        no_diff: Skip diff generation (~17s faster)
        draft: Single-pass compilation (~5s faster)
        dark_mode: Dark mode (black background, white text)
        do_p2t: Convert PPTX to TIF
        crop_tif: Crop TIF files
        verbose: Show verbose output
        force: Force full recompilation

    Returns:
        CompilationResult with status and paths
    """
    from .writer import CompilationResult

    return _run_compilation(
        project_dir=project_dir,
        doc_type="supplementary",
        no_figs=no_figs,
        no_tables=no_tables,
        no_diff=no_diff,
        draft=draft,
        dark_mode=dark_mode,
        do_p2t=do_p2t,
        crop_tif=crop_tif,
        verbose=verbose,
        force=force,
    )


def compile_revision(
    project_dir: Path,
    no_figs: bool = False,
    no_tables: bool = False,
    draft: bool = False,
    dark_mode: bool = False,
    do_p2t: bool = False,
    crop_tif: bool = False,
    verbose: bool = False,
    force: bool = False,
) -> "CompilationResult":
    """
    Compile revision document.

    Args:
        project_dir: Path to project directory
        no_figs: Skip figure processing (~4s faster)
        no_tables: Skip table processing (~4s faster)
        draft: Single-pass compilation (~5s faster)
        dark_mode: Dark mode (black background, white text)
        do_p2t: Convert PPTX to TIF
        crop_tif: Crop TIF files
        verbose: Show verbose output
        force: Force full recompilation

    Note:
        Revision documents skip diff generation by default (changes shown inline)

    Returns:
        CompilationResult with status and paths
    """
    from .writer import CompilationResult

    return _run_compilation(
        project_dir=project_dir,
        doc_type="revision",
        no_figs=no_figs,
        no_tables=no_tables,
        draft=draft,
        dark_mode=dark_mode,
        do_p2t=do_p2t,
        crop_tif=crop_tif,
        verbose=verbose,
        force=force,
    )


def _run_compilation(
    project_dir: Path,
    doc_type: str,
    no_figs: bool = False,
    no_tables: bool = False,
    no_diff: bool = False,
    draft: bool = False,
    dark_mode: bool = False,
    do_p2t: bool = False,
    crop_tif: bool = False,
    verbose: bool = False,
    force: bool = False,
) -> "CompilationResult":
    """
    Internal function to run compilation.

    Args:
        project_dir: Path to project directory
        doc_type: Document type (manuscript, supplementary, revision)
        no_figs: Skip figure processing
        no_tables: Skip table processing
        no_diff: Skip diff generation
        draft: Single-pass compilation
        dark_mode: Dark mode (black background, white text)
        do_p2t: Convert PPTX to TIF
        crop_tif: Crop TIF files
        verbose: Show verbose output
        force: Force full recompilation

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
    if no_tables:
        cmd.append("--no_tables")
    if no_diff:
        cmd.append("--no_diff")
    if draft:
        cmd.append("--draft")
    if dark_mode:
        cmd.append("--dark_mode")
    if do_p2t:
        cmd.append("--ppt2tif")
    if crop_tif:
        cmd.append("--crop_tif")
    if verbose:
        cmd.append("--verbose")
    else:
        cmd.append("--quiet")
    if force:
        cmd.append("--force")

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
