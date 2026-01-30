#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/config/_CONSTANTS.py

"""
Constants for writer module.

Centralized definitions for document dataclasses and directory mappings.
"""

from __future__ import annotations

# Document type to directory mapping
DOC_TYPE_DIRS = {
    "manuscript": "01_manuscript",
    "supplementary": "02_supplementary",
    "revision": "03_revision",
}

# Document type to command-line flag mapping
DOC_TYPE_FLAGS = {
    "manuscript": "-m",
    "supplementary": "-s",
    "revision": "-r",
}

# Document type to PDF filename mapping
DOC_TYPE_PDFS = {
    "manuscript": "manuscript.pdf",
    "supplementary": "supplementary.pdf",
    "revision": "revision.pdf",
}

__all__ = [
    "DOC_TYPE_DIRS",
    "DOC_TYPE_FLAGS",
    "DOC_TYPE_PDFS",
]

# EOF
