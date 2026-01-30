#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/results/_LaTeXIssue.py

"""
LaTeXIssue - dataclass for LaTeX compilation issues.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LaTeXIssue:
    """Single LaTeX error or warning."""

    type: str  # 'error' or 'warning'
    message: str

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.type.upper()}: {self.message}"


__all__ = ["LaTeXIssue"]

# EOF
