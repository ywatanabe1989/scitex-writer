#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: png_to_jpg.py (Pillow PNG->JPG fallback)

import subprocess
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
_SCRIPT = ROOT_DIR / "scripts" / "python" / "png_to_jpg.py"


def _make_png(path, color=(255, 0, 0, 128), size=(40, 30)):
    from PIL import Image

    Image.new("RGBA", size, color).save(path)


def _run(*args):
    return subprocess.run(
        [sys.executable, str(_SCRIPT), *args],
        capture_output=True,
        text=True,
    )


def test_convert_produces_jpeg(tmp_path):
    """--src converts a PNG into a real JPEG file."""
    # Arrange
    pytest.importorskip("PIL")
    from PIL import Image

    src = tmp_path / "in.png"
    _make_png(src)
    dst = tmp_path / "out.jpg"
    # Act
    _run(str(dst), "--src", str(src))
    # Assert
    assert Image.open(dst).format == "JPEG"


def test_convert_flattens_alpha_onto_white(tmp_path):
    """A fully transparent PNG flattens onto a white background."""
    # Arrange
    pytest.importorskip("PIL")
    from PIL import Image

    src = tmp_path / "clear.png"
    _make_png(src, color=(0, 0, 0, 0))
    dst = tmp_path / "clear.jpg"
    # Act
    _run(str(dst), "--src", str(src))
    # Assert
    assert Image.open(dst).convert("RGB").getpixel((0, 0)) == (255, 255, 255)


def test_placeholder_produces_jpeg(tmp_path):
    """--placeholder writes a JPEG placeholder (never a .txt)."""
    # Arrange
    pytest.importorskip("PIL")
    from PIL import Image

    dst = tmp_path / "ph.jpg"
    # Act
    _run(str(dst), "--placeholder", "Missing figure: 02")
    # Assert
    assert Image.open(dst).format == "JPEG"


def test_requires_src_or_placeholder(tmp_path):
    """With neither --src nor --placeholder, the CLI errors (no silent no-op)."""
    # Arrange
    dst = tmp_path / "out.jpg"
    # Act
    proc = _run(str(dst))
    # Assert
    assert proc.returncode != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# EOF
