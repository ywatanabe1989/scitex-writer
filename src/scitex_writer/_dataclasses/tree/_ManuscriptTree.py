#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/tree/_ManuscriptTree.py

"""
ManuscriptTree - dataclass for manuscript directory structure.

Represents the 01_manuscript/ directory with all subdirectories.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from ..contents import ManuscriptContents
from ..core import DocumentSection


@dataclass
class ManuscriptTree:
    """Manuscript directory structure (01_manuscript/)."""

    root: Path
    git_root: Optional[Path] = None

    # Contents subdirectory
    contents: ManuscriptContents = None

    # Root level files
    base: DocumentSection = None
    readme: DocumentSection = None

    # Directories
    archive: Path = None

    def __post_init__(self):
        """Initialize all instances."""
        if self.contents is None:
            self.contents = ManuscriptContents(self.root / "contents", self.git_root)
        if self.base is None:
            self.base = DocumentSection(self.root / "base.tex", self.git_root)
        if self.readme is None:
            self.readme = DocumentSection(self.root / "README.md", self.git_root)
        if self.archive is None:
            self.archive = self.root / "archive"

    def verify_structure(self) -> tuple[bool, list[str]]:
        """
        Verify manuscript structure has required components.

        Returns:
            (is_valid, list_of_missing_items_with_paths)
        """
        missing = []

        # Check contents structure
        contents_valid, contents_missing = self.contents.verify_structure()
        if not contents_valid:
            # Contents already includes full paths, just pass them through
            missing.extend(contents_missing)

        # Check root level files
        if not self.base.path.exists():
            expected_path = (
                self.base.path.relative_to(self.git_root)
                if self.git_root
                else self.base.path
            )
            missing.append(f"base.tex (expected at: {expected_path})")

        return len(missing) == 0, missing


__all__ = ["ManuscriptTree"]

# EOF
