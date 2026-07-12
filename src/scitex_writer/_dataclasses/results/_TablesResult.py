#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/results/_TablesResult.py

"""TablesResult - outcome of one run of the CSV -> LaTeX table pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TablesResult:
    """Result of processing every CSV table of one document type.

    Counts are what ACTUALLY happened during this run, never a request total, and
    are never negative. ``tables`` carries one entry per compiled table
    (``{name, csv, tex, rows, columns, truncated, caption_generated}``).
    ``fallback_header`` is True when NO real table existed and the comment-only
    ``00_Tables_Header.tex`` was emitted instead (it renders no table float).
    """

    success: bool
    """Whether the pipeline completed."""

    tables_compiled: int = 0
    """Number of CSV tables rendered into the compiled directory."""

    captions_created: int = 0
    """Number of default caption files written for tables lacking one."""

    xlsx_converted: int = 0
    """Number of Excel files converted to CSV before rendering."""

    tables: List[dict] = field(default_factory=list)
    """Per-table outcomes, ordered by table number."""

    compiled_file: Optional[str] = None
    """Absolute path of the gathered FINAL.tex (the file the manuscript inputs)."""

    fallback_header: bool = False
    """True when no real table existed: a comment-only header was emitted."""

    skipped: bool = False
    """True when the run was skipped outright (the shell's ``--no_tables``)."""

    error: Optional[str] = None
    """Actionable error message when ``success`` is False; else None."""

    def to_dict(self) -> dict:
        """Plain dict for JSON serialization across the CLI / MCP boundary."""
        return {
            "success": self.success,
            "tables_compiled": self.tables_compiled,
            "captions_created": self.captions_created,
            "xlsx_converted": self.xlsx_converted,
            "tables": self.tables,
            "compiled_file": self.compiled_file,
            "fallback_header": self.fallback_header,
            "skipped": self.skipped,
            "error": self.error,
        }

    def validate(self) -> None:
        """Raise ValueError on an internally inconsistent result (fail-loud).

        A success carries no error and only non-negative counts; a failure must
        carry an error message; and a fallback header is only legitimate when no
        table was compiled (the two are mutually exclusive by construction).
        """
        if self.success and self.error:
            raise ValueError("TablesResult success=True but error is set")
        if not self.success and not self.error:
            raise ValueError("TablesResult success=False but no error message")
        for name in ("tables_compiled", "captions_created", "xlsx_converted"):
            value = getattr(self, name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"TablesResult {name} must be a non-negative int, got {value!r}"
                )
        if self.fallback_header and self.tables_compiled:
            raise ValueError(
                "TablesResult fallback_header=True but tables_compiled="
                f"{self.tables_compiled} (the fallback is the NO-tables branch)"
            )

    def __str__(self) -> str:
        if not self.success:
            return f"Tables FAILED: {self.error}"
        if self.skipped:
            return "Tables: skipped (--no-tables)"
        if self.fallback_header:
            return "Tables: none found -- comment-only fallback header emitted"
        return (
            f"Tables: compiled={self.tables_compiled}, "
            f"captions_created={self.captions_created}, "
            f"xlsx_converted={self.xlsx_converted}"
        )


__all__ = ["TablesResult"]

# EOF
