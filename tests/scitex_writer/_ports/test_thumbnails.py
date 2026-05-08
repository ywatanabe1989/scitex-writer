#!/usr/bin/env python3
"""Tests for the thumbnail service."""

from __future__ import annotations

import csv
from pathlib import Path
from unittest import mock

from PIL import Image

from scitex_writer._ports import thumbnails


def _make_png(path: Path, size: tuple[int, int] = (800, 600)) -> None:
    img = Image.new("RGBA", size, (128, 64, 200, 255))
    img.save(path, format="PNG")


def test_thumbnail_key_stable(tmp_path: Path):
    src = tmp_path / "a.png"
    _make_png(src)
    k1 = thumbnails.thumbnail_key(src)
    k2 = thumbnails.thumbnail_key(src)
    assert k1 == k2


def test_thumbnail_key_changes_on_mtime(tmp_path: Path):
    src = tmp_path / "a.png"
    _make_png(src)
    k1 = thumbnails.thumbnail_key(src)
    import os
    import time

    time.sleep(0.01)
    os.utime(src, None)  # bump mtime
    k2 = thumbnails.thumbnail_key(src)
    assert k1 != k2


def test_renders_png_image(tmp_path: Path):
    src = tmp_path / "fig.png"
    _make_png(src, (800, 600))
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    assert thumb is not None
    assert thumb.is_file()
    with Image.open(thumb) as img:
        assert max(img.size) <= thumbnails.THUMB_EDGE


def test_renders_csv_preview(tmp_path: Path):
    src = tmp_path / "data.csv"
    with src.open("w") as f:
        w = csv.writer(f)
        w.writerow(["cond", "mean", "sd", "n"])
        for i in range(10):
            w.writerow([f"g{i}", i * 1.5, i * 0.2, i])
    thumb = thumbnails.ensure_thumbnail(tmp_path, "tables", src)
    assert thumb is not None and thumb.is_file()
    assert thumb.stat().st_size > 1000  # real rendered PNG, not placeholder


def test_cached_thumbnail_is_reused(tmp_path: Path):
    src = tmp_path / "a.png"
    _make_png(src)
    first = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    assert first is not None
    mtime_first = first.stat().st_mtime
    # Call again — should hit cache, not re-render
    second = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    assert second == first
    assert second.stat().st_mtime == mtime_first


def test_find_media_for_stem_prefers_raster(tmp_path: Path):
    (tmp_path / "fig.pdf").write_bytes(b"%PDF-stub")
    _make_png(tmp_path / "fig.png")
    (tmp_path / "fig.svg").write_text("<svg/>")
    match = thumbnails.find_media_for_stem(tmp_path, "fig")
    assert match is not None
    assert match.suffix == ".png"  # raster beats vector


def test_find_media_walks_subdirs(tmp_path: Path):
    sub = tmp_path / "jpg_for_compilation"
    sub.mkdir()
    _make_png(sub / "fig01.png")
    match = thumbnails.find_media_for_stem(tmp_path, "fig01")
    assert match is not None
    assert match.parent == sub


def test_find_media_returns_none_when_missing(tmp_path: Path):
    assert thumbnails.find_media_for_stem(tmp_path, "nope") is None


def test_placeholder_rendered_for_unknown_format(tmp_path: Path):
    src = tmp_path / "x.xyz"
    src.write_bytes(b"unknown binary")
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    # Unknown extensions aren't in IMAGE/VECTOR/DATA ext lists, so
    # `_render_thumbnail` hits the placeholder branch.
    assert thumb is not None and thumb.is_file()
    with Image.open(thumb) as img:
        assert img.size == (thumbnails.THUMB_EDGE, thumbnails.THUMB_EDGE)


def test_pillow_failure_returns_none(tmp_path: Path):
    """If Pillow raises on an image, ensure_thumbnail logs and returns None."""
    src = tmp_path / "broken.png"
    src.write_bytes(b"not actually a PNG")
    # Pillow raises UnidentifiedImageError; our wrapper logs and returns None
    thumb = thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    assert thumb is None


def test_missing_pandas_falls_back_to_placeholder(tmp_path: Path):
    src = tmp_path / "data.csv"
    src.write_text("a,b\n1,2\n")
    # Simulate pandas not being installed by patching the import
    with mock.patch.dict("sys.modules", {"pandas": None, "matplotlib": None}):
        thumb = thumbnails.ensure_thumbnail(tmp_path, "tables", src)
    # Fallback placeholder still generates a PNG
    assert thumb is not None and thumb.is_file()


def test_thumbnail_cache_dir_created(tmp_path: Path):
    src = tmp_path / "a.png"
    _make_png(src)
    thumbnails.ensure_thumbnail(tmp_path, "figures", src)
    assert (tmp_path / "00_shared" / "thumbnails" / "figures").is_dir()
