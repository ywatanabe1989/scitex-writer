#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/cleanup.py

"""Cleanup functions.

Usage::

    import scitex_writer as sw
    result = sw.cleanup.run("./my-paper", doc_type="manuscript")

Sweeps LaTeX build artefacts for a document type: removes ``*bak*`` and Emacs
temp (``#*#``) files recursively, moves top-level aux/log files into the
project's ``doc_log_dir``, removes ``progress.log`` files, and removes versioned
``*_v*.pdf`` / ``*_v*.tex`` files -- never touching anything outside the project
root. Pure-Python port of ``scripts/shell/modules/cleanup.sh``.
"""

from typing import Literal as _Literal

from ._mcp.handlers._cleanup import clean as _clean

try:
    from scitex_dev.decorators import supports_return_as as _supports_return_as
except ImportError:  # scitex_dev optional -- degrade to a no-op decorator

    def _supports_return_as(fn):
        return fn


@_supports_return_as
def run(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision"] = "manuscript",
    dry_run: bool = False,
) -> dict:
    """Sweep LaTeX build artefacts for ``doc_type`` and return per-category counts.

    When ``dry_run`` is True nothing is removed/moved -- the counts report what
    WOULD happen. Returns ``{success, bak_removed, emacs_removed, aux_moved,
    progress_removed, versioned_removed, log_dir, dry_run, error}``.
    """
    return _clean(project_dir, doc_type, dry_run)


__all__ = ["run"]

# EOF
