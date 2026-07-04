#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/results/_WordCountResult.py

"""WordCountResult - per-section word/element counts for one document type."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class WordCountResult:
    """Result of counting words + figures + tables for one document type.

    ``counts`` holds every section the manuscript's ``\\readwordcount`` reads:
    the IMRaD sections + ``abstract`` (word counts via texcount), plus
    ``figures`` and ``tables`` (element counts), plus ``imrd`` (the IMRaD sum).
    Counts are never negative and never absent for a requested key -- a missing
    or unreadable source contributes 0, so downstream ``\\num{}`` can never
    receive an empty argument (the siunitx "Invalid number" fatal).
    """

    success: bool
    """Whether the count completed."""

    doc_type: str
    """Document type: 'manuscript' | 'supplementary' | 'revision'."""

    counts: Dict[str, int] = field(default_factory=dict)
    """Per-key counts, e.g. {abstract, introduction, ..., figures, tables, imrd}."""

    total: int = 0
    """IMRaD word total (introduction+methods+results+discussion)."""

    output_files: List[str] = field(default_factory=list)
    """Absolute paths of the per-key count files written (one integer each)."""

    error: Optional[str] = None
    """Actionable error message when ``success`` is False; else None."""

    def to_dict(self) -> dict:
        """Plain dict for JSON serialization across the CLI / MCP boundary."""
        return {
            "success": self.success,
            "doc_type": self.doc_type,
            "counts": self.counts,
            "total": self.total,
            "output_files": self.output_files,
            "error": self.error,
        }

    def validate(self) -> None:
        """Raise ValueError on an internally inconsistent result (no silent bad state).

        Guards the fail-loud contract: a success must carry no error and only
        non-negative counts; a failure must carry an error message.
        """
        if self.success and self.error:
            raise ValueError("WordCountResult success=True but error is set")
        if not self.success and not self.error:
            raise ValueError("WordCountResult success=False but no error message")
        for key, value in self.counts.items():
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"WordCountResult count for '{key}' must be a non-negative "
                    f"int, got {value!r}"
                )

    def __str__(self) -> str:
        if not self.success:
            return f"WordCount({self.doc_type}) FAILED: {self.error}"
        parts = ", ".join(f"{k}={v}" for k, v in self.counts.items())
        return f"WordCount({self.doc_type}) total={self.total} [{parts}]"


__all__ = ["WordCountResult"]

# EOF
