#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/results/_DiffResult.py

"""DiffResult - outcome of one run of the version-diff (latexdiff) pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class DiffResult:
    """Result of building the version-diff PDF for one document type.

    ``from_hash`` / ``to_hash`` are the two versions actually compared -- never a
    placeholder. The shell fell back to "current vs current" when it found no
    previous version and still called the empty output a diff; this pipeline fails
    instead, so a successful DiffResult always names two real versions.
    """

    success: bool
    """Whether the diff document was built AND compiled."""

    from_hash: Optional[str] = None
    """Short hash of the OLD version fed to latexdiff."""

    to_hash: Optional[str] = None
    """Short hash of the NEW version ('+' suffix means uncommitted changes)."""

    diff_tex: Optional[str] = None
    """Absolute path of the generated diff LaTeX source."""

    diff_pdf: Optional[str] = None
    """Absolute path of the compiled diff PDF."""

    pdf_bytes: int = 0
    """Size of the compiled diff PDF (0 when no PDF was produced)."""

    skipped: bool = False
    """True when the run was skipped outright (the shell's ``--no_diff``)."""

    error: Optional[str] = None
    """Actionable error message when ``success`` is False; else None."""

    def to_dict(self) -> dict:
        """Plain dict for JSON serialization across the CLI / MCP boundary."""
        return {
            "success": self.success,
            "from_hash": self.from_hash,
            "to_hash": self.to_hash,
            "diff_tex": self.diff_tex,
            "diff_pdf": self.diff_pdf,
            "pdf_bytes": self.pdf_bytes,
            "skipped": self.skipped,
            "error": self.error,
        }

    def validate(self) -> None:
        """Raise ValueError on an internally inconsistent result (fail-loud).

        A success carries no error; a failure must carry one. A non-skipped
        success must name BOTH compared versions and point at a non-empty PDF --
        an "empty diff" that reports success is exactly the silent degradation
        this port removed.
        """
        if self.success and self.error:
            raise ValueError("DiffResult success=True but error is set")
        if not self.success and not self.error:
            raise ValueError("DiffResult success=False but no error message")
        if not isinstance(self.pdf_bytes, int) or self.pdf_bytes < 0:
            raise ValueError(
                f"DiffResult pdf_bytes must be a non-negative int, got "
                f"{self.pdf_bytes!r}"
            )
        if self.success and not self.skipped:
            if not (self.from_hash and self.to_hash):
                raise ValueError(
                    "DiffResult success=True but from_hash/to_hash is unset "
                    "(a diff must name the two versions it compared)"
                )
            if not self.diff_pdf or not self.pdf_bytes:
                raise ValueError(
                    "DiffResult success=True but no non-empty diff_pdf was produced"
                )

    def __str__(self) -> str:
        if not self.success:
            return f"Diff FAILED: {self.error}"
        if self.skipped:
            return "Diff: skipped (--no-diff)"
        return (
            f"Diff: {self.from_hash} -> {self.to_hash} "
            f"({self.pdf_bytes} bytes) -> {self.diff_pdf}"
        )


__all__ = ["DiffResult"]

# EOF
