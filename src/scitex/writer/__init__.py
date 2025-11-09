#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SciTeX Writer - Scientific Manuscript Writing System.

A comprehensive LaTeX-based manuscript writing system with Python interface,
automated compilation, version control, and manuscript management.

Example:
    >>> from scitex.writer import Writer
    >>> writer = Writer("/path/to/manuscript")
    >>> writer.compile()
"""

from pathlib import Path

# Read version from VERSION file at repository root
__version_file__ = Path(__file__).parent.parent.parent.parent / "VERSION"
try:
    __version__ = __version_file__.read_text().strip()
except FileNotFoundError:
    __version__ = "unknown"

# Import main interfaces
from .writer import Writer
from .template import clone_writer_project
from .compile import (
    compile_manuscript,
    compile_supplementary,
    compile_revision,
)

__all__ = [
    "__version__",
    "Writer",
    "clone_writer_project",
    "compile_manuscript",
    "compile_supplementary",
    "compile_revision",
]

# Show version on import for logging purposes
import logging

logger = logging.getLogger(__name__)
logger.debug(f"SciTeX Writer v{__version__} loaded")
