#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: tile_panels.py

import os
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

# calculate_layout is pure logic - no dependencies needed
from tile_panels import calculate_layout, detect_panels

# Check for PIL dependency
try:
    from PIL import Image
    from tile_panels import tile_images

    HAS_PIL = True
except ImportError:
    HAS_PIL = False


# Tests for calculate_layout (pure logic - always testable)
def test_calculate_layout_1_panel():
    """Test layout for 1 panel."""
    assert calculate_layout(1) == (1, 1)


def test_calculate_layout_2_panels():
    """Test layout for 2 panels."""
    assert calculate_layout(2) == (1, 2)


def test_calculate_layout_3_panels():
    """Test layout for 3 panels."""
    assert calculate_layout(3) == (1, 3)


def test_calculate_layout_4_panels():
    """Test layout for 4 panels."""
    assert calculate_layout(4) == (2, 2)


def test_calculate_layout_5_panels():
    """Test layout for 5 panels."""
    assert calculate_layout(5) == (2, 3)


def test_calculate_layout_6_panels():
    """Test layout for 6 panels."""
    assert calculate_layout(6) == (2, 3)


def test_calculate_layout_7_panels():
    """Test layout for 7 panels."""
    assert calculate_layout(7) == (3, 3)


def test_calculate_layout_9_panels():
    """Test layout for 9 panels."""
    assert calculate_layout(9) == (3, 3)


def test_calculate_layout_10_panels():
    """Test layout for 10 panels."""
    rows, cols = calculate_layout(10)
    assert rows * cols >= 10
    assert isinstance(rows, int)
    assert isinstance(cols, int)


# Tests for detect_panels (file system only)
def test_detect_panels_finds_files(tmp_path):
    """Test that detect_panels finds panel files."""
    # Create test panel files following naming convention
    (tmp_path / "01a_figure.jpg").touch()
    (tmp_path / "01b_figure.jpg").touch()
    (tmp_path / "01c_figure.jpg").touch()

    panels = detect_panels("01_demographic_data", str(tmp_path))

    assert len(panels) == 3
    assert "A" in panels
    assert "B" in panels
    assert "C" in panels


def test_detect_panels_empty_dir(tmp_path):
    """Test that empty directory returns empty dict."""
    panels = detect_panels("01_figure", str(tmp_path))
    assert panels == {}


def test_detect_panels_wrong_prefix(tmp_path):
    """Test that panels with wrong prefix are not detected."""
    (tmp_path / "02a_figure.jpg").touch()
    (tmp_path / "02b_figure.jpg").touch()

    panels = detect_panels("01_figure", str(tmp_path))
    assert panels == {}


def test_detect_panels_sorted_order(tmp_path):
    """Test that panels are returned in sorted order."""
    (tmp_path / "01c_figure.jpg").touch()
    (tmp_path / "01a_figure.jpg").touch()
    (tmp_path / "01b_figure.jpg").touch()

    panels = detect_panels("01_figure", str(tmp_path))

    keys = list(panels.keys())
    assert keys == ["A", "B", "C"]


def test_detect_panels_mixed_case(tmp_path):
    """Test that lowercase panel letters are uppercase in output."""
    (tmp_path / "01a_figure.jpg").touch()

    panels = detect_panels("01_figure", str(tmp_path))

    assert "A" in panels
    assert "a" not in panels


# Tests for tile_images (requires PIL)
@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_tile_images_empty_panels():
    """Test that tile_images returns False for empty panels."""
    result = tile_images({}, "output.jpg")
    assert result is False


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_tile_images_creates_output(tmp_path):
    """Test that tile_images creates output file."""
    # Create small test images
    img_a = Image.new("RGB", (100, 100), color="red")
    img_b = Image.new("RGB", (100, 100), color="blue")

    img_a_path = tmp_path / "01a_test.jpg"
    img_b_path = tmp_path / "01b_test.jpg"
    img_a.save(str(img_a_path))
    img_b.save(str(img_b_path))

    panels = {"A": str(img_a_path), "B": str(img_b_path)}
    output_path = tmp_path / "tiled.jpg"

    result = tile_images(panels, str(output_path), spacing=10, dpi=100)

    assert result is True
    assert output_path.exists()


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_tile_images_correct_dimensions(tmp_path):
    """Test that tiled image has correct dimensions."""
    # Create test images
    img_a = Image.new("RGB", (200, 150), color="red")
    img_b = Image.new("RGB", (200, 150), color="blue")

    img_a_path = tmp_path / "01a_test.jpg"
    img_b_path = tmp_path / "01b_test.jpg"
    img_a.save(str(img_a_path))
    img_b.save(str(img_b_path))

    panels = {"A": str(img_a_path), "B": str(img_b_path)}
    output_path = tmp_path / "tiled.jpg"

    spacing = 20
    tile_images(panels, str(output_path), spacing=spacing)

    # Open result and check dimensions
    result_img = Image.open(str(output_path))
    # 2 panels in 1 row, 2 cols layout
    expected_width = 2 * 200 + (2 - 1) * spacing
    assert result_img.width == expected_width


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_tile_images_invalid_path_returns_false(tmp_path):
    """Test that tile_images returns False for invalid image path."""
    panels = {"A": "/nonexistent/image.jpg"}
    output_path = tmp_path / "output.jpg"

    result = tile_images(panels, str(output_path))

    assert result is False


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_tile_images_4_panels_layout(tmp_path):
    """Test that 4 panels use 2x2 layout."""
    # Create 4 test images
    panels = {}
    for letter in ["A", "B", "C", "D"]:
        img = Image.new("RGB", (100, 100), color="white")
        img_path = tmp_path / f"01{letter.lower()}_test.jpg"
        img.save(str(img_path))
        panels[letter] = str(img_path)

    output_path = tmp_path / "tiled.jpg"
    tile_images(panels, str(output_path), spacing=0)

    result_img = Image.open(str(output_path))
    # 2x2 layout
    assert result_img.width == 200  # 2 * 100
    assert result_img.height == 200  # 2 * 100


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
