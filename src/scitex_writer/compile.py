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


__all__ = ["manuscript", "supplementary", "revision"]

# EOF
