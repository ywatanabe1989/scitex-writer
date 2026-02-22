#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/migration/__init__.py

"""Migration tools for importing/exporting scitex-writer projects.

Usage::

    import scitex_writer as sw

    # Import from Overleaf
    result = sw.migration.from_overleaf("project.zip", output_dir="./my-paper")
    result = sw.migration.from_overleaf("project.zip", dry_run=True)

    # Export to Overleaf
    result = sw.migration.to_overleaf("./my-paper", output_path="paper.zip")
"""

from ._overleaf_export import to_overleaf
from ._overleaf_import import from_overleaf

__all__ = ["from_overleaf", "to_overleaf"]

# EOF
