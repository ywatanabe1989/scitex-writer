#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: crop_tif.py

import os
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

pytest.importorskip("cv2")
pytest.importorskip("numpy")

# Check for dependencies
try:
    import cv2
    import numpy as np
    from crop_tif import crop_tif, find_content_area, resize_image

    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False


# Tests for find_content_area
@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_find_content_area_returns_tuple_result_is_tuple_and_len_result(tmp_path):
    # Arrange
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White background
    img[20:80, 20:80] = 0  # Black square in center
    test_image = tmp_path / "test.tif"
    cv2.imwrite(str(test_image), img)
    # Act
    result = find_content_area(str(test_image))
    # Act
    # Assert
    assert (isinstance(result, tuple)) and (len(result) == 4)


@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_find_content_area_returns_tuple_all_isinstance_v_int_np_integer_for_v_in_result(tmp_path):
    # Arrange
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White background
    img[20:80, 20:80] = 0  # Black square in center
    test_image = tmp_path / "test.tif"
    cv2.imwrite(str(test_image), img)
    result = find_content_area(str(test_image))
    # Act
    x, y, w, h = result
    # Act
    # Assert
    assert all(isinstance(v, (int, np.integer)) for v in result)




@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_find_content_area_all_white(tmp_path):
    """Test that all-white image returns full dimensions."""
    # Create all-white image
    # Arrange
    img = np.ones((100, 150, 3), dtype=np.uint8) * 255

    test_image = tmp_path / "white.tif"
    cv2.imwrite(str(test_image), img)

    # Act
    x, y, w, h = find_content_area(str(test_image))
    # Should return full image dimensions
    # Assert
    assert (w == 150) and (h == 100)


@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_find_content_area_missing_file():
    """Test that FileNotFoundError is raised for missing file."""
    # Arrange
    # Act
    # Assert
    with pytest.raises(FileNotFoundError):
        find_content_area("/nonexistent/path/image.tif")


# Tests for resize_image
@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_resize_image_no_change():
    """Test that small image within limits stays same size."""
    # Arrange
    img = np.ones((100, 200, 3), dtype=np.uint8) * 255

    # Act
    result = resize_image(img, max_width=2000, max_height=2000)

    # Assert
    assert (result.shape[0] == 100) and (result.shape[1] == 200)


@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_resize_image_downscale_width():
    """Test that wide image gets scaled down to fit max_width."""
    # Arrange
    img = np.ones((100, 3000, 3), dtype=np.uint8) * 255

    # Act
    result = resize_image(img, max_width=2000, max_height=2000)

    # Assert
    assert (result.shape[1] == 2000) and (result.shape[0] < 100)


@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_resize_image_downscale_height():
    """Test that tall image gets scaled down to fit max_height."""
    # Arrange
    img = np.ones((3000, 100, 3), dtype=np.uint8) * 255

    # Act
    result = resize_image(img, max_width=2000, max_height=2000)

    # Assert
    assert (result.shape[0] == 2000) and (result.shape[1] < 100)


# Tests for crop_tif
@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_crop_tif_output_created_output_file_exists(tmp_path, capsys):
    # Arrange
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    img[50:150, 50:150] = 0  # Black square
    input_file = tmp_path / "input.tif"
    output_file = tmp_path / "output.tif"
    cv2.imwrite(str(input_file), img)
    # Act
    crop_tif(str(input_file), str(output_file), resize=False)
    # Act
    # Assert
    assert output_file.exists()


@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_crop_tif_output_created_result_img_is_not_none(tmp_path, capsys):
    # Arrange
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    img[50:150, 50:150] = 0  # Black square
    input_file = tmp_path / "input.tif"
    output_file = tmp_path / "output.tif"
    cv2.imwrite(str(input_file), img)
    crop_tif(str(input_file), str(output_file), resize=False)
    # Verify it's a valid image
    # Act
    result_img = cv2.imread(str(output_file))
    # Act
    # Assert
    assert result_img is not None




@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_crop_tif_missing_file_raises():
    """Test that FileNotFoundError is raised for missing input."""
    # Arrange
    # Act
    # Assert
    with pytest.raises(FileNotFoundError):
        crop_tif("/nonexistent/input.tif", "/tmp/output.tif")


@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_crop_tif_no_output_no_overwrite_raises():
    """Test that ValueError is raised when no output and no overwrite."""
    # Arrange
    # Act
    # Assert
    with pytest.raises(ValueError, match="output_path must be specified"):
        crop_tif("input.tif", output_path=None, overwrite=False)


@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_crop_tif_with_overwrite_input_file_exists(tmp_path, capsys):
    # Arrange
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    img[50:150, 50:150] = 0
    input_file = tmp_path / "test.tif"
    cv2.imwrite(str(input_file), img)
    # Act
    crop_tif(str(input_file), output_path=None, overwrite=True, resize=False)
    # Act
    # Assert
    assert input_file.exists()


@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_crop_tif_with_overwrite_result_img_is_not_none(tmp_path, capsys):
    # Arrange
    img = np.ones((200, 200, 3), dtype=np.uint8) * 255
    img[50:150, 50:150] = 0
    input_file = tmp_path / "test.tif"
    cv2.imwrite(str(input_file), img)
    crop_tif(str(input_file), output_path=None, overwrite=True, resize=False)
    # File should still exist
    # Act
    result_img = cv2.imread(str(input_file))
    # Act
    # Assert
    assert result_img is not None




@pytest.mark.skipif(not HAS_CV2, reason="cv2 (opencv-python) not available")
def test_crop_tif_with_resize(tmp_path, capsys):
    """Test that crop_tif resizes when requested."""
    # Create large test image
    # Arrange
    img = np.ones((3000, 3000, 3), dtype=np.uint8) * 255
    img[100:2900, 100:2900] = 0

    input_file = tmp_path / "large.tif"
    output_file = tmp_path / "resized.tif"
    cv2.imwrite(str(input_file), img)

    crop_tif(
        str(input_file), str(output_file), resize=True, max_width=1000, max_height=1000
    )

    # Act
    result_img = cv2.imread(str(output_file))
    # Assert
    assert (result_img.shape[0] <= 1000) and (result_img.shape[1] <= 1000)


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
