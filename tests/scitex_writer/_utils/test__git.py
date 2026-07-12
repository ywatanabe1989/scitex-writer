#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_utils/test__git.py

"""Tests for the ONE git backend behind the diff + archive pipelines.

Real repositories throughout: every fixture runs the real ``git`` binary in a
``tmp_path``. No mocks -- the point of this module is that a broken repo, a
missing commit and a clean "nothing found" are told apart, which only a real repo
can demonstrate.
"""

import os
import subprocess

import pytest

from scitex_writer._utils import _git


@pytest.fixture
def empty_path(tmp_path):
    """Point PATH at an EMPTY directory, so no binary resolves (real env seam)."""
    previous = os.environ.get("PATH", "")
    os.environ["PATH"] = str(tmp_path / "empty-bin")
    (tmp_path / "empty-bin").mkdir()
    try:
        yield os.environ["PATH"]
    finally:
        os.environ["PATH"] = previous


def _git_cmd(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    )


def _init_repo(tmp_path):
    """A real git repo with an identity configured; return its path."""
    _git_cmd(tmp_path, "init", "-q")
    _git_cmd(tmp_path, "config", "user.email", "tester@example.com")
    _git_cmd(tmp_path, "config", "user.name", "Tester")
    return tmp_path


def _commit(repo, name, text, message):
    (repo / name).write_text(text, encoding="utf-8")
    _git_cmd(repo, "add", name)
    _git_cmd(repo, "commit", "-q", "-m", message)


class TestRepoDetection:
    def test_plain_directory_is_not_repo(self, tmp_path):
        # Arrange
        plain = tmp_path
        # Act
        detected = _git.is_repo(plain)
        # Assert
        assert detected is False

    def test_initialized_repo_is_detected(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        # Act
        detected = _git.is_repo(repo)
        # Assert
        assert detected is True

    def test_empty_repo_has_no_commits(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        # Act
        detected = _git.has_commits(repo)
        # Assert
        assert detected is False

    def test_committed_repo_has_commits(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        _commit(repo, "a.tex", "one\n", "first")
        # Act
        detected = _git.has_commits(repo)
        # Assert
        assert detected is True


class TestCleanliness:
    def test_committed_tree_is_clean(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        _commit(repo, "a.tex", "one\n", "first")
        # Act
        clean = _git.is_clean(repo)
        # Assert
        assert clean is True

    def test_modified_tree_is_dirty(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        _commit(repo, "a.tex", "one\n", "first")
        (repo / "a.tex").write_text("two\n", encoding="utf-8")
        # Act
        clean = _git.is_clean(repo)
        # Assert
        assert clean is False

    def test_staged_change_is_dirty(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        _commit(repo, "a.tex", "one\n", "first")
        (repo / "a.tex").write_text("two\n", encoding="utf-8")
        _git_cmd(repo, "add", "a.tex")
        # Act
        clean = _git.is_clean(repo)
        # Assert
        assert clean is False

    def test_repo_without_commits_is_not_clean(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        # Act
        clean = _git.is_clean(repo)
        # Assert
        assert clean is False


class TestHistoryQueries:
    def test_short_hash_is_seven_characters(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        _commit(repo, "a.tex", "one\n", "first")
        # Act
        short = _git.short_hash(repo, "HEAD")
        # Assert
        assert len(short) == 7

    def test_unknown_commit_resolves_to_none(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        _commit(repo, "a.tex", "one\n", "first")
        # Act
        short = _git.short_hash(repo, "no-such-ref")
        # Assert
        assert short is None

    def test_single_commit_file_has_no_previous_commit(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        _commit(repo, "a.tex", "one\n", "first")
        # Act
        previous = _git.previous_commit(repo, "a.tex")
        # Assert
        assert previous is None

    def test_twice_committed_file_has_previous_commit(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        _commit(repo, "a.tex", "one\n", "first")
        _commit(repo, "a.tex", "two\n", "second")
        # Act
        previous = _git.previous_commit(repo, "a.tex")
        # Assert
        assert previous is not None

    def test_show_file_returns_previous_content(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        _commit(repo, "a.tex", "one\n", "first")
        _commit(repo, "a.tex", "two\n", "second")
        previous = _git.previous_commit(repo, "a.tex")
        # Act
        content = _git.show_file(repo, previous, "a.tex")
        # Assert
        assert content == "one\n"

    def test_show_file_of_untracked_path_returns_none(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        _commit(repo, "a.tex", "one\n", "first")
        # Act
        content = _git.show_file(repo, "HEAD", "absent.tex")
        # Assert
        assert content is None

    def test_configured_user_name_is_read_back(self, tmp_path):
        # Arrange
        repo = _init_repo(tmp_path)
        _commit(repo, "a.tex", "one\n", "first")
        # Act
        name = _git.user_name(repo)
        # Assert
        assert name == "Tester"


class TestFailLoud:
    def test_require_git_returns_binary_path(self):
        # Arrange
        # Act
        binary = _git.require_git()
        # Assert
        assert binary.endswith("git")

    def test_missing_git_raises_actionable_error(self, empty_path):
        # Arrange
        # (``empty_path`` points PATH at an empty dir for the duration.)
        # Act
        # Assert
        with pytest.raises(_git.GitUnavailableError, match="install git"):
            _git.require_git()
