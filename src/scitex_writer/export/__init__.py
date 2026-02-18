#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/export/__init__.py

"""Export functions for manuscript packaging and arXiv compliance.

Usage::

    import scitex_writer as sw

    # Export manuscript as arXiv-ready tarball
    result = sw.export.manuscript("./my-paper")

    # Clean LaTeX for arXiv compliance
    cleaned = sw.export.clean_latex(raw_latex)

    # Check compliance
    result = sw.export.check_compliance(title, abstract, latex_content)

    # Validate file types in a directory
    valid, invalid = sw.export.validate_file_types(Path("./my-paper"))

    # Suggest arXiv categories from text
    suggestions = sw.export.suggest_categories("deep learning neural network")
"""

from .._mcp.handlers import export_manuscript as _export_manuscript
from ._arxiv_categories import suggest_categories
from ._arxiv_cleaner import ArxivLatexCleaner as _ArxivLatexCleaner


def manuscript(
    project_dir: str,
    output_dir: str | None = None,
    format: str = "arxiv",
) -> dict:
    """Export manuscript as arXiv-ready tarball.

    Args:
        project_dir: Path to scitex-writer project directory.
        output_dir: Output directory (default: 01_manuscript/export/).
        format: Export format (currently only 'arxiv').

    Returns:
        dict with keys: success, tarball_path, message/error.
    """
    return _export_manuscript(project_dir, output_dir, format)


def clean_latex(latex_content: str) -> str:
    """Clean LaTeX content for arXiv compliance.

    Args:
        latex_content: Raw LaTeX content string.

    Returns:
        Cleaned LaTeX content string.
    """
    cleaner = _ArxivLatexCleaner()
    return cleaner.clean_latex_for_arxiv(latex_content)


__all__ = [
    "manuscript",
    "clean_latex",
    "suggest_categories",
]

# EOF
