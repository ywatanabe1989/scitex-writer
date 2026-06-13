#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: crop_tif.py
# Wave 2 cluster A batch 1 — NM+TQ003+TQ002+TQ007 cleanup.

import os
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

try:
    import cv2
    import numpy as np
    from crop_tif import crop_tif, find_content_area, resize_image

    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


pytestmark = pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")


# ============================================================================
# find_content_area
# ============================================================================


def test_find_content_area_returns_four_tuple_for_valid_image(tmp_path):
    """find_content_area returns a 4-tuple (x, y, w, h) for a content image."""
    # Arrange
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255
    img[20:80, 20:80] = 0
    test_image = tmp_path / "test.tif"
    cv2.imwrite(str(test_image), img)
    # Act
    result = find_content_area(str(test_image))
    # Assert
    assert len(result) == 4


def test_find_content_area_all_white_returns_full_width(tmp_path):
    """For an all-white image the returned width equals the image width."""
    # Arrange
    img = np.ones((100, 150, 3), dtype=np.uint8) * 255
    test_image = tmp_path / "white.tif"
    cv2.imwrite(str(test_image), img)
    # Act
    _, _, w, _ = find_content_area(str(test_image))
    # Assert
    assert w == 150


def test_find_content_area_all_white_returns_full_height(tmp_path):
    """For an all-white image the returned height equals the image height."""
    # Arrange
    img = np.ones((100, 150, 3), dtype=np.uint8) * 255
    test_image = tmp_path / "white.tif"
    cv2.imwrite(str(test_image), img)
    # Act
    _, _, _, h = find_content_area(str(test_image))
    # Assert
    assert h == 100


def test_find_content_area_missing_file_raises_filenotfound():
    """find_content_area raises FileNotFoundError for a missing path."""
    # Arrange
    missing = "/nonexistent/path/image.tif"
    # Act / Assert
    with pytest.raises(FileNotFoundError):
        find_content_area(missing)


# ============================================================================
# resize_image
# ============================================================================


def test_resize_image_within_limits_preserves_height():
    """A small image (100x200) within 2000x2000 limits keeps its height of 100."""
    # Arrange
    img = np.ones((100, 200, 3), dtype=np.uint8) * 255
    # Act
    result = resize_image(img, max_width=2000, max_height=2000)
    # Assert
    assert result.shape[0] == 100


def test_resize_image_within_limits_preserves_width():
    """A small image (100x200) within 2000x2000 limits keeps its width of 200."""
    # Arrange
    img = np.ones((100, 200, 3), dtype=np.uint8) * 255
    # Act
    result = resize_image(img, max_width=2000, max_height=2000)
    # Assert
    assert result.shape[1] == 200


def test_resize_image_wide_image_is_downscaled_to_max_width():
    """A wide image (100x3000) is downscaled to width 2000 when max_width=2000."""
    # Arrange
    img = np.ones((100, 3000, 3), dtype=np.uint8) * 255
    # Act
    result = resize_image(img, max_width=2000, max_height=2000)
    # Assert
    assert result.shape[1] == 2000


def test_resize_image_tall_image_is_downscaled_to_max_height():
    """A tall image (3000x100) is downscaled to height 2000 when max_height=2000."""
    # Arrange
    img = np.ones((3000, 100, 3), dtype=np.uint8) * 255
    # Act
    result = resize_image(img, max_width=2000, max_height=2000)
    # Assert
    assert result.shape[0] == 2000


# ============================================================================
# crop_tif
# ============================================================================


def test_crop_tif_default_writes_output_file(tmp_path):
    """crop_tif writes the output .tif at the supplied path."""
    # Arrange
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    img[50:150, 50:150] = 0
    input_file = tmp_path / "input.tif"
    output_file = tmp_path / "output.tif"
    cv2.imwrite(str(input_file), img)
    # Act
    crop_tif(str(input_file), str(output_file), resize=False)
    # Assert
    assert output_file.exists()


def test_crop_tif_output_is_readable_as_image(tmp_path):
    """The output file produced by crop_tif is readable via cv2.imread."""
    # Arrange
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    img[50:150, 50:150] = 0
    input_file = tmp_path / "input.tif"
    output_file = tmp_path / "output.tif"
    cv2.imwrite(str(input_file), img)
    crop_tif(str(input_file), str(output_file), resize=False)
    # Act
    result_img = cv2.imread(str(output_file))
    # Assert
    assert result_img is not None


def test_crop_tif_missing_input_raises_filenotfound():
    """crop_tif raises FileNotFoundError when the input path does not exist."""
    # Arrange
    missing = "/nonexistent/input.tif"
    # Act / Assert
    with pytest.raises(FileNotFoundError):
        crop_tif(missing, "/tmp/output.tif")


def test_crop_tif_no_output_no_overwrite_raises_valueerror():
    """crop_tif raises ValueError when neither output_path nor overwrite is given."""
    # Arrange
    # (no setup needed)
    # Act / Assert
    with pytest.raises(ValueError, match="output_path must be specified"):
        crop_tif("input.tif", output_path=None, overwrite=False)


def test_crop_tif_overwrite_in_place_keeps_input_path(tmp_path):
    """crop_tif with overwrite=True leaves the original input path in place."""
    # Arrange
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    img[50:150, 50:150] = 0
    input_file = tmp_path / "test.tif"
    cv2.imwrite(str(input_file), img)
    # Act
    crop_tif(str(input_file), output_path=None, overwrite=True, resize=False)
    # Assert
    assert input_file.exists()


def test_crop_tif_with_resize_caps_width_at_max(tmp_path):
    """crop_tif with resize=True downscales width to at most max_width."""
    # Arrange
    img = np.ones((3000, 3000, 3), dtype=np.uint8) * 255
    img[100:2900, 100:2900] = 0
    input_file = tmp_path / "large.tif"
    output_file = tmp_path / "resized.tif"
    cv2.imwrite(str(input_file), img)
    # Act
    crop_tif(
        str(input_file),
        str(output_file),
        resize=True,
        max_width=1000,
        max_height=1000,
    )
    result_img = cv2.imread(str(output_file))
    # Assert
    assert result_img.shape[1] <= 1000


def test_crop_tif_with_resize_caps_height_at_max(tmp_path):
    """crop_tif with resize=True downscales height to at most max_height."""
    # Arrange
    img = np.ones((3000, 3000, 3), dtype=np.uint8) * 255
    img[100:2900, 100:2900] = 0
    input_file = tmp_path / "large.tif"
    output_file = tmp_path / "resized.tif"
    cv2.imwrite(str(input_file), img)
    # Act
    crop_tif(
        str(input_file),
        str(output_file),
        resize=True,
        max_width=1000,
        max_height=1000,
    )
    result_img = cv2.imread(str(output_file))
    # Assert
    assert result_img.shape[0] <= 1000


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__), "-v"])
