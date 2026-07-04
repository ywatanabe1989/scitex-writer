#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/results/_CitationStyleResult.py

"""CitationStyleResult - result of applying a bibliography citation style."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class CitationStyleResult:
    """Result of setting the active ``\\bibliographystyle`` in bibliography.tex."""

    success: bool
    """Whether the operation completed."""

    changed: bool = False
    """True if the active style was actually changed (False = already set / no-op)."""

    current_style: Optional[str] = None
    """The active style BEFORE the operation (None if none was set)."""

    new_style: Optional[str] = None
    """The requested/target style (None when no style was configured)."""

    backup_path: Optional[str] = None
    """Absolute path of the .bak written before editing (None when no edit)."""

    message: str = ""
    """Human-readable status."""

    error: Optional[str] = None
    """Actionable error message when ``success`` is False; else None."""

    def to_dict(self) -> dict:
        """Plain dict for JSON serialization across the CLI / MCP boundary."""
        return {
            "success": self.success,
            "changed": self.changed,
            "current_style": self.current_style,
            "new_style": self.new_style,
            "backup_path": self.backup_path,
            "message": self.message,
            "error": self.error,
        }

    def validate(self) -> None:
        """Raise ValueError on an internally inconsistent result (fail-loud)."""
        if self.success and self.error:
            raise ValueError("CitationStyleResult success=True but error is set")
        if not self.success and not self.error:
            raise ValueError("CitationStyleResult success=False but no error message")
        if self.changed and not self.new_style:
            raise ValueError("CitationStyleResult changed=True but new_style is None")

    def __str__(self) -> str:
        if not self.success:
            return f"CitationStyle FAILED: {self.error}"
        if self.changed:
            return f"CitationStyle: {self.current_style} -> {self.new_style}"
        return f"CitationStyle: already '{self.new_style or self.current_style}'"


__all__ = ["CitationStyleResult"]

# EOF
