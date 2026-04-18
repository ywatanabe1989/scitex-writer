#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_update/_diff.py

"""File comparison and collection for the update handler."""

import hashlib
import shutil
from datetime import datetime
from pathlib import Path

from ._constants import LEGACY_ENGINE_PATHS, SYNC_DIRS, SYNC_FILES


def file_hash(path: Path) -> str:
    """SHA-256 hash of a file's contents."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def should_skip(rel_path: str) -> bool:
    """Return True if this relative path should never be synced."""
    normalized = rel_path.replace("\\", "/")
    if "__pycache__" in normalized:
        return True
    if normalized.endswith(".pyc"):
        return True
    return False


def collect_sync_files(source_root: Path) -> dict[str, Path]:
    """Collect all files to sync from the source, keyed by relative path."""
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
