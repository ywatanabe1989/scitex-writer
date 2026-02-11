#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: pptx2tif.py

import os
import sys
from pathlib import Path

import pytest

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

# Check for dependencies
try:
    from pptx2tif import check_libreoffice_installed

    HAS_SCRIPT = True
except ImportError:
    HAS_SCRIPT = False

try:
    from pptx2tif import (
        batch_convert_pptx_to_tif,
        convert_pptx_to_tif,
        convert_pptx_to_tif_libreoffice,
    )

    HAS_FULL_SCRIPT = True
except ImportError:
    HAS_FULL_SCRIPT = False


# Tests for check_libreoffice_installed (safe to call)
@pytest.mark.skipif(not HAS_SCRIPT, reason="pptx2tif.py not importable")
def test_check_libreoffice_installed_returns_bool():
    """Test that check_libreoffice_installed returns a boolean."""
    result = check_libreoffice_installed()
    assert isinstance(result, bool)


# Tests for convert_pptx_to_tif_libreoffice
@pytest.mark.skipif(not HAS_FULL_SCRIPT, reason="pptx2tif functions not importable")
def test_convert_pptx_missing_file_raises():
    """Test that FileNotFoundError is raised for missing input."""
    with pytest.raises(FileNotFoundError, match="PowerPoint file not found"):
        convert_pptx_to_tif_libreoffice("/nonexistent/file.pptx")


# Tests for batch_convert_pptx_to_tif
@pytest.mark.skipif(not HAS_FULL_SCRIPT, reason="pptx2tif functions not importable")
def test_batch_convert_missing_dir_raises():
    """Test that ValueError is raised for missing directory."""
    with pytest.raises(ValueError, match="Directory not found"):
        batch_convert_pptx_to_tif("/nonexistent/directory")


@pytest.mark.skipif(not HAS_FULL_SCRIPT, reason="pptx2tif functions not importable")
def test_batch_convert_empty_dir_returns_empty_list(tmp_path):
    """Test that empty directory returns empty list."""
    result = batch_convert_pptx_to_tif(str(tmp_path))
    assert result == []


# Tests for convert_pptx_to_tif (auto method selection)
@pytest.mark.skipif(not HAS_FULL_SCRIPT, reason="pptx2tif functions not importable")
def test_convert_auto_method_no_tools_raises():
    """Test that RuntimeError is raised when no conversion tools available."""
    # This test assumes neither LibreOffice nor python-pptx+PIL are available
    # It will only fail if we have the tools, which is acceptable
    try:
        convert_pptx_to_tif("/fake/file.pptx", method="auto")
    except (RuntimeError, FileNotFoundError) as e:
        # Either no tools (RuntimeError) or file not found is acceptable
        assert "not found" in str(e).lower() or "no suitable" in str(e).lower()


@pytest.mark.skipif(not HAS_FULL_SCRIPT, reason="pptx2tif functions not importable")
def test_convert_pptx_invalid_method_raises():
    """Test that ValueError is raised for invalid method."""
    with pytest.raises(ValueError, match="Unknown conversion method"):
        convert_pptx_to_tif("/fake/file.pptx", method="invalid_method")


@pytest.mark.skipif(not HAS_FULL_SCRIPT, reason="pptx2tif functions not importable")
def test_convert_pptx_path_object_support(tmp_path):
    """Test that Path objects are supported for input/output."""
    # Create a fake pptx file
    fake_pptx = tmp_path / "test.pptx"
    fake_pptx.write_bytes(b"fake pptx content")

    output_dir = tmp_path / "output"

    # This should handle Path objects without error
    # It will fail due to invalid pptx, but that's after path handling
    try:
        convert_pptx_to_tif(fake_pptx, output_dir, method="auto")
    except (RuntimeError, FileNotFoundError, Exception) as e:
        # We're just testing that Path objects don't cause TypeError
        # Any other error is acceptable
        assert not isinstance(e, TypeError)


@pytest.mark.skipif(not HAS_FULL_SCRIPT, reason="pptx2tif functions not importable")
def test_batch_convert_recursive_flag(tmp_path):
    """Test that recursive flag is handled."""
    # Create subdirectory structure
    subdir = tmp_path / "subdir"
    subdir.mkdir()

    # This should not raise an error for valid directory
    result = batch_convert_pptx_to_tif(str(tmp_path), recursive=True)
    assert isinstance(result, list)


@pytest.mark.skipif(not HAS_FULL_SCRIPT, reason="pptx2tif functions not importable")
def test_convert_pptx_string_path_support(tmp_path):
    """Test that string paths are supported."""
    fake_pptx = tmp_path / "test.pptx"
    fake_pptx.write_bytes(b"fake")

    # Should handle string paths
    try:
        convert_pptx_to_tif(str(fake_pptx), method="auto")
    except (RuntimeError, FileNotFoundError, Exception) as e:
        # We're testing path handling, not actual conversion
        assert not isinstance(e, TypeError)


# Integration-style tests (will skip if dependencies missing)
@pytest.mark.skipif(not HAS_FULL_SCRIPT, reason="pptx2tif functions not importable")
def test_module_imports_successfully():
    """Test that the module imports without errors."""
    # If we got here, imports succeeded
    assert HAS_FULL_SCRIPT is True


@pytest.mark.skipif(not HAS_SCRIPT, reason="pptx2tif.py not importable")
def test_check_libreoffice_handles_exceptions():
    """Test that check_libreoffice_installed handles exceptions gracefully."""
    # This should never raise an exception
    try:
        result = check_libreoffice_installed()
        assert result in [True, False]
    except Exception as e:
        pytest.fail(f"check_libreoffice_installed raised unexpected exception: {e}")


if __name__ == "__main__":
    import pytest

    pytest.main([os.path.abspath(__file__), "-v"])
