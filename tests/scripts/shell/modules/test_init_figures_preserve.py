"""init_figures must preserve real user-placed jpgs and only clear derived symlinks."""

import os
import subprocess
from pathlib import Path

_COMMON_SRC = (
    Path(__file__).resolve().parents[4]
    / "scripts/shell/modules/process_figures_modules/00_common.src"
)


def _run_init_figures(caption_dir, jpg_dir, compiled_dir):
    env = dict(os.environ)
    env["SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR"] = str(caption_dir)
    env["SCITEX_WRITER_FIGURE_JPG_DIR"] = str(jpg_dir)
    env["SCITEX_WRITER_FIGURE_COMPILED_DIR"] = str(compiled_dir)
    return subprocess.run(
        ["bash", "-c", f"source '{_COMMON_SRC}'; init_figures"],
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )


def test_preserves_user_jpg_without_source(tmp_path):
    # Arrange
    caption_dir = tmp_path / "caption_and_media"
    jpg_dir = caption_dir / "jpg_for_compilation"
    compiled_dir = tmp_path / "compiled"
    jpg_dir.mkdir(parents=True)
    caption_dir.mkdir(exist_ok=True)
    compiled_dir.mkdir()
    user_jpg = jpg_dir / "01.jpg"
    user_jpg.write_bytes(b"\xff\xd8\xff\xe0real-image-bytes")
    # Act
    _run_init_figures(caption_dir, jpg_dir, compiled_dir)
    # Assert
    assert user_jpg.is_file()


def test_removes_derived_symlink(tmp_path):
    # Arrange
    caption_dir = tmp_path / "caption_and_media"
    jpg_dir = caption_dir / "jpg_for_compilation"
    compiled_dir = tmp_path / "compiled"
    jpg_dir.mkdir(parents=True)
    compiled_dir.mkdir()
    source_jpg = caption_dir / "02.jpg"
    source_jpg.write_bytes(b"\xff\xd8\xff\xe0source")
    link = jpg_dir / "02.jpg"
    link.symlink_to(source_jpg)
    # Act
    _run_init_figures(caption_dir, jpg_dir, compiled_dir)
    # Assert
    assert not os.path.lexists(link)


def test_warns_on_preserved_orphan(tmp_path):
    # Arrange
    caption_dir = tmp_path / "caption_and_media"
    jpg_dir = caption_dir / "jpg_for_compilation"
    compiled_dir = tmp_path / "compiled"
    jpg_dir.mkdir(parents=True)
    compiled_dir.mkdir()
    (jpg_dir / "03.jpg").write_bytes(b"\xff\xd8\xff\xe0orphan")
    # Act
    result = _run_init_figures(caption_dir, jpg_dir, compiled_dir)
    # Assert
    assert "Preserving user-placed 03.jpg" in result.stdout + result.stderr
