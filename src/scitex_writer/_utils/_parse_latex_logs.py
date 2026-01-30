#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_utils/_parse_latex_logs.py

"""
LaTeX error and warning parsing from compilation output.

Simple parsing of LaTeX errors and warnings from stdout/stderr.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from .._dataclasses import LaTeXIssue


def parse_compilation_output(
    output: str, log_file: Path = None
) -> Tuple[List[LaTeXIssue], List[LaTeXIssue]]:
    """
    Parse errors and warnings from compilation output.

    Args:
        output: Compilation output (stdout + stderr)
        log_file: Optional path to .log file (unused, for compatibility)

    Returns:
        Tuple of (error_issues, warning_issues)
    """
    errors = []
    warnings = []

    for line in output.split("\n"):
        # LaTeX error pattern: "! Error message"
        if line.startswith("!"):
            error_text = line[1:].strip()
            if error_text:
                errors.append(LaTeXIssue(type="error", message=error_text))

        # LaTeX warning pattern
        elif "warning" in line.lower():
            warnings.append(LaTeXIssue(type="warning", message=line.strip()))

    return errors, warnings


__all__ = [
    "parse_compilation_output",
]

# EOF
