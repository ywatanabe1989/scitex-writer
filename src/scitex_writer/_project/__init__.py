#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_project/__init__.py

"""
Project initialization helpers for writer module.

Handles project creation, attachment, and validation.
"""

from __future__ import annotations

from ._create import ensure_project_exists
from ._trees import create_document_trees
from ._validate import validate_structure

__all__ = [
    "ensure_project_exists",
    "validate_structure",
    "create_document_trees",
]

# EOF
