"""compile_figure_tex_files emits per-figure placeable files + a guarded end block."""

import subprocess
from pathlib import Path

_MODULES = (
    Path(__file__).resolve().parents[4]
    / "scripts/shell/modules/process_figures_modules"
)


def _run_assembler(tmp_path):
    compiled = tmp_path / "compiled"
    cam = tmp_path / "cam"
    jpg = cam / "jpg_for_compilation"
    for d in (compiled, cam, jpg):
        d.mkdir(parents=True)
    (compiled / "01_Test.tex").write_text("% fig\n")
    (cam / "01_Test.tex").write_text("\\caption{\\textbf{T}\\\\desc}\n")
    (jpg / "01_Test.jpg").write_bytes(b"\xff\xd8\xff\xe0")
    script = (
        f'export SCITEX_WRITER_FIGURE_COMPILED_DIR="{compiled}";'
        f'export SCITEX_WRITER_FIGURE_COMPILED_FILE="{compiled}/FINAL.tex";'
        f'export SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR="{cam}";'
        f'export SCITEX_WRITER_FIGURE_JPG_DIR="{jpg}";'
        f"source '{_MODULES}/00_common.src';"
        f"source '{_MODULES}/04_compilation.src';"
        f"compile_figure_tex_files"
    )
    subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True)
    return compiled


def test_placeable_file_written(tmp_path):
    # Arrange
    compiled = _run_assembler(tmp_path)
    # Act
    placeable = compiled / "_placeable" / "01.tex"
    # Assert
    assert placeable.is_file() and "\\begin{figure*}" in placeable.read_text()


def test_final_block_is_guarded(tmp_path):
    # Arrange
    compiled = _run_assembler(tmp_path)
    # Act
    final = (compiled / "FINAL.tex").read_text()
    # Assert
    assert "\\ifcsname scitexfigplaced@01\\endcsname\\else" in final


def test_final_still_contains_figure_when_unplaced(tmp_path):
    # Arrange
    compiled = _run_assembler(tmp_path)
    # Act
    final = (compiled / "FINAL.tex").read_text()
    # Assert
    assert "\\begin{figure*}" in final
