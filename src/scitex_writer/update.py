#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/update.py

"""Public API for updating a scitex-writer project's engine files."""

from __future__ import annotations

from typing import Optional

from ._mcp.handlers._update import update_project as _update_project


def project(
    project_dir: str = ".",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    """Update engine files in an existing scitex-writer project.

    Replaces build scripts, LaTeX styles, and base templates with the latest
    version from the installed scitex-writer package (or GitHub if branch/tag
    is specified).  User content is never modified.

    Engine files updated:
        - scripts/                    (all shell scripts)
        - 00_shared/latex_styles/     (LaTeX style files)
        - 01_manuscript/base.tex
        - 02_supplementary/base.tex
        - 03_revision/base.tex
        - compile.sh
        - Makefile

    User content preserved (never touched):
        - 00_shared/authors.tex, title.tex, keywords.tex, journal_name.tex
        - 00_shared/bib_files/bibliography.bib
        - 00_shared/claims.json
        - 01_manuscript/contents/
        - 02_supplementary/contents/
        - 03_revision/contents/

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project to update (default: current directory).
    branch : str, optional
        Pull from a specific template branch. Triggers GitHub clone.
    tag : str, optional
        Pull from a specific template tag/version. Triggers GitHub clone.
    dry_run : bool
        If True, report what would change without modifying any files.

    Returns
    -------
    dict
        - success (bool)
        - updated_paths (list[str])
        - skipped_paths (list[str])
        - preserved_paths (list[str])
        - dry_run (bool)
        - message (str)
        - error (str, only on failure)

    Examples
    --------
    >>> import scitex_writer as sw
    >>> sw.update.project("~/proj/my-paper", dry_run=True)
    >>> sw.update.project("~/proj/my-paper")
    >>> sw.update.project("~/proj/my-paper", tag="v2.7.1")
    """
    return _update_project(
        project_dir, branch=branch, tag=tag, dry_run=dry_run, force=force
    )


__all__ = ["project"]

# EOF
