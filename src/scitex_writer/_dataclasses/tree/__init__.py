#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/tree/__init__.py

"""
Tree dataclasses for Writer module (internal use).

Provides dataclasses for directory tree structures at the project level.
Not intended for public API - access trees through Writer class.
"""

# Import for internal use only
from ._ConfigTree import ConfigTree
from ._ManuscriptTree import ManuscriptTree
from ._RevisionTree import RevisionTree
from ._ScriptsTree import ScriptsTree
from ._SharedTree import SharedTree
from ._SupplementaryTree import SupplementaryTree

__all__ = [
    "ConfigTree",
    "SharedTree",
    "ScriptsTree",
    "ManuscriptTree",
    "SupplementaryTree",
    "RevisionTree",
]

# EOF
