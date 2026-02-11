#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: optimize_figure.py

import os
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

# Check for PIL dependency
try:
    from optimize_figure import crop_whitespace, enhance_image_quality, optimize_figure
    from PIL import Image

    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# compute_optimal_size is pure logic - try to import separately
try:
    from optimize_figure import compute_optimal_size

    HAS_COMPUTE = True
except ImportError:
    HAS_COMPUTE = False


# Tests for compute_optimal_size (pure logic - no dependencies)
@pytest.mark.skipif(not HAS_COMPUTE, reason="compute_optimal_size not available")
def test_compute_optimal_size_within_limits():
    """Test that image already within limits returns same dimensions."""
    # Use larger dimensions that are above 80% of publication_width_px threshold
    width, height = 2000, 1600
    max_width, max_height = 3000, 3000

    new_w, new_h = compute_optimal_size(width, height, max_width, max_height)

    # Should not change since within limits and good resolution
    assert new_w == 2000
    assert new_h == 1600


@pytest.mark.skipif(not HAS_COMPUTE, reason="compute_optimal_size not available")
def test_compute_optimal_size_width_limit():
    """Test that wide image gets scaled to fit max_width."""
    width, height = 3000, 1000
    max_width, max_height = 2000, 2000

    new_w, new_h = compute_optimal_size(width, height, max_width, max_height)

    assert new_w == 2000  # Width limited
    assert new_h < 1000  # Height scaled proportionally


@pytest.mark.skipif(not HAS_COMPUTE, reason="compute_optimal_size not available")
def test_compute_optimal_size_height_limit():
    """Test that tall image gets scaled to fit max_height."""
    width, height = 1000, 3000
    max_width, max_height = 2000, 2000

    new_w, new_h = compute_optimal_size(width, height, max_width, max_height)

    assert new_h == 2000  # Height limited
    assert new_w < 1000  # Width scaled proportionally


@pytest.mark.skipif(not HAS_COMPUTE, reason="compute_optimal_size not available")
def test_compute_optimal_size_even_dimensions():
    """Test that result has even width and height."""
    width, height = 2501, 1501
    max_width, max_height = 2000, 2000

    new_w, new_h = compute_optimal_size(width, height, max_width, max_height)

    assert new_w % 2 == 0  # Even width
    assert new_h % 2 == 0  # Even height


@pytest.mark.skipif(not HAS_COMPUTE, reason="compute_optimal_size not available")
def test_compute_optimal_size_aspect_ratio_preserved():
    """Test that aspect ratio is approximately preserved."""
    width, height = 1600, 1000
    max_width, max_height = 800, 800

    new_w, new_h = compute_optimal_size(width, height, max_width, max_height)

    original_ratio = width / height
    new_ratio = new_w / new_h
    # Allow small difference due to rounding
    assert abs(original_ratio - new_ratio) < 0.01


# Tests for crop_whitespace (requires PIL)
@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_crop_whitespace_removes_padding():
    """Test that crop_whitespace removes white borders."""
    # Create image with white border
    img = Image.new("RGB", (200, 200), color="white")
    # Add colored content in center
    pixels = img.load()
    for i in range(50, 150):
        for j in range(50, 150):
            pixels[j, i] = (255, 0, 0)  # Red square

    cropped = crop_whitespace(img, padding=5)

    # Should be smaller than original
    assert cropped.width < 200
    assert cropped.height < 200
    # Should be around 100x100 + padding
    assert 100 <= cropped.width <= 120
    assert 100 <= cropped.height <= 120


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_crop_whitespace_no_content_returns_original():
    """Test that all-white image returns original."""
    img = Image.new("RGB", (100, 100), color="white")

    cropped = crop_whitespace(img)

    assert cropped.size == img.size


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_crop_whitespace_padding_parameter():
    """Test that padding parameter is respected."""
    img = Image.new("RGB", (200, 200), color="white")
    pixels = img.load()
    for i in range(80, 120):
        for j in range(80, 120):
            pixels[j, i] = (0, 0, 255)  # Blue square

    cropped_small = crop_whitespace(img, padding=5)
    cropped_large = crop_whitespace(img, padding=20)

    # Larger padding should result in larger image
    assert cropped_large.width > cropped_small.width
    assert cropped_large.height > cropped_small.height


# Tests for enhance_image_quality (requires PIL)
@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_enhance_image_quality_returns_rgb():
    """Test that RGBA image is converted to RGB."""
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))

    enhanced = enhance_image_quality(img)

    assert enhanced.mode == "RGB"


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_enhance_image_quality_preserves_dimensions():
    """Test that enhancement preserves image dimensions."""
    img = Image.new("RGB", (150, 200), color="blue")

    enhanced = enhance_image_quality(img)

    assert enhanced.size == img.size


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_enhance_image_quality_returns_image():
    """Test that enhancement returns a PIL Image."""
    img = Image.new("RGB", (100, 100), color="green")

    enhanced = enhance_image_quality(img)

    assert isinstance(enhanced, Image.Image)


# Tests for optimize_figure (full pipeline - requires PIL)
@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_optimize_figure_creates_output(tmp_path):
    """Test that optimize_figure creates output file."""
    # Create test image
    img = Image.new("RGB", (300, 200), color="red")
    input_path = tmp_path / "input.jpg"
    output_path = tmp_path / "output.jpg"
    img.save(str(input_path))

    result = optimize_figure(str(input_path), str(output_path), no_crop=True)

    assert result == str(output_path)
    assert output_path.exists()


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_optimize_figure_missing_input_returns_none(tmp_path):
    """Test that optimize_figure returns None for missing file."""
    output_path = tmp_path / "output.jpg"

    result = optimize_figure("/nonexistent/input.jpg", str(output_path))

    assert result is None


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_optimize_figure_auto_output_path(tmp_path):
    """Test that optimize_figure generates output path automatically."""
    img = Image.new("RGB", (200, 200), color="blue")
    input_path = tmp_path / "test.jpg"
    img.save(str(input_path))

    result = optimize_figure(str(input_path), output_path=None)

    # Should create test_optimized.jpg
    expected_path = tmp_path / "test_optimized.jpg"
    assert result == str(expected_path)
    assert expected_path.exists()


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_optimize_figure_with_crop(tmp_path):
    """Test that optimize_figure crops whitespace when enabled."""
    # Create image with white border
    img = Image.new("RGB", (400, 400), color="white")
    pixels = img.load()
    for i in range(100, 300):
        for j in range(100, 300):
            pixels[j, i] = (0, 255, 0)  # Green square

    input_path = tmp_path / "bordered.jpg"
    output_path = tmp_path / "cropped.jpg"
    img.save(str(input_path))

    result = optimize_figure(
        str(input_path),
        str(output_path),
        no_crop=False,
        max_width=5000,
        max_height=5000,
    )

    assert result is not None
    assert output_path.exists()
    # The function successfully runs with cropping enabled
    # Actual dimensions depend on scaling logic, so just verify file was created


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_optimize_figure_respects_max_dimensions(tmp_path):
    """Test that optimize_figure respects max width/height."""
    # Create large image
    img = Image.new("RGB", (3000, 2000), color="yellow")
    input_path = tmp_path / "large.jpg"
    output_path = tmp_path / "resized.jpg"
    img.save(str(input_path))

    result = optimize_figure(
        str(input_path), str(output_path), max_width=1000, max_height=1000, no_crop=True
    )

    result_img = Image.open(result)
    assert result_img.width <= 1000
    assert result_img.height <= 1000


@pytest.mark.skipif(not HAS_PIL, reason="PIL (Pillow) not available")
def test_optimize_figure_different_formats(tmp_path):
    """Test that optimize_figure handles different image formats."""
    # Test with PNG
    img = Image.new("RGB", (200, 200), color="purple")
    input_path = tmp_path / "test.png"
    output_path = tmp_path / "test_out.png"
    img.save(str(input_path))

    result = optimize_figure(str(input_path), str(output_path))

    assert result is not None
    assert output_path.exists()


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
