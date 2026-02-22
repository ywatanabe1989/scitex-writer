#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_update.py

"""Update handler: refresh engine files while preserving user content."""


import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from ..utils import resolve_project_path

TEMPLATE_REPO_URL = "https://github.com/ywatanabe1989/scitex-writer.git"

# Engine paths to update (relative to project root)
ENGINE_PATHS = [
    "scripts",
    Path("00_shared") / "latex_styles",
    Path("01_manuscript") / "base.tex",
    Path("02_supplementary") / "base.tex",
    Path("03_revision") / "base.tex",
    "compile.sh",
    "Makefile",
]

# User content — never touch (used for documentation in results only)
PRESERVED_PATHS = [
    Path("00_shared") / "authors.tex",
    Path("00_shared") / "title.tex",
    Path("00_shared") / "keywords.tex",
    Path("00_shared") / "journal_name.tex",
    Path("00_shared") / "bib_files" / "bibliography.bib",
    Path("00_shared") / "claims.json",
    Path("01_manuscript") / "contents",
    Path("02_supplementary") / "contents",
    Path("03_revision") / "contents",
]


# ---------------------------------------------------------------------------
# Git safety helpers
# ---------------------------------------------------------------------------


def _is_git_repo(directory: Path) -> bool:
    """Return True if directory is inside a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=str(directory),
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def _has_uncommitted_changes(directory: Path) -> bool:
    """Return True if git working tree has uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(directory),
            capture_output=True,
            text=True,
            timeout=10,
        )
        return bool(result.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def _git_status_summary(directory: Path) -> str:
    """Return a short git status summary for error messages."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(directory),
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = result.stdout.strip().splitlines()
        if len(lines) > 5:
            return "\n".join(lines[:5]) + f"\n  ... and {len(lines) - 5} more"
        return result.stdout.strip()
    except Exception:
        return "(could not read git status)"


# ---------------------------------------------------------------------------
# Source resolution
# ---------------------------------------------------------------------------


def _find_source_dir(branch: Optional[str], tag: Optional[str]) -> tuple[Path, bool]:
    """Return (source_dir, is_temp). Prefers installed package; falls back to GitHub clone.

    Returns
    -------
    source_dir : Path
        Root of the scitex-writer template to copy from.
    is_temp : bool
        True if source_dir is a temporary clone that must be deleted after use.
    """
    # Try installed/editable package: navigate up from this file to project root
    # _update.py → handlers/ → _mcp/ → scitex_writer/ → src/ → project_root/
    candidate = Path(__file__).parent.parent.parent.parent.parent
    if (candidate / "scripts").exists() and (candidate / "00_shared").exists():
        # Only usable when branch/tag are not requested (or match installed)
        if not branch and not tag:
            return candidate, False

    # Fallback: clone from GitHub
    tmp_dir = tempfile.mkdtemp(prefix="scitex_writer_update_")
    tmp_path = Path(tmp_dir)
    cmd = ["git", "clone", "--depth", "1"]
    if branch:
        cmd.extend(["--branch", branch])
    elif tag:
        cmd.extend(["--branch", tag])
    cmd.extend([TEMPLATE_REPO_URL, str(tmp_path / "repo")])
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        shutil.rmtree(tmp_dir, ignore_errors=True)
        raise RuntimeError(f"Git clone failed: {result.stderr.strip()}")
    return tmp_path / "repo", True


# ---------------------------------------------------------------------------
# File operations
# ---------------------------------------------------------------------------


def _copy_engine_path(src: Path, dst: Path, dry_run: bool) -> str:
    """Copy one engine path from src to dst. Returns status string."""
    if not src.exists():
        return "missing"
    if dry_run:
        return "would_update"
    if dst.exists():
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return "updated"


# ---------------------------------------------------------------------------
# Public handler
# ---------------------------------------------------------------------------


def update_project(
    project_dir: str,
    branch: Optional[str] = None,
    tag: Optional[str] = None,
    dry_run: bool = False,
    force: bool = False,
) -> dict:
    """Update engine files of an existing scitex-writer project.

    Replaces build scripts, LaTeX styles, and base templates with the latest
    version from scitex-writer. User content (manuscript text, bibliography,
    figures, tables, metadata) is never modified.

    Git safety:
    - If the project is a git repository, uncommitted changes are blocked
      (commit or ``git stash`` first, or pass ``force=True`` to override).
    - If the project has no git history, a warning is included in the result
      (no revert possible via git).

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
        success, source, updated_paths, skipped_paths, dry_run, git_safe,
        warnings, message
    """
    try:
        project_path = resolve_project_path(project_dir)

        if not project_path.exists():
            return {"success": False, "error": f"Project not found: {project_path}"}

        # Validate it's a scitex-writer project (00_shared/ is the marker)
        if not (project_path / "00_shared").exists():
            return {
                "success": False,
                "error": (
                    f"{project_path} does not look like a scitex-writer project "
                    "(00_shared/ directory not found)."
                ),
            }

        # ----------------------------------------------------------------
        # Git safety checks
        # ----------------------------------------------------------------
        warnings = []
        git_safe = True

        if _is_git_repo(project_path):
            if not dry_run and not force and _has_uncommitted_changes(project_path):
                status = _git_status_summary(project_path)
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
            # Not a git repo — warn but allow (no revert path available)
            warnings.append(
                "Project is not a git repository. "
                "Cannot revert engine changes via git if something goes wrong."
            )
            git_safe = False

        # ----------------------------------------------------------------
        # Resolve source template
        # ----------------------------------------------------------------
        source_dir, is_temp = _find_source_dir(branch, tag)

        updated, skipped, missing = [], [], []
        try:
            for rel in ENGINE_PATHS:
                rel = Path(rel)
                src = source_dir / rel
                dst = project_path / rel
                status = _copy_engine_path(src, dst, dry_run)
                if status in ("updated", "would_update"):
                    updated.append(str(rel))
                elif status == "skipped":
                    skipped.append(str(rel))
                else:
                    missing.append(str(rel))

            # Ensure compile.sh is executable
            compile_sh = project_path / "compile.sh"
            if not dry_run and compile_sh.exists():
                compile_sh.chmod(compile_sh.stat().st_mode | 0o111)
        finally:
            if is_temp:
                shutil.rmtree(str(source_dir.parent), ignore_errors=True)

        verb = "Would update" if dry_run else "Updated"
        hint = "" if dry_run else f"\nReview changes: git -C {project_path} diff"
        return {
            "success": True,
            "dry_run": dry_run,
            "git_safe": git_safe,
            "warnings": warnings,
            "source": str(source_dir),
            "updated_paths": updated,
            "skipped_paths": skipped,
            "missing_paths": missing,
            "preserved_paths": [str(p) for p in PRESERVED_PATHS],
            "message": (
                f"{verb} {len(updated)} engine path(s) in {project_path}. "
                f"User content preserved.{hint}"
            ),
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


# EOF
