#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_compile/__init__.py

"""
LaTeX compilation module for writer.

Provides organized compilation functionality:
- manuscript: Manuscript compilation with figure/conversion options
- supplementary: Supplementary materials compilation
- revision: Revision response compilation with change tracking
- _runner: Script execution engine
- _parser: Output parsing utilities
- _validator: Pre-compile validation
"""

from __future__ import annotations

from .._dataclasses import CompilationResult
from ._compile_unified import compile
from ._runner import run_compile
from .manuscript import compile_manuscript
from .revision import compile_revision
from .supplementary import compile_supplementary

__all__ = [
    "compile",
    "run_compile",
    "compile_manuscript",
    "compile_supplementary",
    "compile_revision",
    "CompilationResult",
]

# EOF
