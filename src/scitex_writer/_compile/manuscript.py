#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_compile/manuscript.py

"""
Manuscript compilation function.

Provides manuscript-specific compilation with options for:
- Figure exclusion for quick compilation
- PowerPoint to TIF conversion
- TIF cropping
- Verbose/quiet modes
- Force recompilation
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable, Optional

from .._dataclasses import CompilationResult
from ._runner import run_compile


def compile_manuscript(
    project_dir: Path,
    timeout: int = 300,
    no_figs: bool = False,
    ppt2tif: bool = False,
    crop_tif: bool = False,
    quiet: bool = False,
    verbose: bool = False,
    force: bool = False,
    log_callback: Optional[Callable[[str], None]] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
    *,
    runner_fn: Optional[Callable[..., dict]] = None,
    validator_fn: Optional[Callable[[Path], None]] = None,
    output_finder_fn: Optional[Callable[[Path, str], tuple]] = None,
    script_resolver_fn: Optional[Callable[[Path, str], Path]] = None,
) -> CompilationResult:
    """
    Compile manuscript document with optional callbacks.

    Parameters
    ----------
    project_dir : Path
        Path to writer project directory
    timeout : int
        Timeout in seconds
    no_figs : bool
        Exclude figures for quick compilation
    ppt2tif : bool
        Convert PowerPoint to TIF on WSL
    crop_tif : bool
        Crop TIF images to remove excess whitespace
    quiet : bool
        Suppress detailed logs for LaTeX compilation
    verbose : bool
        Show detailed logs for LaTeX compilation
    force : bool
        Force full recompilation, ignore cache
    log_callback : Optional[Callable[[str], None]]
        Called with each log line
    progress_callback : Optional[Callable[[int, str], None]]
        Called with progress updates (percent, step)

    Returns
    -------
    CompilationResult
        Compilation status and outputs

    Examples
    --------
    >>> from pathlib import Path
    >>> from scitex_writer._compile import compile_manuscript
    >>>
    >>> # Quick compilation without figures
    >>> result = compile_manuscript(
    ...     project_dir=Path("~/my-paper"),
    ...     no_figs=True,
    ...     quiet=True
    ... )
    >>>
    >>> # Full compilation with PowerPoint conversion
    >>> result = compile_manuscript(
    ...     project_dir=Path("~/my-paper"),
    ...     ppt2tif=True,
    ...     crop_tif=True,
    ...     verbose=True
    ... )
    """
    return run_compile(
        "manuscript",
        project_dir,
        timeout=timeout,
        no_figs=no_figs,
        ppt2tif=ppt2tif,
        crop_tif=crop_tif,
        quiet=quiet,
        verbose=verbose,
        force=force,
        log_callback=log_callback,
        progress_callback=progress_callback,
        runner_fn=runner_fn,
        validator_fn=validator_fn,
        output_finder_fn=output_finder_fn,
        script_resolver_fn=script_resolver_fn,
    )


__all__ = ["compile_manuscript"]

# EOF
