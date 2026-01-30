#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_compile/_validator.py

"""
Pre-compile validation for writer projects.

Validates project structure before attempting compilation.
"""

from __future__ import annotations

from logging import getLogger
from pathlib import Path

from .._utils._verify_tree_structure import verify_tree_structure

logger = getLogger(__name__)


def validate_before_compile(project_dir: Path) -> None:
    """
    Validate project structure before compilation.

    Parameters
    ----------
    project_dir : Path
        Path to project directory

    Raises
    ------
    RuntimeError
        If validation fails
    """
    verify_tree_structure(project_dir)


__all__ = ["validate_before_compile"]

# EOF
