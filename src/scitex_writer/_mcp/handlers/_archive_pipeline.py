#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_archive_pipeline.py

r"""The archive pipeline: a pure-Python port of ``process_archive.sh``.

Ports the shell module stage for stage, reading the SAME config keys the shell
read via ``yq`` out of ``config/config_<doc_type>.yaml``: ``paths.compiled_pdf``,
``paths.compiled_tex``, ``paths.diff_pdf``, ``paths.diff_tex`` and
``paths.archive_dir``.

Stages (``process`` runs them in order):

1. ``clean-tree gate`` -- archive ONLY when the working tree is clean; a snapshot
                          stamped with a commit hash whose content it does not
                          actually hold would be a lie. A dirty tree is a
                          ``skipped=True`` success carrying ``skip_reason``.
2. ``archive_id``      -- ``YYYYmmdd-HHMMSS_<short7>``.
3. ``store_file`` x4   -- copy each compiled output to
                          ``<archive_dir>/<stem>_<archive_id>.<ext>`` plus an
                          un-stamped ``<stem>.<ext>`` "current" copy. A
                          ``*_diff`` stem keeps its suffix LAST:
                          ``manuscript_diff`` -> ``manuscript_<id>_diff``.

One shell branch this port refuses as DEAD, not ported: ``get_git_identifier``
substituted ``nogit`` / ``nocommit`` for the hash when the directory was not a
repo or carried no commit -- but its only caller ran AFTER ``is_git_clean``, which
returns false in exactly those two cases. Those identifiers could never be
produced. This port requires a repo with commits (the gate already did) and
therefore always stamps a REAL hash.

Robust by construction: pathlib only (never shells out to cp/mkdir); every write
target is resolved and asserted to live INSIDE the project root; fail-loud on a
missing project dir / config.
"""

from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..._dataclasses import ArchiveResult
from ..._utils import _git
from ..utils import resolve_project_path
from ._engine_paths import DOC_DIRS, load_doc_config, resolve_paths

_CFG_KEYS = {
    "compiled_pdf": ("paths", "compiled_pdf"),
    "compiled_tex": ("paths", "compiled_tex"),
    "diff_pdf": ("paths", "diff_pdf"),
    "diff_tex": ("paths", "diff_tex"),
    "versions_dir": ("paths", "archive_dir"),
}

# The order the shell stored them in; also the order they appear in the result.
_STORE_ORDER = ("compiled_pdf", "compiled_tex", "diff_pdf", "diff_tex")

DIFF_SUFFIX = "_diff"


def archive_id(project_path: Path, now: Optional[datetime] = None) -> str:
    """The snapshot identifier: ``YYYYmmdd-HHMMSS_<short7>`` of HEAD.

    Raises ValueError when HEAD does not resolve -- the caller must have passed
    the clean-tree gate, which already guarantees it does, so this is a contract
    check rather than a fallback.
    """
    stamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    short = _git.short_hash(project_path, "HEAD")
    if short is None:
        raise ValueError(
            f"Cannot stamp an archive: HEAD does not resolve in {project_path}."
        )
    return f"{stamp}_{short}"


def archived_name(stem: str, snapshot_id: str) -> str:
    """The archived stem for ``stem`` in snapshot ``snapshot_id``.

    ``manuscript`` -> ``manuscript_<id>``; ``manuscript_diff`` ->
    ``manuscript_<id>_diff`` (the ``_diff`` marker stays LAST so the archive sorts
    by document, not by kind -- the shell's rule).
    """
    if stem.endswith(DIFF_SUFFIX):
        return f"{stem[: -len(DIFF_SUFFIX)]}_{snapshot_id}{DIFF_SUFFIX}"
    return f"{stem}_{snapshot_id}"


def store_file(source: Path, versions_dir: Path, snapshot_id: str) -> Optional[dict]:
    """Copy ``source`` into ``versions_dir`` twice: stamped, and as "current".

    Returns ``{source, archived, current}``, or None when ``source`` does not
    exist (a project with no diff PDF is normal -- the shell logged and moved on).
    """
    if not source.is_file():
        return None
    versions_dir.mkdir(parents=True, exist_ok=True)
    suffix = source.suffix
    stamped = versions_dir / f"{archived_name(source.stem, snapshot_id)}{suffix}"
    current = versions_dir / f"{source.stem}{suffix}"
    shutil.copyfile(source, stamped)
    shutil.copyfile(source, current)
    return {
        "source": str(source),
        "archived": str(stamped),
        "current": str(current),
    }


def process(
    project_dir: str,
    doc_type: str = "manuscript",
    no_archive: bool = False,
    now: Optional[datetime] = None,
) -> dict:
    """Snapshot the compiled outputs of ``doc_type`` into the versions directory.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project directory (must be a git repository).
    doc_type : str
        One of 'manuscript' (default), 'supplementary', 'revision'.
    no_archive : bool
        Skip the whole pipeline.
    now : datetime, optional
        Timestamp for the archive id. Injected by the tests; defaults to now.

    Returns
    -------
    dict
        The serialized :class:`ArchiveResult`. A DIRTY working tree is a
        ``skipped`` success (an archive must match a real commit); a missing
        project / config is a hard error with an actionable hint.
    """
    try:
        if no_archive:
            return ArchiveResult(
                success=True, skipped=True, skip_reason="no_archive requested"
            ).to_dict()

        if doc_type not in DOC_DIRS:
            return {
                "success": False,
                "error": (
                    f"Invalid doc_type '{doc_type}'. Must be one of: {tuple(DOC_DIRS)}"
                ),
            }

        project_path = resolve_project_path(project_dir)
        if not project_path.is_dir():
            return {
                "success": False,
                "error": (
                    f"Project directory not found: {project_path}. "
                    f"Check the path passed as project_dir."
                ),
            }

        cfg, error = load_doc_config(project_path, doc_type)
        if error:
            return {"success": False, "error": error}
        paths, error = resolve_paths(project_path, cfg, _CFG_KEYS, "paths")
        if error:
            return {"success": False, "error": error}

        versions_dir = paths["versions_dir"]
        versions_dir.mkdir(parents=True, exist_ok=True)

        if not _git.is_clean(project_path):
            reason = (
                "uncommitted changes in the working tree -- an archive is stamped "
                "with a commit hash, so it may only snapshot a clean tree. "
                "Fix: commit your changes, then archive."
            )
            result = ArchiveResult(
                success=True,
                skipped=True,
                skip_reason=reason,
                versions_dir=str(versions_dir),
            )
            result.validate()
            return result.to_dict()

        snapshot_id = archive_id(project_path, now=now)

        archived, missing = [], []
        for name in _STORE_ORDER:
            stored = store_file(paths[name], versions_dir, snapshot_id)
            if stored is None:
                missing.append(str(paths[name]))
            else:
                archived.append(stored)

        result = ArchiveResult(
            success=True,
            archive_id=snapshot_id,
            archived=archived,
            versions_dir=str(versions_dir),
            missing=missing,
        )
        result.validate()
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": f"{type(e).__name__}: {e}"}


__all__ = ["archive_id", "archived_name", "process", "store_file"]

# EOF
