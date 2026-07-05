"""gather_table_tex_files emits no stray placeholder "Table" when no tables exist.

Regression guard for card writer-stray-table-zero-artifact: the no-tables
fallback header must NOT be a renderable \\begin{table} float with a
\\label{tab:0_Tables_Header}, otherwise an empty-tables manuscript (or a stale
FINAL.tex leaked from a prior no-tables run) surfaces a stray "Table 0" in the
compiled PDF. The fallback is comment-only, mirroring the figures side.
"""

import subprocess
from pathlib import Path

_MODULES = (
    Path(__file__).resolve().parents[4] / "scripts/shell/modules/process_tables_modules"
)


def _run_gather(tmp_path, real_table=False):
    compiled = tmp_path / "compiled"
    cam = tmp_path / "cam"
    for d in (compiled, cam):
        d.mkdir(parents=True)
    if real_table:
        (compiled / "01_real.tex").write_text(
            "\\begin{table}[htbp]\\caption{Real}\\label{tab:01_real}\\end{table}\n"
        )
    script = (
        "echo_info(){ :; }; echo_warning(){ :; }; echo_success(){ :; };"
        f'export SCITEX_WRITER_TABLE_COMPILED_DIR="{compiled}";'
        f'export SCITEX_WRITER_TABLE_COMPILED_FILE="{compiled}/FINAL.tex";'
        f'export SCITEX_WRITER_TABLE_CAPTION_MEDIA_DIR="{cam}";'
        f"source '{_MODULES}/04_gather.src';"
        f"gather_table_tex_files"
    )
    subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True)
    return compiled


def _active_latex(path):
    """Non-comment LaTeX from ``path`` (drop full-line ``%`` comments), i.e. the
    text that actually renders. A ``\\label`` mentioned inside a ``%`` comment
    never reaches the PDF, so only active lines matter for the regression."""
    return "\n".join(
        line
        for line in path.read_text().splitlines()
        if not line.lstrip().startswith("%")
    )


def test_no_tables_header_emits_no_table_float(tmp_path):
    # Arrange
    compiled = _run_gather(tmp_path, real_table=False)
    # Act
    active = _active_latex(compiled / "00_Tables_Header.tex")
    # Assert
    assert "\\begin{table}" not in active


def test_no_tables_header_has_no_zero_label(tmp_path):
    # Arrange
    compiled = _run_gather(tmp_path, real_table=False)
    # Act
    active = _active_latex(compiled / "00_Tables_Header.tex")
    # Assert
    assert "\\label{tab:" not in active


def test_no_tables_header_has_no_stray_caption(tmp_path):
    # Arrange
    compiled = _run_gather(tmp_path, real_table=False)
    # Act
    active = _active_latex(compiled / "00_Tables_Header.tex")
    # Assert
    assert "\\caption{" not in active


def test_real_table_still_gathered(tmp_path):
    # Arrange
    compiled = _run_gather(tmp_path, real_table=True)
    # Act
    final = (compiled / "FINAL.tex").read_text()
    # Assert
    assert "01_real.tex" in final
