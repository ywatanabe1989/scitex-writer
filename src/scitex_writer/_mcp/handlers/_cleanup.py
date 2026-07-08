#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_cleanup.py

"""Cleanup handler: sweep LaTeX build artefacts for one document type.

A pure-Python port of ``scripts/shell/modules/cleanup.sh``. It resolves the
per-doc-type paths from ``config/config_<doc_type>.yaml`` (the same keys the
shell read via ``yq``): ``paths.doc_root_dir`` -> the shell's
``SCITEX_WRITER_ROOT_DIR`` (the recursive-sweep root) and ``paths.doc_log_dir``
-> the shell's ``LOG_DIR`` (the move target, created if missing). It then:

1. removes ``*bak*`` files recursively under the doc root,
2. removes Emacs temp files (``#*#``) recursively under the doc root,
3. moves top-level-only (maxdepth 1) aux/log files into ``log_dir``,
4. removes ``progress.log`` files recursively under the doc root,
5. removes versioned ``*_v*.pdf`` / ``*_v*.tex`` files in the project root.

Robust by construction: pathlib only (never shells out to find/rm/mv); every
unlink/move target is ``resolve()``-d and asserted to live INSIDE the project
root before touching it (guards ``..`` escapes -- NEVER deletes outside root);
a file that races away mid-sweep is tolerated (only what actually happened is
counted). Fail-loud (explicit error dict + actionable hint) on a missing
project dir / config -- never a silent fallback.
"""

import shutil
from pathlib import Path
from typing import Optional

from ..utils import resolve_project_path
from ..._dataclasses import CleanupResult

DOC_DIRS = {
    "manuscript": "01_manuscript",
    "supplementary": "02_supplementary",
    "revision": "03_revision",
}

# Config key paths (the same ones cleanup.sh read via load_config.sh / yq).
_CFG_DOC_ROOT = ("paths", "doc_root_dir")  # -> SCITEX_WRITER_ROOT_DIR
_CFG_LOG_DIR = ("paths", "doc_log_dir")  # -> LOG_DIR

# Extensions moved (maxdepth 1) into LOG_DIR -- verbatim from cleanup.sh.
_AUX_EXTS = (
    "log",
    "out",
    "bbl",
    "blg",
    "spl",
    "dvi",
    "toc",
    "bak",
    "stderr",
    "stdout",
    "aux",
    "fls",
    "fdb_latexmk",
    "cb",
    "cb2",
)


def _cfg_get(cfg: dict, path, default=None):
    """Nested dict lookup by a key-tuple; ``default`` if any level is absent."""
    cur = cfg
    for key in path:
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _resolve(project_path: Path, rel) -> Optional[Path]:
    """Resolve a config path (possibly ``./``-relative) against the project root."""
    if not rel:
        return None
    rel = str(rel)
    if rel.startswith("./"):
        rel = rel[2:]
    return (project_path / rel).resolve()


def _within(boundary: Path, target: Path) -> bool:
    """True iff ``target`` resolves to a path inside ``boundary`` (guard ``..``)."""
    try:
        target.resolve().relative_to(boundary)
        return True
    except ValueError:
        return False


def _remove_recursive(
    boundary: Path, root: Path, pattern: str, dry_run: bool = False
) -> int:
    """Recursively unlink files matching ``pattern`` under ``root``; return count.

    Only regular files strictly inside ``boundary`` are touched. In ``dry_run``
    mode nothing is unlinked -- the count is what WOULD be removed. A file that
    vanishes mid-sweep (a race) is tolerated -- it just is not counted."""
    if not root or not root.is_dir():
        return 0
    n = 0
    for f in root.rglob(pattern):
        if not f.is_file() or not _within(boundary, f):
            continue
        if dry_run:
            n += 1
            continue
        try:
            f.unlink()
            n += 1
        except FileNotFoundError:
            continue  # raced away -- fine
    return n


def clean(
    project_dir: str, doc_type: str = "manuscript", dry_run: bool = False
) -> dict:
    """Sweep LaTeX build artefacts for ``doc_type`` and return per-category counts.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project directory.
    doc_type : str
        One of 'manuscript' (default), 'supplementary', 'revision'.
    dry_run : bool
        When True, nothing is removed/moved and no directory is created -- the
        returned counts report what WOULD happen (a safe preview).

    Returns
    -------
    dict
        ``{success, bak_removed, emacs_removed, aux_moved, progress_removed,
        versioned_removed, log_dir, dry_run, error}`` -- the serialized
        :class:`CleanupResult`. On failure ``error`` carries an actionable hint
        (fail-loud, never a silent no-op).
    """
    try:
        if doc_type not in DOC_DIRS:
            return {
                "success": False,
                "error": (
                    f"Invalid doc_type '{doc_type}'. "
                    f"Must be one of: {tuple(DOC_DIRS)}"
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

        config_path = project_path / "config" / f"config_{doc_type}.yaml"
        if not config_path.exists():
            return {
                "success": False,
                "error": (
                    f"Config not found: {config_path}. "
                    f"Run `scitex-writer update-project` or check --doc-type."
                ),
            }
        try:
            import yaml
        except ImportError:
            return {
                "success": False,
                "error": "PyYAML not installed. Fix: pip install pyyaml",
            }
        try:
            cfg = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            return {"success": False, "error": f"{config_path} is not valid YAML: {e}"}

        # SCITEX_WRITER_ROOT_DIR (recursive-sweep root) and LOG_DIR (move target).
        doc_root = _resolve(
            project_path, _cfg_get(cfg, _CFG_DOC_ROOT, DOC_DIRS[doc_type])
        )
        log_dir = _resolve(project_path, _cfg_get(cfg, _CFG_LOG_DIR))
        if log_dir is None:
            return {
                "success": False,
                "error": (
                    f"paths.doc_log_dir is missing in {config_path}; "
                    f"cannot resolve the log directory to move aux files into."
                ),
            }

        boundary = project_path.resolve()
        if not _within(boundary, doc_root) or not _within(boundary, log_dir):
            return {
                "success": False,
                "error": (
                    "Refusing to run: doc_root_dir / doc_log_dir resolve OUTSIDE "
                    f"the project root {boundary} (config path escape via '..'?)."
                ),
            }

        # Ensure the log directory exists (mirror the shell's `mkdir -p LOG_DIR`).
        # Skipped in dry-run: a preview must not mutate the filesystem.
        if not dry_run:
            log_dir.mkdir(parents=True, exist_ok=True)

        # 1 + 2: recursive removals under the doc root.
        bak_removed = _remove_recursive(boundary, doc_root, "*bak*", dry_run)
        emacs_removed = _remove_recursive(boundary, doc_root, "#*#", dry_run)

        # 3: move top-level-only (maxdepth 1) aux/log files into LOG_DIR.
        aux_moved = 0
        if doc_root.is_dir():
            for ext in _AUX_EXTS:
                for f in doc_root.glob(f"*.{ext}"):
                    if not f.is_file() or not _within(boundary, f):
                        continue
                    dest = log_dir / f.name
                    if dest.resolve() == f.resolve():
                        continue  # already sitting in the log dir
                    if dry_run:
                        aux_moved += 1
                        continue
                    try:
                        shutil.move(str(f), str(dest))
                        aux_moved += 1
                    except FileNotFoundError:
                        continue  # raced away -- fine

        # 4: recursive progress.log removal.
        progress_removed = _remove_recursive(
            boundary, doc_root, "progress.log", dry_run
        )

        # 5: versioned files in the project root (the shell's `./ *_v*.{pdf,tex}`).
        versioned_removed = 0
        for pattern in ("*_v*.pdf", "*_v*.tex"):
            for f in project_path.glob(pattern):
                if not f.is_file() or not _within(boundary, f):
                    continue
                if dry_run:
                    versioned_removed += 1
                    continue
                try:
                    f.unlink()
                    versioned_removed += 1
                except FileNotFoundError:
                    continue

        result = CleanupResult(
            success=True,
            bak_removed=bak_removed,
            emacs_removed=emacs_removed,
            aux_moved=aux_moved,
            progress_removed=progress_removed,
            versioned_removed=versioned_removed,
            log_dir=str(log_dir),
            dry_run=dry_run,
        )
        result.validate()
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


__all__ = ["clean"]

# EOF
