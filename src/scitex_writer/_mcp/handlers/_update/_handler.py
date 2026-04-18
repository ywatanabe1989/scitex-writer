#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_update/_handler.py

"""Main update handler: orchestrates file sync with safety checks."""

import shutil
from pathlib import Path
from typing import Optional

from ...utils import resolve_project_path
from ._constants import PRESERVED_PATHS
from ._diff import backup_files, collect_sync_files, compare_files
from ._git_safety import (
    git_status_summary,
    has_uncommitted_changes,
    is_git_repo,
)
from ._source import find_package_root, read_version


def update_project(
    project_dir: str,
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    """Update engine files of an existing scitex-writer project.

    Syncs source code, scripts, and build files from the installed
    scitex-writer package to the project. User content is never modified.

    Parameters
    ----------
    project_dir : str
        Path to the existing scitex-writer project.
    branch : str, optional
        Update from a specific template branch (triggers GitHub clone).
    tag : str, optional
        Update from a specific template tag (triggers GitHub clone).
    dry_run : bool
        If True, report what would change without touching any files.
    force : bool
        If True, skip the uncommitted-changes git safety check.

    Returns
    -------
    dict
        success, source, modified, added, unchanged, backup_dir,
        dry_run, git_safe, warnings, message, error (on failure)
    """
    try:
        project_path = resolve_project_path(project_dir)

        if not project_path.exists():
            return {"success": False, "error": f"Project not found: {project_path}"}

        if not (project_path / "00_shared").exists():
            return {
                "success": False,
                "error": (
                    f"{project_path} does not look like a scitex-writer project "
                    "(00_shared/ directory not found)."
                ),
            }

        # Git safety checks
        warnings: list[str] = []
        git_safe = True

        safety_error = _check_git_safety(
            project_path, project_dir, dry_run, force, warnings
        )
        if safety_error:
            return safety_error
        if warnings:
            git_safe = False

        # Resolve source template
        source_dir, is_temp = find_package_root(branch, tag)
        pkg_version = read_version(source_dir)

        try:
            source_files = collect_sync_files(source_dir)
            modified, added, unchanged = compare_files(source_files, project_path)

            backup_dir = None
            if not dry_run and (modified or added):
                backup_dir = _apply_updates(project_path, source_files, modified, added)
        finally:
            if is_temp:
                shutil.rmtree(str(source_dir.parent), ignore_errors=True)

        return {
            "success": True,
            "dry_run": dry_run,
            "git_safe": git_safe,
            "warnings": warnings,
            "source": str(source_dir),
            "version": pkg_version,
            "modified": modified,
            "added": added,
            "unchanged": unchanged,
            "backup_dir": str(backup_dir) if backup_dir else None,
            # Legacy compatibility keys
            "updated_paths": modified + added,
            "skipped_paths": [],
            "missing_paths": [],
            "preserved_paths": [str(p) for p in PRESERVED_PATHS],
            "message": _build_message(
                project_path, modified, added, unchanged, dry_run, backup_dir
            ),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


def _check_git_safety(
    project_path: Path,
    project_dir: str,
    dry_run: bool,
    force: bool,
    warnings: list[str],
) -> Optional[dict]:
    """Check git safety. Returns error dict or None if safe."""
    if is_git_repo(project_path):
        if not dry_run and not force and has_uncommitted_changes(project_path):
            status = git_status_summary(project_path)
            return {
                "success": False,
                "git_safe": False,
                "error": (
                    "Uncommitted changes detected in the project. "
                    "Commit or stash them first so you can revert if needed.\n\n"
                    f"  git -C {project_path} stash\n"
                    f"  scitex-writer update {project_dir}\n"
                    f"  git -C {project_path} stash pop\n\n"
                    f"Or pass --force / force=True to skip this check.\n\n"
                    f"Git status:\n{status}"
                ),
            }
    else:
        warnings.append(
            "Project is not a git repository. "
            "Cannot revert engine changes via git if something goes wrong."
        )
    return None


def _apply_updates(
    project_path: Path,
    source_files: dict[str, Path],
    modified: list[str],
    added: list[str],
) -> Optional[Path]:
    """Apply file updates with backup. Returns backup_dir or None."""
    backup_dir = None
    if modified:
        backup_dir = backup_files(project_path, modified)

    for rel in modified + added:
        src = source_files[rel]
        dst = project_path / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)

    # Ensure compile.sh is executable
    compile_sh = project_path / "compile.sh"
    if compile_sh.exists():
        compile_sh.chmod(compile_sh.stat().st_mode | 0o111)

    # Ensure scripts are executable
    scripts_dir = project_path / "scripts"
    if scripts_dir.is_dir():
        for script in scripts_dir.rglob("*.sh"):
            script.chmod(script.stat().st_mode | 0o111)

    return backup_dir


def _build_message(
    project_path: Path,
    modified: list[str],
    added: list[str],
    unchanged: list[str],
    dry_run: bool,
    backup_dir: Optional[Path],
) -> str:
    """Build a human-readable summary message."""
    parts = []

    if dry_run:
        parts.append("Dry run -- no files modified.")
    else:
        total = len(modified) + len(added)
        if total:
            parts.append(f"Updated {total} file(s) in {project_path}.")
            if backup_dir:
                parts.append(f"Backup: {backup_dir}")
            parts.append(f"Review changes: git -C {project_path} diff")
        else:
            parts.append("Already up to date.")

    parts.append(
        f"{len(modified)} modified, {len(added)} new, {len(unchanged)} unchanged"
    )

    return "\n".join(parts)


# EOF
