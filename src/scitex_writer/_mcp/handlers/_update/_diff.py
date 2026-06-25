#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_update/_diff.py

"""File comparison and collection for the update handler."""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path

from ._constants import (
    ACTIVE_STYLE_DOC_DIRS,
    LEGACY_ENGINE_PATHS,
    SKIP_DIR_NAMES,
    SYNC_DIRS,
    SYNC_FILES,
    TEMPLATE_STYLE_DIR,
)


def file_hash(path: Path) -> str:
    """SHA-256 hash of a file's contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8_192), b""):
            h.update(chunk)
    return h.hexdigest()


def should_skip(rel_path: str) -> bool:
    """Return True if this relative path should never be synced.

    Skips build artifacts, caches, and vendored deps (node_modules, sphinx
    HTML, ...) so the drift report shows only real, editable engine files.
    """
    parts = rel_path.replace("\\", "/").split("/")
    if any(part in SKIP_DIR_NAMES for part in parts):
        return True
    if any(part.endswith(".egg-info") for part in parts):
        return True
    return rel_path.endswith((".pyc", ".pyo"))


def collect_sync_files(source_root: Path, project_root: Path) -> dict[str, Path]:
    """Collect template files to sync, keyed by their path in the PROJECT.

    Most files keep the same relative path. Rendering style files are keyed by
    the ACTIVE compiled path (``<doc>/contents/latex_styles/``) so drift is
    caught in the copy the manuscript actually compiles, even when that path is
    a symlink to a diverged directory.
    """
    files: dict[str, Path] = {}

    for sync_dir in SYNC_DIRS:
        src_dir = source_root / sync_dir
        if not src_dir.is_dir():
            continue
        for src_file in src_dir.rglob("*"):
            if not src_file.is_file():
                continue
            rel = str(src_file.relative_to(source_root))
            if not should_skip(rel):
                files[rel] = src_file

    for sync_file in SYNC_FILES:
        src_file = source_root / sync_file
        if src_file.is_file():
            files[sync_file] = src_file

    for legacy_path in LEGACY_ENGINE_PATHS:
        legacy_path = Path(legacy_path)
        src = source_root / legacy_path
        if src.is_file():
            files[str(legacy_path)] = src
        elif src.is_dir():
            for src_file in src.rglob("*"):
                if src_file.is_file():
                    rel = str(src_file.relative_to(source_root))
                    if not should_skip(rel):
                        files[rel] = src_file

    # Rendering style files: key by the ACTIVE compiled path, only for doc
    # types that actually have a latex_styles dir (so we never create style
    # files where the manuscript would not read them).
    styles_src = source_root / TEMPLATE_STYLE_DIR
    if styles_src.is_dir():
        for src_file in sorted(styles_src.glob("*.tex")):
            for doc_dir in ACTIVE_STYLE_DOC_DIRS:
                if not (project_root / doc_dir / "contents" / "latex_styles").exists():
                    continue
                active_rel = str(
                    Path(doc_dir) / "contents" / "latex_styles" / src_file.name
                )
                files[active_rel] = src_file

    return files


def compare_files(
    source_files: dict[str, Path], project_root: Path
) -> tuple[list[str], list[str], list[str]]:
    """Compare source files against project files.

    Returns
    -------
    modified : list[str]
        Relative paths where source differs from project.
    added : list[str]
        Relative paths that exist in source but not in project.
    unchanged : list[str]
        Relative paths that are identical.
    """
    modified, added, unchanged = [], [], []

    for rel in sorted(source_files.keys()):
        src_path = source_files[rel]
        dst_path = project_root / rel
        if not dst_path.exists():
            added.append(rel)
        elif file_hash(src_path) != file_hash(dst_path):
            modified.append(rel)
        else:
            unchanged.append(rel)

    return modified, added, unchanged


def backup_files(project_root: Path, rel_paths: list[str]) -> Path:
    """Create backup of files that will be modified.

    Returns the backup directory path.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = project_root / ".update_backup" / timestamp

    for rel in rel_paths:
        src = project_root / rel
        if src.exists():
            dst = backup_dir / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)

    return backup_dir


# EOF
