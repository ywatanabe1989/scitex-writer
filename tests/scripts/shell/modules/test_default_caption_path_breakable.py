"""ensure_caption wraps the placeholder edit-path in a breakable \\url{} macro.

A bare \\texttt{<long path>} in the generated placeholder caption cannot break
and overflows the right text margin (Overfull \\hbox). \\url{} (backed by the
already-loaded xurl+hyperref preamble) breaks the path at any character.
"""

import subprocess
from pathlib import Path

_MODULES = (
    Path(__file__).resolve().parents[4]
    / "scripts/shell/modules/process_figures_modules"
)

# A long, underscore-heavy stem so the generated path is exactly the kind that
# overflows the margin when left un-breakable.
_FIGURE_STEM = "01_a_very_long_example_figure_file_name_that_overflows"


def _run_ensure_caption(tmp_path):
    cam = tmp_path / "cam"
    cam.mkdir(parents=True)
    # A main figure (not a panel: stem is NN_..., not NNx_...) with no caption
    # file yet, so ensure_caption emits the default placeholder caption.
    (cam / f"{_FIGURE_STEM}.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    script = (
        f'export SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR="{cam}";'
        f"source '{_MODULES}/00_common.src';"
        f"source '{_MODULES}/01_caption_management.src';"
        f"ensure_caption"
    )
    subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=True)
    return (cam / f"{_FIGURE_STEM}.tex").read_text()


def test_placeholder_caption_wraps_path_in_url(tmp_path):
    # Arrange
    expected = f"\\url{{{tmp_path}/cam/{_FIGURE_STEM}.tex}}"
    # Act
    caption = _run_ensure_caption(tmp_path)
    # Assert
    assert expected in caption


def test_placeholder_caption_leaves_no_unbreakable_texttt_path(tmp_path):
    # Arrange
    unbreakable = "\\texttt"
    # Act
    caption = _run_ensure_caption(tmp_path)
    # Assert
    assert unbreakable not in caption
