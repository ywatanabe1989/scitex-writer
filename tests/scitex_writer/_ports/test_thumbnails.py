#!/usr/bin/env python3
"""Tests for the thumbnail service."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

from PIL import Image

from scitex_writer._ports import thumbnails


def _make_png(path: Path, size: tuple[int, int] = (800, 600)) -> None:
    img = Image.new("RGBA", size, (128, 64, 200, 255))
    img.save(path, format="PNG")


def test_thumbnail_key_is_stable_for_unchanged_file(tmp_path: Path):
    """Verify thumbnail_key returns the same value for two calls without changes."""
    # Arrange
    src = tmp_path / "a.png"
    _make_png(src)
    # Act
    k1 = thumbnails.thumbnail_key(src)
    k2 = thumbnails.thumbnail_key(src)
    # Assert
    assert k1 == k2


def test_thumbnail_key_changes_when_mtime_changes(tmp_path: Path):
    """Verify thumbnail_key changes when the source mtime is bumped."""
    # Arrange
    src = tmp_path / "a.png"
    _make_png(src)
    k1 = thumbnails.thumbnail_key(src)
    import os
    import time

    time.sleep(0.01)
    os.utime(src, None)  # bump mtime
    # Act
    k2 = thumbnails.thumbnail_key(src)
    # Assert
    assert k1 != k2


def test_ensure_thumbnail_writes_existing_png_file(tmp_path: Path):
    """Verify ensure_thumbnail produces a thumbnail file for a PNG source."""
    # Arrange
    src = tmp_path / "fig.png"
    _make_png(src, (800, 600))
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    assert thumb is not None and thumb.is_file()


def test_ensure_thumbnail_png_respects_max_edge(tmp_path: Path):
    """Verify thumbnail size respects THUMB_EDGE bound for PNG source."""
    # Arrange
    src = tmp_path / "fig.png"
    _make_png(src, (800, 600))
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    with Image.open(thumb) as img:
        assert max(img.size) <= thumbnails.THUMB_EDGE


def test_ensure_thumbnail_csv_produces_file(tmp_path: Path):
    """Verify ensure_thumbnail produces a thumbnail for a CSV source."""
    # Arrange
    src = tmp_path / "data.csv"
    with src.open("w") as f:
        w = csv.writer(f)
        w.writerow(["cond", "mean", "sd", "n"])
        for i in range(10):
            w.writerow([f"g{i}", i * 1.5, i * 0.2, i])
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "tables", src)
    # Assert
    assert thumb is not None and thumb.is_file()


def test_ensure_thumbnail_csv_size_exceeds_one_kilobyte(tmp_path: Path):
    """Verify CSV thumbnail is a real rendered PNG (not placeholder size)."""
    # Arrange
    src = tmp_path / "data.csv"
    with src.open("w") as f:
        w = csv.writer(f)
        w.writerow(["cond", "mean", "sd", "n"])
        for i in range(10):
            w.writerow([f"g{i}", i * 1.5, i * 0.2, i])
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "tables", src)
    # Assert
    assert thumb.stat().st_size > 1000


def test_cached_thumbnail_path_is_reused_on_second_call(tmp_path: Path):
    """Verify second call returns identical thumbnail path."""
    # Arrange
    src = tmp_path / "a.png"
    _make_png(src)
    first = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Act
    second = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    assert second == first


def test_cached_thumbnail_mtime_is_reused_on_second_call(tmp_path: Path):
    """Verify second call does not rewrite the thumbnail file."""
    # Arrange
    src = tmp_path / "a.png"
    _make_png(src)
    first = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    mtime_first = first.stat().st_mtime
    # Act
    second = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    assert second.stat().st_mtime == mtime_first


def test_find_media_for_stem_returns_match(tmp_path: Path):
    """Verify find_media_for_stem returns a result when raster file is present."""
    # Arrange
    (tmp_path / "fig.pdf").write_bytes(b"%PDF-stub")
    _make_png(tmp_path / "fig.png")
    (tmp_path / "fig.svg").write_text("<svg/>")
    # Act
    match = thumbnails.find_media_for_stem(tmp_path, "fig")
    # Assert
    assert match is not None


def test_find_media_for_stem_prefers_raster_extension(tmp_path: Path):
    """Verify raster (.png) beats vector (.pdf/.svg) when both are present."""
    # Arrange
    (tmp_path / "fig.pdf").write_bytes(b"%PDF-stub")
    _make_png(tmp_path / "fig.png")
    (tmp_path / "fig.svg").write_text("<svg/>")
    # Act
    match = thumbnails.find_media_for_stem(tmp_path, "fig")
    # Assert
    assert match.suffix == ".png"


def test_find_media_walks_into_subdirectories(tmp_path: Path):
    """Verify find_media_for_stem locates files inside subdirectories."""
    # Arrange
    sub = tmp_path / "jpg_for_compilation"
    sub.mkdir()
    _make_png(sub / "fig01.png")
    # Act
    match = thumbnails.find_media_for_stem(tmp_path, "fig01")
    # Assert
    assert match is not None and match.parent == sub


def test_find_media_returns_none_when_no_match_found(tmp_path: Path):
    """Verify find_media_for_stem returns None when nothing matches."""
    # Arrange
    # tmp_path is empty
    # Act
    result = thumbnails.find_media_for_stem(tmp_path, "nope")
    # Assert
    assert result is None


def test_placeholder_rendered_for_unknown_extension(tmp_path: Path):
    """Verify placeholder thumbnail is generated for unknown extension."""
    # Arrange
    src = tmp_path / "x.xyz"
    src.write_bytes(b"unknown binary")
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    assert thumb is not None and thumb.is_file()


def test_placeholder_dimensions_use_thumb_edge_square(tmp_path: Path):
    """Verify placeholder thumbnail uses THUMB_EDGE square dimensions."""
    # Arrange
    src = tmp_path / "x.xyz"
    src.write_bytes(b"unknown binary")
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    with Image.open(thumb) as img:
        assert img.size == (thumbnails.THUMB_EDGE, thumbnails.THUMB_EDGE)


def test_pillow_failure_returns_none_for_corrupt_png(tmp_path: Path):
    """If Pillow raises on an image, ensure_thumbnail logs and returns None."""
    # Arrange
    src = tmp_path / "broken.png"
    src.write_bytes(b"not actually a PNG")
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    assert thumb is None


def test_missing_pandas_falls_back_to_placeholder(tmp_path: Path):
    """If pandas is unavailable, ensure_thumbnail still produces a PNG."""
    # Arrange
    src = tmp_path / "data.csv"
    src.write_text("a,b\n1,2\n")
    saved = {k: sys.modules.get(k) for k in ("pandas", "matplotlib")}
    sys.modules["pandas"] = None
    sys.modules["matplotlib"] = None
    try:
        # Act
        thumb = thumbnails.ensure_thumbnail(tmp_path, "tables", src)
    finally:
        for k, v in saved.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
    # Assert
    assert thumb is not None and thumb.is_file()


def test_thumbnail_cache_directory_is_created(tmp_path: Path):
    """Verify the thumbnail cache directory is created when needed."""
    # Arrange
    src = tmp_path / "a.png"
    _make_png(src)
    # Act
    thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    assert (tmp_path / "00_shared" / "thumbnails" / "figures").is_dir()
