#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/export.py

"""Export functions for manuscript packaging.

Usage::

    import scitex_writer as sw

    # Export manuscript as arXiv-ready tarball
    result = sw.export.manuscript("./my-paper")

    # With custom output directory
    result = sw.export.manuscript("./my-paper", output_dir="/tmp/arxiv-export")
"""

from ._mcp.handlers import export_manuscript as _export_manuscript


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


__all__ = ["manuscript"]

# EOF
