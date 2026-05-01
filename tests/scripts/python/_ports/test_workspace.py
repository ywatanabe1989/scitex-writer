#!/usr/bin/env python3
"""Tests for the writer-side workspace setup."""

from __future__ import annotations

from pathlib import Path

from scitex_writer._ports.workspace import ensure_scholar_library_link


def test_creates_symlink(tmp_path: Path):
    link = ensure_scholar_library_link(tmp_path)
    assert link is not None
    assert link.is_symlink()
    assert link == tmp_path / "00_shared" / "scholar" / "library"
    assert link.readlink() == Path("~/.scitex/scholar/library").expanduser()


def test_idempotent(tmp_path: Path):
    first = ensure_scholar_library_link(tmp_path)
    second = ensure_scholar_library_link(tmp_path)
    assert first == second


def test_refuses_to_replace_real_directory(tmp_path: Path):
    (tmp_path / "00_shared" / "scholar" / "library").mkdir(parents=True)
    (tmp_path / "00_shared" / "scholar" / "library" / "sentinel").write_text("x")
    link = ensure_scholar_library_link(tmp_path)
    assert link is None
    assert (tmp_path / "00_shared" / "scholar" / "library" / "sentinel").exists()


def test_replaces_stale_symlink(tmp_path: Path):
    other = tmp_path / "other"
    other.mkdir()
    scholar_dir = tmp_path / "00_shared" / "scholar"
    scholar_dir.mkdir(parents=True)
    (scholar_dir / "library").symlink_to(other)

    link = ensure_scholar_library_link(tmp_path)
    assert link is not None
    assert link.readlink() == Path("~/.scitex/scholar/library").expanduser()
