#!/usr/bin/env python3
"""Tests for the writer-side workspace setup."""

from __future__ import annotations

from pathlib import Path

from scitex_writer._ports.workspace import ensure_scholar_library_link


def test_creates_symlink_link_is_not_none_and_link_is_symlink_and_link_tmp_(tmp_path: Path):
    # Arrange
    # Act
    link = ensure_scholar_library_link(tmp_path)
    # Assert
    assert (link is not None) and (link.is_symlink()) and (link == tmp_path / '00_shared' / 'scholar' / 'library') and (link.readlink() == Path('~/.scitex/scholar/library').expanduser())


def test_idempotent_first_equals_second(tmp_path: Path):
    # Arrange
    first = ensure_scholar_library_link(tmp_path)
    # Act
    second = ensure_scholar_library_link(tmp_path)
    # Assert
    assert first == second


def test_refuses_to_replace_real_directory(tmp_path: Path):
    # Arrange
    (tmp_path / "00_shared" / "scholar" / "library").mkdir(parents=True)
    (tmp_path / "00_shared" / "scholar" / "library" / "sentinel").write_text("x")
    # Act
    link = ensure_scholar_library_link(tmp_path)
    # Assert
    assert (link is None) and ((tmp_path / '00_shared' / 'scholar' / 'library' / 'sentinel').exists())


def test_replaces_stale_symlink(tmp_path: Path):
    # Arrange
    other = tmp_path / "other"
    other.mkdir()
    scholar_dir = tmp_path / "00_shared" / "scholar"
    scholar_dir.mkdir(parents=True)
    (scholar_dir / "library").symlink_to(other)

    # Act
    link = ensure_scholar_library_link(tmp_path)
    # Assert
    assert (link is not None) and (link.readlink() == Path('~/.scitex/scholar/library').expanduser())
