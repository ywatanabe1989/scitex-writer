#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/compile.py

"""Compilation functions for LaTeX manuscripts.

Usage::

    import scitex_writer as sw

    # Compile manuscript
    result = sw.compile.manuscript("./my-paper")

    # With options
    result = sw.compile.manuscript("./my-paper", draft=True, no_figs=True)

    # Compile other document types
    result = sw.compile.supplementary("./my-paper")
    result = sw.compile.revision("./my-paper", track_changes=True)

    # Compile raw LaTeX content with color mode support
    result = sw.compile.content(
        latex_content,
        project_dir="./my-paper",  # Optional, for bibliography
        color_mode="dark",         # 'light', 'dark', 'sepia', 'paper'
    )
"""

from ._mcp.handlers import compile_manuscript as _compile_manuscript
from ._mcp.handlers import compile_revision as _compile_revision
from ._mcp.handlers import compile_supplementary as _compile_supplementary


def manuscript(
    project_dir: str,
    timeout: int = 300,
    no_figs: bool = False,
    no_tables: bool = False,
    no_diff: bool = False,
    draft: bool = False,
    dark_mode: bool = False,
    quiet: bool = False,
    verbose: bool = False,
) -> dict:
    """Compile manuscript to PDF.

    Args:
        project_dir: Path to scitex-writer project directory.
        timeout: Compilation timeout in seconds.
        no_figs: Skip figure processing.
        no_tables: Skip table processing.
        no_diff: Skip diff generation.
        draft: Fast single-pass compilation.
        dark_mode: Enable dark mode output.
        quiet: Suppress output.
        verbose: Verbose output.

    Returns:
        Dict with success status, pdf_path, and any errors.
    """
    return _compile_manuscript(
        project_dir,
        timeout=timeout,
        no_figs=no_figs,
        no_tables=no_tables,
        no_diff=no_diff,
        draft=draft,
        dark_mode=dark_mode,
        quiet=quiet,
        verbose=verbose,
    )


def supplementary(
    project_dir: str,
    timeout: int = 300,
    no_figs: bool = False,
    no_tables: bool = False,
    no_diff: bool = False,
    draft: bool = False,
    quiet: bool = False,
) -> dict:
    """Compile supplementary materials to PDF.

    Args:
        project_dir: Path to scitex-writer project directory.
        timeout: Compilation timeout in seconds.
        no_figs: Skip figure processing.
        no_tables: Skip table processing.
        no_diff: Skip diff generation.
        draft: Fast single-pass compilation.
        quiet: Suppress output.

    Returns:
        Dict with success status, pdf_path, and any errors.
    """
    return _compile_supplementary(
        project_dir,
        timeout=timeout,
        no_figs=no_figs,
        no_tables=no_tables,
        no_diff=no_diff,
        draft=draft,
        quiet=quiet,
    )


def revision(
    project_dir: str,
    track_changes: bool = False,
    timeout: int = 300,
    no_diff: bool = True,
    draft: bool = False,
    quiet: bool = False,
) -> dict:
    """Compile revision document to PDF.

    Args:
        project_dir: Path to scitex-writer project directory.
        track_changes: Enable change tracking.
        timeout: Compilation timeout in seconds.
        no_diff: Skip diff generation.
        draft: Fast single-pass compilation.
        quiet: Suppress output.

    Returns:
        Dict with success status, pdf_path, and any errors.
    """
    return _compile_revision(
        project_dir,
        track_changes=track_changes,
        timeout=timeout,
        no_diff=no_diff,
        draft=draft,
        quiet=quiet,
    )


def content(
    latex_content: str,
    project_dir: str | None = None,
    color_mode: str = "light",
    name: str = "content",
    timeout: int = 60,
    keep_aux: bool = False,
) -> dict:
    """Compile raw LaTeX content to PDF.

    Creates a standalone document from the provided LaTeX content and compiles
    it to PDF. Supports color modes for comfortable viewing and can link to
    project bibliography for citation rendering.

    Args:
        latex_content: Raw LaTeX content to compile. Can be:
            - A complete document (with \\documentclass)
            - Document body only (will be wrapped automatically)
        project_dir: Optional path to scitex-writer project for bibliography.
        color_mode: Color theme for output:
            - 'light': Default white background
            - 'dark': Dark gray background with light text
            - 'sepia': Warm cream background for comfortable reading
            - 'paper': Pure white, optimized for printing
        name: Name for the output (used in filename).
        timeout: Compilation timeout in seconds.
        keep_aux: Keep auxiliary files (.aux, .log, etc.) after compilation.

    Returns:
        Dict with success status, output_pdf path, log, and any errors.

    Example::

        import scitex_writer as sw

        # Compile simple content
        result = sw.compile.content(
            r"\\section{Introduction}\\nThis is my introduction.",
            color_mode="dark",
        )

        # With project bibliography
        result = sw.compile.content(
            latex_content,
            project_dir="./my-paper",
            color_mode="sepia",
        )
    """
    from ._mcp.content import compile_content as _compile_content

    return _compile_content(
        latex_content,
        project_dir=project_dir,
        color_mode=color_mode,
        section_name=name,
        timeout=timeout,
        keep_aux=keep_aux,
    )


__all__ = ["manuscript", "supplementary", "revision", "content"]

# EOF
