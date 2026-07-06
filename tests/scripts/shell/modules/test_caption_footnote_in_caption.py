"""compile_figure_tex_files renders a \\captionfootnote{...} as footnote-in-caption."""

import subprocess
from pathlib import Path

_MODULES = (
    Path(__file__).resolve().parents[4]
    / "scripts/shell/modules/process_figures_modules"
)

_WITH_FOOTNOTE = "\\caption{\\textbf{T}\\\\ desc.\\captionfootnote{Note me.}}"
_PLAIN = "\\caption{\\textbf{T}\\\\ plain desc.}"


def _run_assembler(tmp_path, caption_body):
    compiled = tmp_path / "compiled"
    cam = tmp_path / "cam"
    jpg = cam / "jpg_for_compilation"
    for d in (compiled, cam, jpg):
        d.mkdir(parents=True)
    (compiled / "01_Test.tex").write_text("% fig\n")
    (cam / "01_Test.tex").write_text(caption_body + "\n")
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
    return (compiled / "_placeable" / "01.tex").read_text()


def test_declared_footnote_becomes_footnotemark_in_caption(tmp_path):
    # Arrange
    caption = _WITH_FOOTNOTE
    # Act
    placeable = _run_assembler(tmp_path, caption)
    # Assert
    assert "\\footnotemark" in placeable


def test_declared_footnote_emits_footnotetext_after_float_close(tmp_path):
    # Arrange
    caption = _WITH_FOOTNOTE
    # Act
    placeable = _run_assembler(tmp_path, caption)
    # Assert
    assert "\\footnotetext{Note me.}" in placeable.split("\\end{figure*}", 1)[1]


def test_no_declared_footnote_leaves_placeable_without_footnotetext(tmp_path):
    # Arrange
    caption = _PLAIN
    # Act
    placeable = _run_assembler(tmp_path, caption)
    # Assert
    assert "\\footnotetext" not in placeable
