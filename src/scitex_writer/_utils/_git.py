#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_utils/_git.py

"""The ONE git backend for the engine pipelines (diff + archive).

``process_diff.sh`` and ``process_archive.sh`` each shelled out to ``git`` with
``2>/dev/null`` on every call, so a broken repo, a missing binary and a genuine
"no such commit" all collapsed into the same empty string -- and the caller then
guessed. This module keeps the ONE backend (the real ``git`` binary; there is no
second way to read a commit) but separates the three cases:

* ``git`` not on PATH        -> :class:`GitUnavailableError` with an install hint;
* not a repo / no commits    -> a False from :func:`is_repo` / :func:`has_commits`;
* a command that legitimately finds nothing -> ``None`` from the query helpers.

Every helper takes the repository directory explicitly (never relies on the
process CWD, which the shell did).
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import List, Optional


class GitUnavailableError(RuntimeError):
    """Raised when the ``git`` binary is not installed (fail loud, never guess)."""


def require_git() -> str:
    """Return the absolute path of ``git``, or raise with an actionable hint."""
    binary = shutil.which("git")
    if binary is None:
        raise GitUnavailableError(
            "git not found on PATH. The diff and archive pipelines are git-based "
            "(they read previous versions from history and stamp archives with the "
            "commit hash). Fix: install git (e.g. `apt-get install git`)."
        )
    return binary


def _run(repo: Path, args: List[str]) -> subprocess.CompletedProcess:
    """Run ``git <args>`` inside ``repo`` and return the completed process."""
    return subprocess.run(
        [require_git(), "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def is_repo(repo: Path) -> bool:
    """True iff ``repo`` is inside a git working tree."""
    return _run(repo, ["rev-parse", "--git-dir"]).returncode == 0


def has_commits(repo: Path) -> bool:
    """True iff ``repo`` is a git repo carrying at least one commit."""
    return _run(repo, ["rev-parse", "HEAD"]).returncode == 0


def is_clean(repo: Path) -> bool:
    """True iff the working tree has NO staged or unstaged change against HEAD.

    Mirrors the shell's ``is_git_clean``: a repo with no commits, or no repo at
    all, is NOT clean (there is nothing to snapshot against).
    """
    if not has_commits(repo):
        return False
    unstaged = _run(repo, ["diff", "--quiet", "HEAD", "--"]).returncode == 0
    staged = _run(repo, ["diff", "--cached", "--quiet", "HEAD", "--"]).returncode == 0
    return unstaged and staged


def short_hash(repo: Path, commit: str = "HEAD") -> Optional[str]:
    """The 7-char hash of ``commit``, or None when it does not resolve."""
    proc = _run(repo, ["rev-parse", "--short=7", commit])
    if proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def previous_commit(repo: Path, rel_path: str) -> Optional[str]:
    """The second-most-recent commit touching ``rel_path``, or None.

    The shell took ``git log --format=%H -n 2 -- <path> | tail -1``, which for a
    file with exactly ONE commit returns that same commit -- i.e. it diffed a
    version against itself. This returns None in that case, so the caller can say
    so instead of shipping an empty diff (see :mod:`._diff_pipeline`).
    """
    proc = _run(repo, ["log", "--format=%H", "-n", "2", "--", rel_path])
    if proc.returncode != 0:
        return None
    commits = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    if len(commits) < 2:
        return None
    return commits[1]


def show_file(repo: Path, commit: str, rel_path: str) -> Optional[str]:
    """The content of ``rel_path`` at ``commit``, or None when it is not there."""
    proc = _run(repo, ["show", f"{commit}:{rel_path}"])
    if proc.returncode != 0:
        return None
    return proc.stdout


def user_name(repo: Path) -> str:
    """The configured ``user.name``, or ``'unknown'`` (a signature is not a gate)."""
    return _run(repo, ["config", "user.name"]).stdout.strip() or "unknown"


def user_email(repo: Path) -> str:
    """The configured ``user.email``, or ``'unknown'``."""
    return _run(repo, ["config", "user.email"]).stdout.strip() or "unknown"


def current_branch(repo: Path) -> str:
    """The checked-out branch, or ``'unknown'`` on a detached HEAD."""
    return _run(repo, ["branch", "--show-current"]).stdout.strip() or "unknown"


__all__ = [
    "GitUnavailableError",
    "current_branch",
    "has_commits",
    "is_clean",
    "is_repo",
    "previous_commit",
    "require_git",
    "short_hash",
    "show_file",
    "user_email",
    "user_name",
]

# EOF
