#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/__init__.py

"""
Type definitions for Writer module.

Provides dataclasses for document structures with clear separation of concerns.
Each document type includes:
- Typed access to sections and files
- Nested Contents dataclass for content/ subdirectory
- verify_structure() method for validation
"""

from .config import WriterConfig
from .contents import ManuscriptContents, RevisionContents, SupplementaryContents
from .core import Document, DocumentSection
from .results import CompilationResult, LaTeXIssue

# Tree structures (internal use)
from .tree import (
    ConfigTree,
    ManuscriptTree,
    RevisionTree,
    ScriptsTree,
    SharedTree,
    SupplementaryTree,
)

__all__ = [
    # Core document dataclasses
    "DocumentSection",
    "Document",
    # Document contents
    "ManuscriptContents",
    "SupplementaryContents",
    "RevisionContents",
    # Configuration and results
    "CompilationResult",
    "WriterConfig",
    "LaTeXIssue",
    # Tree structures
    "ConfigTree",
    "SharedTree",
    "ScriptsTree",
    "ManuscriptTree",
    "SupplementaryTree",
    "RevisionTree",
]

# EOF
