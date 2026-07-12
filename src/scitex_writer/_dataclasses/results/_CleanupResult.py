#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/results/_CleanupResult.py

"""CleanupResult - per-category counts for one cleanup sweep."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CleanupResult:
    """Result of sweeping build artefacts for one document type.

    Each count is what ACTUALLY happened during this sweep (files that raced
    away mid-sweep are simply not counted), never a request total. Counts are
    never negative. ``log_dir`` is the absolute directory aux files were moved
    into (created if missing, like the shell's ``mkdir -p``).
    """

    success: bool
    """Whether the sweep completed."""

    bak_removed: int = 0
    """Number of ``*bak*`` files removed recursively."""

    emacs_removed: int = 0
    """Number of Emacs temp files (``#*#``) removed recursively."""

    aux_moved: int = 0
    """Number of top-level aux/log files moved into ``log_dir``."""

    progress_removed: int = 0
    """Number of ``progress.log`` files removed recursively."""

    versioned_removed: int = 0
    """Number of versioned ``*_v*.pdf`` / ``*_v*.tex`` files removed."""

    log_dir: Optional[str] = None
    """Absolute path of the log directory aux files were moved into."""

    dry_run: bool = False
    """True if this was a preview: counts are what WOULD happen; nothing mutated."""

    error: Optional[str] = None
    """Actionable error message when ``success`` is False; else None."""

    def to_dict(self) -> dict:
        """Plain dict for JSON serialization across the CLI / MCP boundary."""
        return {
            "success": self.success,
            "bak_removed": self.bak_removed,
            "emacs_removed": self.emacs_removed,
            "aux_moved": self.aux_moved,
            "progress_removed": self.progress_removed,
            "versioned_removed": self.versioned_removed,
            "log_dir": self.log_dir,
            "dry_run": self.dry_run,
            "error": self.error,
        }

    def validate(self) -> None:
        """Raise ValueError on an internally inconsistent result (fail-loud).

        A success must carry no error and only non-negative counts; a failure
        must carry an error message.
        """
        if self.success and self.error:
            raise ValueError("CleanupResult success=True but error is set")
        if not self.success and not self.error:
            raise ValueError("CleanupResult success=False but no error message")
        for name in (
            "bak_removed",
            "emacs_removed",
            "aux_moved",
            "progress_removed",
            "versioned_removed",
        ):
            value = getattr(self, name)
            if not isinstance(value, int) or value < 0:
                raise ValueError(
                    f"CleanupResult {name} must be a non-negative int, got {value!r}"
                )

    def __str__(self) -> str:
        if not self.success:
            return f"Cleanup FAILED: {self.error}"
        head = "Cleanup[dry-run]: " if self.dry_run else "Cleanup: "
        return (
            f"{head}"
            f"bak={self.bak_removed}, emacs={self.emacs_removed}, "
            f"aux_moved={self.aux_moved}, progress={self.progress_removed}, "
            f"versioned={self.versioned_removed}"
        )


__all__ = ["CleanupResult"]

# EOF
