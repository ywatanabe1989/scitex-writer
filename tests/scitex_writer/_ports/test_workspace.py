#!/usr/bin/env python3
"""Tests for the writer-side workspace setup."""

from __future__ import annotations

from pathlib import Path

from scitex_writer._ports.workspace import ensure_scholar_library_link


def test_creates_symlink_returns_non_none_path(tmp_path: Path):
    """Verify ensure_scholar_library_link returns a non-None path."""
    # Arrange
    # tmp_path provided by fixture
    # Act
    link = ensure_scholar_library_link(tmp_path)
    # Assert
    assert link is not None


def test_creates_symlink_path_is_symlink(tmp_path: Path):
    """Verify returned link is a symlink."""
    # Arrange
    # tmp_path provided by fixture
    # Act
    link = ensure_scholar_library_link(tmp_path)
    # Assert
    assert link.is_symlink()


def test_creates_symlink_path_uses_canonical_location(tmp_path: Path):
    """Verify symlink is created at <root>/00_shared/scholar/library."""
    # Arrange
    # tmp_path provided by fixture
    # Act
    link = ensure_scholar_library_link(tmp_path)
    # Assert
    assert link == tmp_path / "00_shared" / "scholar" / "library"


def test_creates_symlink_targets_user_scitex_scholar_library(tmp_path: Path):
    """Verify symlink target resolves to ~/.scitex/scholar/library."""
    # Arrange
    # tmp_path provided by fixture
    # Act
    link = ensure_scholar_library_link(tmp_path)
    # Assert
    assert link.readlink() == Path("~/.scitex/scholar/library").expanduser()


def test_idempotent_returns_same_path_for_repeated_calls(tmp_path: Path):
    """Verify ensure_scholar_library_link is idempotent."""
    # Arrange
    first = ensure_scholar_library_link(tmp_path)
    # Act
    second = ensure_scholar_library_link(tmp_path)
    # Assert
    assert first == second


def test_refuses_to_replace_real_directory_returns_none(tmp_path: Path):
    """Verify None is returned when a real directory occupies the link path."""
    # Arrange
    (tmp_path / "00_shared" / "scholar" / "library").mkdir(parents=True)
    (tmp_path / "00_shared" / "scholar" / "library" / "sentinel").write_text("x")
    # Act
    link = ensure_scholar_library_link(tmp_path)
    # Assert
    assert link is None


def test_refuses_to_replace_real_directory_preserves_contents(tmp_path: Path):
    """Verify pre-existing files inside the real directory are kept intact."""
    # Arrange
    (tmp_path / "00_shared" / "scholar" / "library").mkdir(parents=True)
    sentinel = tmp_path / "00_shared" / "scholar" / "library" / "sentinel"
    sentinel.write_text("x")
    # Act
    ensure_scholar_library_link(tmp_path)
    # Assert
    assert sentinel.exists()


def test_replaces_stale_symlink_returns_non_none(tmp_path: Path):
    """Verify a stale symlink is replaced and a new link path is returned."""
    # Arrange
    other = tmp_path / "other"
    other.mkdir()
    scholar_dir = tmp_path / "00_shared" / "scholar"
    scholar_dir.mkdir(parents=True)
    (scholar_dir / "library").symlink_to(other)
    # Act
    link = ensure_scholar_library_link(tmp_path)
    # Assert
    assert link is not None


def test_replaces_stale_symlink_uses_canonical_target(tmp_path: Path):
    """Verify replacement symlink points to ~/.scitex/scholar/library."""
    # Arrange
    other = tmp_path / "other"
    other.mkdir()
    scholar_dir = tmp_path / "00_shared" / "scholar"
    scholar_dir.mkdir(parents=True)
    (scholar_dir / "library").symlink_to(other)
    # Act
    link = ensure_scholar_library_link(tmp_path)
    # Assert
    assert link.readlink() == Path("~/.scitex/scholar/library").expanduser()
