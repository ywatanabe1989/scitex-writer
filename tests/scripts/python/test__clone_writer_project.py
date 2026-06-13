#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Wave 2 cluster A batch 1 — NM+TQ003+TQ002+TQ007 cleanup.
"""Tests for scitex_writer._project._create.clone_writer_project.

No-mock rewrite: each test drives the real implementation against either
(a) the existing-directory short-circuit, or
(b) a real local bare git repository so that `git clone` succeeds without
    network access.
"""

import os
import subprocess

import pytest

from scitex_writer._project import _create
from scitex_writer._project._create import clone_writer_project


@pytest.fixture
def local_template_repo(tmp_path):
    """Make TEMPLATE_REPO_URL point at a real local bare git repo.

    Uses a `yield` fixture to set + restore the module-level constant
    without monkeypatching production internals at call-time.
    """
    # Arrange a real bare git repo + one commit so `git clone` succeeds.
    src = tmp_path / "src"
    src.mkdir()
    (src / "README.md").write_text("template\n")
    subprocess.run(["git", "init", "-q"], cwd=src, check=True)
    subprocess.run(["git", "add", "-A"], cwd=src, check=True, capture_output=True)
    env = dict(os.environ)
    env.update(
        {
            "GIT_AUTHOR_NAME": "t",
            "GIT_AUTHOR_EMAIL": "t@t",
            "GIT_COMMITTER_NAME": "t",
            "GIT_COMMITTER_EMAIL": "t@t",
        }
    )
    subprocess.run(
        ["git", "commit", "-q", "-m", "init"],
        cwd=src,
        check=True,
        env=env,
        capture_output=True,
    )
    bare = tmp_path / "tpl.git"
    subprocess.run(
        ["git", "clone", "--bare", "-q", str(src), str(bare)],
        check=True,
        capture_output=True,
    )

    original = _create.TEMPLATE_REPO_URL
    _create.TEMPLATE_REPO_URL = str(bare)
    yield bare
    _create.TEMPLATE_REPO_URL = original


# ============================================================================
# Existing-directory short circuit (no git/network needed)
# ============================================================================


def test_clone_writer_project_existing_directory_returns_false(tmp_path):
    """If project_dir already exists, clone_writer_project returns False without cloning."""
    # Arrange
    project_dir = tmp_path / "existing"
    project_dir.mkdir()
    # Act
    result = clone_writer_project(str(project_dir))
    # Assert
    assert result is False


# ============================================================================
# Real local clone against a bare repo
# ============================================================================


def test_clone_writer_project_default_returns_true_with_local_template(
    tmp_path, local_template_repo
):
    """A real `git clone` of a local bare repo succeeds and returns True."""
    # Arrange
    project_dir = tmp_path / "new_paper"
    # Act
    result = clone_writer_project(str(project_dir))
    # Assert
    assert result is True


def test_clone_writer_project_default_materialises_project_dir(
    tmp_path, local_template_repo
):
    """After a successful clone the project directory contains the cloned README."""
    # Arrange
    project_dir = tmp_path / "new_paper"
    # Act
    clone_writer_project(str(project_dir))
    # Assert
    assert (project_dir / "README.md").exists()


def test_clone_writer_project_child_strategy_creates_fresh_git_dir(
    tmp_path, local_template_repo
):
    """`git_strategy='child'` initialises a brand-new .git in the project root."""
    # Arrange
    project_dir = tmp_path / "new_paper"
    # Act
    clone_writer_project(str(project_dir), git_strategy="child")
    # Assert
    assert (project_dir / ".git").is_dir()


def test_clone_writer_project_none_strategy_removes_git_dir(
    tmp_path, local_template_repo
):
    """`git_strategy='none'` strips the cloned .git directory from the project."""
    # Arrange
    project_dir = tmp_path / "new_paper"
    # Act
    clone_writer_project(str(project_dir), git_strategy="none")
    # Assert
    assert not (project_dir / ".git").exists()


def test_clone_writer_project_origin_strategy_preserves_git_dir(
    tmp_path, local_template_repo
):
    """`git_strategy='origin'` preserves the .git directory from the template."""
    # Arrange
    project_dir = tmp_path / "new_paper"
    # Act
    clone_writer_project(str(project_dir), git_strategy="origin")
    # Assert
    assert (project_dir / ".git").exists()


# ============================================================================
# Branch / tag failure path against a non-existent ref
# ============================================================================


def test_clone_writer_project_unknown_branch_returns_false(
    tmp_path, local_template_repo
):
    """Cloning a non-existent branch of a real repo returns False without raising."""
    # Arrange
    project_dir = tmp_path / "bad_branch"
    # Act
    result = clone_writer_project(str(project_dir), branch="does-not-exist")
    # Assert
    assert result is False


def test_clone_writer_project_unknown_tag_returns_false(tmp_path, local_template_repo):
    """Cloning a non-existent tag of a real repo returns False without raising."""
    # Arrange
    project_dir = tmp_path / "bad_tag"
    # Act
    result = clone_writer_project(str(project_dir), tag="v999.0.0")
    # Assert
    assert result is False
