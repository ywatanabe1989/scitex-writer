#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Writer class for manuscript LaTeX compilation.

Provides object-oriented interface to scitex-writer functionality.
"""

from pathlib import Path
from typing import Optional
import subprocess
import os


class Writer:
    """
    LaTeX manuscript compiler.

    Example:
        >>> from scitex.writer import Writer
        >>> writer = Writer("/path/to/manuscript")
        >>> result = writer.compile()
        >>> print(f"Compiled: {result.pdf_path}")
    """

    def __init__(
        self,
        project_dir: Path,
        doc_type: str = "manuscript",
    ):
        """
        Initialize Writer.

        Args:
            project_dir: Path to the manuscript project directory
            doc_type: Type of document (manuscript, supplementary, or revision)
        """
        self.project_dir = Path(project_dir).resolve()
        self.doc_type = doc_type
        self.scripts_dir = self.project_dir / "scripts" / "shell"

        if not self.project_dir.exists():
            raise ValueError(f"Project directory does not exist: {self.project_dir}")

    def compile(
        self,
        no_figs: bool = False,
        do_p2t: bool = False,
        crop_tif: bool = False,
        verbose: bool = False,
    ) -> "CompilationResult":
        """
        Compile the manuscript.

        Args:
            no_figs: Skip figure processing
            do_p2t: Convert PPTX to TIF
            crop_tif: Crop TIF files
            verbose: Show verbose output

        Returns:
            CompilationResult with compilation status and paths
        """
        from .compile import compile_manuscript, compile_supplementary, compile_revision

        compile_funcs = {
            "manuscript": compile_manuscript,
            "supplementary": compile_supplementary,
            "revision": compile_revision,
        }

        compile_func = compile_funcs.get(self.doc_type)
        if not compile_func:
            raise ValueError(f"Unknown doc_type: {self.doc_type}")

        return compile_func(
            project_dir=self.project_dir,
            no_figs=no_figs,
            do_p2t=do_p2t,
            crop_tif=crop_tif,
            verbose=verbose,
        )

    def watch(self, callback: Optional[callable] = None):
        """
        Watch for changes and auto-compile.

        Args:
            callback: Optional callback function called after each compilation
        """
        from .watch import watch_manuscript

        return watch_manuscript(
            project_dir=self.project_dir,
            doc_type=self.doc_type,
            callback=callback,
        )


class CompilationResult:
    """Result of compilation operation."""

    def __init__(
        self,
        success: bool,
        pdf_path: Optional[Path] = None,
        tex_path: Optional[Path] = None,
        error: Optional[str] = None,
    ):
        self.success = success
        self.pdf_path = pdf_path
        self.tex_path = tex_path
        self.error = error

    def __repr__(self):
        status = "SUCCESS" if self.success else "FAILED"
        return f"CompilationResult({status}, pdf={self.pdf_path})"


__all__ = ["Writer", "CompilationResult"]
