#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_update/_git_safety.py

"""Git safety checks for the update handler."""

import subprocess
from pathlib import Path


def is_git_repo(directory: Path) -> bool:
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


def has_uncommitted_changes(directory: Path) -> bool:
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


def git_status_summary(directory: Path) -> str:
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


# EOF
