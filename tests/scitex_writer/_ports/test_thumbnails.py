#!/usr/bin/env python3
"""Tests for the thumbnail service."""

from __future__ import annotations

import csv
from pathlib import Path

from PIL import Image

from scitex_writer._ports import thumbnails


def _make_png(path: Path, size: tuple[int, int] = (800, 600)) -> None:
    img = Image.new("RGBA", size, (128, 64, 200, 255))
    img.save(path, format="PNG")


def test_thumbnail_key_stable(tmp_path: Path):
    # Arrange
    src = tmp_path / "a.png"
    _make_png(src)
    k1 = thumbnails.thumbnail_key(src)
    # Act
    k2 = thumbnails.thumbnail_key(src)
    # Assert
    assert k1 == k2


def test_thumbnail_key_changes_on_mtime(tmp_path: Path):
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


def test_renders_png_image_to_a_file(tmp_path: Path):
    # Arrange
    src = tmp_path / "fig.png"
    _make_png(src, (800, 600))
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    assert thumb is not None and thumb.is_file()


def test_rendered_png_thumbnail_fits_within_thumb_edge(tmp_path: Path):
    # Arrange
    src = tmp_path / "fig.png"
    _make_png(src, (800, 600))
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    with Image.open(thumb) as img:
        longest_edge = max(img.size)
    # Assert
    assert longest_edge <= thumbnails.THUMB_EDGE


def test_renders_csv_preview(tmp_path: Path):
    # Arrange
    src = tmp_path / "data.csv"
    with src.open("w") as f:
        w = csv.writer(f)
        w.writerow(["cond", "mean", "sd", "n"])
        for i in range(10):
            w.writerow([f"g{i}", i * 1.5, i * 0.2, i])
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "tables", src)
    is_real_png = thumb is not None and thumb.is_file() and thumb.stat().st_size > 1_000
    # Assert
    assert is_real_png


def test_cached_thumbnail_is_reused_first_is_not_none(tmp_path: Path):
    # Arrange
    src = tmp_path / "a.png"
    _make_png(src)
    # Act
    first = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Act
    # Assert
    assert first is not None


def test_cached_thumbnail_is_reused_second_equals_first_and_second_stat_st_mtime(
    tmp_path: Path,
):
    # Arrange
    src = tmp_path / "a.png"
    _make_png(src)
    first = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    mtime_first = first.stat().st_mtime
    # Call again — should hit cache, not re-render
    # Act
    second = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Act
    # Assert
    assert (second == first) and (second.stat().st_mtime == mtime_first)


def test_find_media_for_stem_prefers_raster(tmp_path: Path):
    # Arrange
    (tmp_path / "fig.pdf").write_bytes(b"%PDF-stub")
    _make_png(tmp_path / "fig.png")
    (tmp_path / "fig.svg").write_text("<svg/>")
    # Act
    match = thumbnails.find_media_for_stem(tmp_path, "fig")
    # Assert
    assert (match is not None) and (match.suffix == ".png")


def test_find_media_walks_subdirs(tmp_path: Path):
    # Arrange
    sub = tmp_path / "jpg_for_compilation"
    sub.mkdir()
    _make_png(sub / "fig01.png")
    # Act
    match = thumbnails.find_media_for_stem(tmp_path, "fig01")
    # Assert
    assert (match is not None) and (match.parent == sub)


def test_find_media_returns_none_when_missing(tmp_path: Path):
    # Arrange
    # Act
    # Assert
    assert thumbnails.find_media_for_stem(tmp_path, "nope") is None


def test_unknown_format_produces_a_thumbnail_file(tmp_path: Path):
    # Arrange
    src = tmp_path / "x.xyz"
    src.write_bytes(b"unknown binary")
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    assert thumb is not None and thumb.is_file()


def test_unknown_format_placeholder_is_square_thumb_edge(tmp_path: Path):
    # Unknown extensions aren't in IMAGE/VECTOR/DATA ext lists, so
    # _render_thumbnail hits the placeholder branch (a square THUMB_EDGE).
    # Arrange
    src = tmp_path / "x.xyz"
    src.write_bytes(b"unknown binary")
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    with Image.open(thumb) as img:
        size = img.size
    # Assert
    assert size == (thumbnails.THUMB_EDGE, thumbnails.THUMB_EDGE)


def test_pillow_failure_returns_none(tmp_path: Path):
    """If Pillow raises on an image, ensure_thumbnail logs and returns None."""
    # Arrange
    src = tmp_path / "broken.png"
    src.write_bytes(b"not actually a PNG")
    # Pillow raises UnidentifiedImageError; our wrapper logs and returns None
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    assert thumb is None


def test_unparseable_csv_falls_back_to_placeholder_thumbnail(tmp_path: Path):
    # An empty CSV makes pandas raise "No columns to parse", driving
    # _render_data_preview into its real placeholder fallback — a genuine
    # exercise of the fallback path without patching the pandas import.
    # Arrange
    src = tmp_path / "empty.csv"
    src.write_text("")
    # Act
    thumb = thumbnails.ensure_thumbnail(tmp_path, "tables", src)
    # Assert
    assert thumb is not None and thumb.is_file()


def test_thumbnail_cache_dir_created(tmp_path: Path):
    # Arrange
    src = tmp_path / "a.png"
    _make_png(src)
    # Act
    thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Assert
    assert (tmp_path / "00_shared" / "thumbnails" / "figures").is_dir()
