#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_utils/test__figure_image.py

"""Tests for the single Pillow image backend of the figure engine.

Real images written to ``tmp_path`` throughout -- no mocks. These are the
regression guard for the silent ImageMagick fallthroughs the shell had: a crop
that did nothing and a "composite" that was really just the first panel.
"""

import pytest
from PIL import Image

from scitex_writer._utils import _figure_image


def _write_png(path, size=(40, 30), color=(200, 30, 30), alpha=None):
    """Write a real PNG fixture; ``alpha`` makes it RGBA with that opacity."""
    mode = "RGBA" if alpha is not None else "RGB"
    fill = (*color, alpha) if alpha is not None else color
    Image.new(mode, size, fill).save(path, "PNG")
    return path


class TestToJpg:
    def test_png_is_converted_to_jpeg(self, tmp_path):
        # Arrange
        src = _write_png(tmp_path / "in.png")
        # Act
        dst = _figure_image.to_jpg(src, tmp_path / "out.jpg")
        # Assert
        with Image.open(dst) as image:
            assert image.format == "JPEG"

    def test_transparent_png_flattens_onto_white(self, tmp_path):
        # Arrange: a fully transparent PNG must become WHITE, not black -- JPEG has
        # no alpha, and Pillow's naive convert() would blacken the figure.
        src = _write_png(tmp_path / "clear.png", color=(0, 0, 0), alpha=0)
        # Act
        dst = _figure_image.to_jpg(src, tmp_path / "clear.jpg")
        # Assert
        with Image.open(dst) as image:
            assert image.convert("RGB").getpixel((0, 0)) == (255, 255, 255)

    def test_missing_source_fails_loud(self, tmp_path):
        # Arrange
        absent = tmp_path / "nope.png"
        # Act
        # Assert
        with pytest.raises(FileNotFoundError, match="nope.png"):
            _figure_image.to_jpg(absent, tmp_path / "out.jpg")

    def test_corrupt_source_fails_loud(self, tmp_path):
        # Arrange
        broken = tmp_path / "broken.png"
        broken.write_bytes(b"not an image at all")
        # Act
        # Assert
        with pytest.raises(ValueError, match="not a readable image"):
            _figure_image.to_jpg(broken, tmp_path / "out.jpg")


class TestToPng:
    def test_tiff_is_converted_to_png(self, tmp_path):
        # Arrange
        src = tmp_path / "in.tif"
        Image.new("RGB", (20, 20), (10, 120, 10)).save(src, "TIFF")
        # Act
        dst = _figure_image.to_png(src, tmp_path / "out.png")
        # Assert
        with Image.open(dst) as image:
            assert image.format == "PNG"


class TestTrimWhitespace:
    def test_uniform_border_is_cropped_away(self, tmp_path):
        # Arrange: a 60x60 white canvas with a 20x20 red square inset at (20, 20).
        canvas = Image.new("RGB", (60, 60), (255, 255, 255))
        canvas.paste(Image.new("RGB", (20, 20), (255, 0, 0)), (20, 20))
        target = tmp_path / "padded.jpg"
        canvas.save(target, "JPEG", quality=95)
        # Act
        _figure_image.trim_whitespace(target)
        # Assert
        with Image.open(target) as image:
            assert image.size == (20, 20)

    def test_uniform_image_is_left_untouched(self, tmp_path):
        # Arrange: cropping an all-one-colour image to its bbox would destroy it.
        target = tmp_path / "flat.jpg"
        Image.new("RGB", (30, 30), (128, 128, 128)).save(target, "JPEG")
        # Act
        changed = _figure_image.trim_whitespace(target)
        # Assert
        assert changed is False


class TestPlaceholderJpg:
    def test_placeholder_is_a_real_jpeg(self, tmp_path):
        # Arrange: NEVER a .txt -- \includegraphics needs a real raster.
        dst = tmp_path / "01_missing.jpg"
        # Act
        _figure_image.placeholder_jpg(dst, "01_missing")
        # Assert
        with Image.open(dst) as image:
            assert image.format == "JPEG"


class TestLayout:
    def test_four_panels_use_a_two_by_two_grid(self):
        # Arrange
        num_panels = 4
        # Act
        layout = _figure_image.calculate_layout(num_panels)
        # Assert
        assert layout == (2, 2)

    def test_many_panels_use_a_near_square_grid(self):
        # Arrange
        num_panels = 12
        # Act
        rows, cols = _figure_image.calculate_layout(num_panels)
        # Assert
        assert rows * cols >= num_panels and cols == 4

    def test_zero_panels_fails_loud(self):
        # Arrange
        num_panels = 0
        # Act
        # Assert
        with pytest.raises(ValueError, match="must be positive"):
            _figure_image.calculate_layout(num_panels)


class TestPanelLetter:
    def test_panel_stem_reports_its_letter(self):
        # Arrange
        stem = "01a_overview"
        # Act
        letter = _figure_image.panel_letter(stem)
        # Assert
        assert letter == "a"

    def test_main_figure_stem_reports_none(self):
        # Arrange
        stem = "01_overview"
        # Act
        letter = _figure_image.panel_letter(stem)
        # Assert
        assert letter is None

    def test_unnumbered_stem_reports_none(self):
        # Arrange
        stem = "overview_a_thing"
        # Act
        letter = _figure_image.panel_letter(stem)
        # Assert
        assert letter is None


class TestTilePanels:
    def test_two_panels_tile_side_by_side(self, tmp_path):
        # Arrange: 1x2 grid of 40x30 panels + 20px gutter -> 100x30.
        panels = [
            _write_png(tmp_path / "01a_left.png"),
            _write_png(tmp_path / "01b_right.png", color=(30, 30, 200)),
        ]
        # Act
        dst = _figure_image.tile_panels(panels, tmp_path / "01.jpg")
        # Assert
        with Image.open(dst) as image:
            assert image.size == (100, 30)

    def test_composite_is_not_merely_the_first_panel(self, tmp_path):
        # Arrange: the shell's `cp <first panel> <composite>` bug -- a real tile
        # must be strictly wider than one panel.
        panels = [
            _write_png(tmp_path / "01a_left.png"),
            _write_png(tmp_path / "01b_right.png", color=(30, 30, 200)),
        ]
        with Image.open(panels[0]) as first:
            panel_width = first.width
        # Act
        dst = _figure_image.tile_panels(panels, tmp_path / "01.jpg")
        # Assert
        with Image.open(dst) as image:
            assert image.width > panel_width

    def test_mismatched_panel_is_resized_to_the_grid(self, tmp_path):
        # Arrange: panel B is a different size and must be normalized to A's.
        panels = [
            _write_png(tmp_path / "02a_left.png", size=(40, 30)),
            _write_png(tmp_path / "02b_right.png", size=(80, 90)),
        ]
        # Act
        dst = _figure_image.tile_panels(panels, tmp_path / "02.jpg")
        # Assert
        with Image.open(dst) as image:
            assert image.size == (100, 30)

    def test_empty_panel_list_fails_loud(self, tmp_path):
        # Arrange
        panels = []
        # Act
        # Assert
        with pytest.raises(ValueError, match="no panel images"):
            _figure_image.tile_panels(panels, tmp_path / "03.jpg")


if __name__ == "__main__":
    import sys

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
