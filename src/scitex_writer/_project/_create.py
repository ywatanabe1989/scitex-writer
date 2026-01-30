#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_project/_create.py

"""
Project creation logic for writer module.

Handles creating new writer projects from template.
"""

from __future__ import annotations

import shutil
import subprocess
from logging import getLogger
from pathlib import Path
from typing import Optional

logger = getLogger(__name__)

# Template repository URL
TEMPLATE_REPO_URL = "https://github.com/ywatanabe1989/scitex-writer.git"


def clone_writer_project(
    project_dir: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
) -> bool:
    """
    Initialize a new writer project directory from scitex-writer template.

    Args:
        project_dir: Path to project directory (will be created)
        git_strategy: Git initialization strategy (optional)
            - 'child': Create isolated git in project directory (default)
            - 'parent': Use parent git repository
            - 'origin': Preserve template's original git history
            - None or 'none': Disable git initialization
        branch: Specific branch of the template repository to clone (optional)
            If None, clones the default branch. Mutually exclusive with tag.
        tag: Specific tag/release of the template repository to clone (optional)
            If None, clones the default branch. Mutually exclusive with branch.

    Returns:
        True if successful, False otherwise

    Examples:
        >>> clone_writer_project("my_paper")
        >>> clone_writer_project("./papers/my_paper")
        >>> clone_writer_project("my_paper", git_strategy="parent")
        >>> clone_writer_project("my_paper", branch="develop")
        >>> clone_writer_project("my_paper", tag="v1.0.0")
    """
    try:
        project_path = Path(project_dir)

        if project_path.exists():
            logger.error(f"Directory already exists: {project_path}")
            return False

        # Build git clone command
        cmd = ["git", "clone"]

        if branch:
            cmd.extend(["--branch", branch])
        elif tag:
            cmd.extend(["--branch", tag])

        cmd.extend([TEMPLATE_REPO_URL, str(project_path)])

        # Execute git clone
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            logger.error(f"Git clone failed: {result.stderr}")
            return False

        # Handle git strategy
        if git_strategy == "none" or git_strategy is None:
            git_dir = project_path / ".git"
            if git_dir.exists():
                shutil.rmtree(git_dir)
        elif git_strategy == "child":
            git_dir = project_path / ".git"
            if git_dir.exists():
                shutil.rmtree(git_dir)
            subprocess.run(["git", "init"], cwd=str(project_path), capture_output=True)
            subprocess.run(
                ["git", "add", "."], cwd=str(project_path), capture_output=True
            )
            subprocess.run(
                ["git", "commit", "-m", "Initial commit from scitex-writer template"],
                cwd=str(project_path),
                capture_output=True,
            )
        # "parent" and "origin" strategies keep the git history as-is

        logger.info(f"Successfully created writer project at {project_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to initialize writer directory: {e}")
        return False


def ensure_project_exists(
    project_dir: Path,
    project_name: str,
    git_strategy: Optional[str] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
) -> Path:
    """
    Ensure project directory exists, creating it if necessary.

    Parameters
    ----------
    project_dir : Path
        Path to project directory
    project_name : str
        Name of the project
    git_strategy : str or None
        Git initialization strategy
    branch : str, optional
        Specific branch of template repository to clone. If None, clones the default branch.
        Mutually exclusive with tag parameter.
    tag : str, optional
        Specific tag/release of template repository to clone. If None, clones the default branch.
        Mutually exclusive with branch parameter.

    Returns
    -------
    Path
        Path to the project directory

    Raises
    ------
    RuntimeError
        If project creation fails
    """
    if project_dir.exists():
        logger.info(f"Attached to existing project at {project_dir.absolute()}")
        return project_dir

    logger.info(f"Creating new project '{project_name}' at {project_dir.absolute()}")

    # Initialize project directory structure
    success = clone_writer_project(str(project_dir), git_strategy, branch, tag)

    if not success:
        logger.error(f"Failed to initialize project directory for {project_name}")
        raise RuntimeError(f"Could not create project directory at {project_dir}")

    # Verify project directory was created
    if not project_dir.exists():
        logger.error(f"Project directory {project_dir} was not created")
        raise RuntimeError(f"Project directory {project_dir} was not created")

    logger.info(f"Successfully created project at {project_dir.absolute()}")
    return project_dir


__all__ = ["ensure_project_exists", "clone_writer_project"]

# EOF
