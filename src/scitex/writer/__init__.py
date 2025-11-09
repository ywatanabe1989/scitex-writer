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

# Read version from pyproject.toml (single source of truth)
try:
    # Try using importlib.metadata first (works for installed packages)
    from importlib.metadata import version
    __version__ = version("scitex-writer")
except Exception:
    # Fallback: read directly from pyproject.toml
    try:
        import tomllib  # Python 3.11+
    except ImportError:
        try:
            import tomli as tomllib  # Fallback for older Python
        except ImportError:
            # Last resort: manual parsing
            pyproject_file = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
            try:
                content = pyproject_file.read_text()
                for line in content.split('\n'):
                    if line.strip().startswith('version ='):
                        __version__ = line.split('=')[1].strip().strip('"').strip("'")
                        break
                else:
                    __version__ = "unknown"
            except FileNotFoundError:
                __version__ = "unknown"
    else:
        # Use tomllib to parse properly
        pyproject_file = Path(__file__).parent.parent.parent.parent / "pyproject.toml"
        try:
            with open(pyproject_file, 'rb') as f:
                data = tomllib.load(f)
                __version__ = data.get('project', {}).get('version', 'unknown')
        except FileNotFoundError:
            __version__ = "unknown"

# Import main interfaces
from .writer import Writer, CompilationResult
from .template import clone_writer_project
from .compile import (
    compile_manuscript,
    compile_supplementary,
    compile_revision,
)

__all__ = [
    "__version__",
    "Writer",
    "CompilationResult",
    "clone_writer_project",
    "compile_manuscript",
    "compile_supplementary",
    "compile_revision",
]

# Show version on import for logging purposes
import logging

logger = logging.getLogger(__name__)
logger.debug(f"SciTeX Writer v{__version__} loaded")
