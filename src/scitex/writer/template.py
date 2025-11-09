#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Template management for scitex-writer.

Provides functions to clone and initialize writer projects.
"""

from pathlib import Path
from typing import Optional
import subprocess
import shutil
import os


def clone_writer_project(
    project_name: str,
    target_dir: Optional[str] = None,
    git_strategy: str = "child",
) -> bool:
    """
    Clone scitex-writer template to create a new manuscript project.

    Args:
        project_name: Name of the new project
        target_dir: Directory where project will be created (default: current directory)
        git_strategy: Git initialization strategy
            - 'child': Create isolated git in project directory (default)
            - 'parent': Use parent git repository
            - 'origin': Preserve template's original git history
            - None: Disable git initialization

    Returns:
        True if successful, False otherwise

    Example:
        >>> from scitex.writer import clone_writer_project
        >>> clone_writer_project("my_paper")
        >>> clone_writer_project("my_paper", target_dir="/path/to/papers")
    """
    # Get template directory (from installed package)
    template_dir = Path(__file__).parent.parent.parent.parent

    # Determine target path
    if target_dir:
        target_path = Path(target_dir) / project_name
    else:
        target_path = Path.cwd() / project_name

    if target_path.exists():
        print(f"Error: Directory already exists: {target_path}")
        return False

    try:
        # Copy template
        shutil.copytree(
            template_dir,
            target_path,
            ignore=shutil.ignore_patterns(
                ".git",
                "__pycache__",
                "*.pyc",
                ".pytest_cache",
                "*.egg-info",
                "dist",
                "build",
                ".backup_*",
            ),
        )

        # Initialize git if requested
        if git_strategy == "child":
            subprocess.run(
                ["git", "init"],
                cwd=target_path,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "add", "."],
                cwd=target_path,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", f"Initialize {project_name} from scitex-writer template"],
                cwd=target_path,
                capture_output=True,
                check=True,
            )
        elif git_strategy == "parent":
            # Use parent git, do nothing
            pass
        elif git_strategy == "origin":
            # Keep original git history (already copied)
            pass

        print(f"Successfully created project: {target_path}")
        print(f"\nNext steps:")
        print(f"  cd {target_path}")
        print(f"  ./compile.sh")

        return True

    except Exception as e:
        print(f"Error creating project: {e}")
        if target_path.exists():
            shutil.rmtree(target_path)
        return False


__all__ = ["clone_writer_project"]
