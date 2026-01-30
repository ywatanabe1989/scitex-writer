#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/core/_Document.py

"""
Base Document class for document type accessors.

Provides dynamic file access via attribute lookups.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ._DocumentSection import DocumentSection


class Document:
    """
    Base document accessor.

    Provides dynamic file access by mapping attribute names to .tex files:
    - document.introduction -> introduction.tex
    - document.methods -> methods.tex
    - Custom: document.custom_section -> custom_section.tex
    """

    def __init__(self, root: Path, git_root: Optional[Path] = None):
        """
        Initialize document accessor.

        Args:
            root: Path to document directory (contains 'contents/' subdirectory)
            git_root: Path to git repository root (optional, for efficiency)
        """
        self.root = root
        self.git_root = git_root

    @property
    def name(self) -> str:
        """Return the document directory name."""
        return self.root.name

    def __getattr__(self, name: str) -> DocumentSection:
        """
        Get file path by name (e.g., introduction -> introduction.tex).

        Args:
            name: Section name without .tex extension

        Returns:
            DocumentSection for the requested file

        Example:
            >>> manuscript = ManuscriptDocument(Path("01_manuscript"))
            >>> manuscript.introduction.read()  # Reads contents/introduction.tex
        """
        if name.startswith("_"):
            # Avoid infinite recursion for private attributes
            raise AttributeError(
                f"'{self.__class__.__name__}' has no attribute '{name}'"
            )

        file_path = self.root / "contents" / f"{name}.tex"
        return DocumentSection(file_path, git_root=self.git_root)

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}({self.root.name})"


__all__ = ["Document"]

# EOF
