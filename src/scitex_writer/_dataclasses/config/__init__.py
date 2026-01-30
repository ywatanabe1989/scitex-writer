#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_dataclasses/config/__init__.py

from ._CONSTANTS import DOC_TYPE_DIRS, DOC_TYPE_FLAGS, DOC_TYPE_PDFS
from ._WriterConfig import WriterConfig

__all__ = [
    "WriterConfig",
    "DOC_TYPE_DIRS",
    "DOC_TYPE_FLAGS",
    "DOC_TYPE_PDFS",
]

# EOF
