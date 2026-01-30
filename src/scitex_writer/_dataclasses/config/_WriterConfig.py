#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/config/_WriterConfig.py

"""
WriterConfig - dataclass for writer configuration.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class WriterConfig:
    """Configuration for scitex_writer."""

    project_dir: Path
    """Root directory of writer project"""

    manuscript_dir: Path
    """Directory for manuscript (01_manuscript/)"""

    supplementary_dir: Path
    """Directory for supplementary (02_supplementary/)"""

    revision_dir: Path
    """Directory for revision (03_revision/)"""

    shared_dir: Path
    """Directory for shared resources (00_shared/)"""

    compile_script: Optional[Path] = None
    """Path to compile script (auto-detected if None)"""

    @classmethod
    def from_directory(cls, project_dir: Path) -> WriterConfig:
        """
        Create config from project directory.

        Args:
            project_dir: Path to writer project root

        Returns:
            WriterConfig instance

        Examples:
            >>> config = WriterConfig.from_directory(Path("/path/to/project"))
            >>> print(config.manuscript_dir)
        """
        project_dir = Path(project_dir)

        return cls(
            project_dir=project_dir,
            manuscript_dir=project_dir / "01_manuscript",
            supplementary_dir=project_dir / "02_supplementary",
            revision_dir=project_dir / "03_revision",
            shared_dir=project_dir / "00_shared",
        )

    def validate(self) -> bool:
        """
        Validate that required directories exist.

        Returns:
            True if valid writer project structure

        Raises:
            ValueError: If invalid structure
        """
        if not self.project_dir.exists():
            raise ValueError(f"Project directory not found: {self.project_dir}")

        # Check for at least one document directory
        doc_dirs = [
            self.manuscript_dir,
            self.supplementary_dir,
            self.revision_dir,
        ]

        if not any(d.exists() for d in doc_dirs):
            raise ValueError(
                f"No document directories found in {self.project_dir}. "
                "Expected: 01_manuscript/, 02_supplementary/, or 03_revision/"
            )

        return True


__all__ = ["WriterConfig"]

# EOF
