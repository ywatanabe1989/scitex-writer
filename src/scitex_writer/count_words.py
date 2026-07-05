#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/count_words.py

"""Word-count functions.

Usage::

    import scitex_writer as sw
    result = sw.count_words.run("./my-paper", doc_type="manuscript")

Counts words per abstract/IMRaD section (via ``texcount``) plus figure/table
elements, and writes one integer per key into the project's ``wordcount_dir`` --
the files the manuscript's ``\\readwordcount`` reads. Pure-Python port of
``scripts/shell/modules/count_words.sh``.
"""

from typing import Literal as _Literal

from ._mcp.handlers._wordcount import count_words as _count_words

try:
    from scitex_dev.decorators import supports_return_as as _supports_return_as
except ImportError:  # scitex_dev optional -- degrade to a no-op decorator

    def _supports_return_as(fn):
        return fn


@_supports_return_as
def run(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision"] = "manuscript",
) -> dict:
    """Count words + figures + tables for ``doc_type`` and write the count files.

    Returns ``{success, doc_type, counts, total, output_files, error}``.
    """
    return _count_words(project_dir, doc_type)


__all__ = ["run"]

# EOF
