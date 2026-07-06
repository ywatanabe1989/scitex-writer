"""run_overflow_check.sh auto-runs the overflow check post-compile.

Item 2 of writer-overflow-prevention-followups: after each compile the
post-compile wiring must invoke check_overflow.py against the just-produced
LaTeX .log, honoring the resolved overflow severity (off/warn/error) and
staying robust when the .log is missing (an earlier compile failure).

No mocks (STX-NM002): each test drives the REAL run_overflow_check.sh over a
sandbox project with a stand-in .log and asserts on its behavior.
"""

import os
import subprocess
from pathlib import Path

_MODULE = (
    Path(__file__).resolve().parents[4] / "scripts/shell/modules/run_overflow_check.sh"
)

# A real pdfTeX overfull-hbox line (a too-wide tabular / table not shown
# entirely) — check_overflow.py parses exactly this shape.
_OVERFULL_LOG = (
    "This is pdfTeX, Version 3.14159265\n"
    "Overfull \\hbox (72.26999pt too wide) in alignment at lines 120--145\n"
    "[1] [2] )\n"
)


def _run(project_dir, level=None):
    env = {
        "PROJECT_ROOT": str(project_dir),
        "SCITEX_WRITER_DOC_TYPE": "manuscript",
        # Isolate from the real ~/.scitex/writer/config.yaml so the resolver
        # falls through to the check's own default (warn) unless overridden.
        "HOME": str(project_dir),
        "PATH": os.environ["PATH"],
    }
    if level is not None:
        env["SCITEX_WRITER_OVERFLOW"] = level
    return subprocess.run(
        ["bash", str(_MODULE)],
        capture_output=True,
        text=True,
        env=env,
    )


def _project_with_log(tmp_path, log_text):
    logs = tmp_path / "01_manuscript" / "logs"
    logs.mkdir(parents=True)
    (logs / "manuscript.log").write_text(log_text)
    return tmp_path


def _project_without_log(tmp_path):
    # doc dir exists (compile started) but no .log landed (compile failed).
    (tmp_path / "01_manuscript").mkdir(parents=True)
    return tmp_path


def test_overflow_box_in_log_is_reported(tmp_path):
    # Arrange
    project = _project_with_log(tmp_path, _OVERFULL_LOG)
    # Act
    result = _run(project)
    # Assert
    assert "72.3pt too wide" in result.stdout


def test_warn_level_does_not_block_compile(tmp_path):
    # Arrange
    project = _project_with_log(tmp_path, _OVERFULL_LOG)
    # Act
    result = _run(project)  # default level is warn
    # Assert
    assert result.returncode == 0


def test_error_level_blocks_on_overflow(tmp_path):
    # Arrange
    project = _project_with_log(tmp_path, _OVERFULL_LOG)
    # Act
    result = _run(project, level="error")
    # Assert
    assert result.returncode == 1


def test_off_level_skips_with_loud_disabled_note(tmp_path):
    # Arrange
    project = _project_with_log(tmp_path, _OVERFULL_LOG)
    # Act
    result = _run(project, level="off")
    # Assert
    assert "disabled" in result.stdout


def test_off_level_does_not_block(tmp_path):
    # Arrange
    project = _project_with_log(tmp_path, _OVERFULL_LOG)
    # Act
    result = _run(project, level="off")
    # Assert
    assert result.returncode == 0


def test_missing_log_reports_could_not_check(tmp_path):
    # Arrange
    project = _project_without_log(tmp_path)
    # Act
    result = _run(project)
    # Assert
    assert "No .log found" in result.stdout


def test_missing_log_does_not_crash(tmp_path):
    # Arrange
    project = _project_without_log(tmp_path)
    # Act
    result = _run(project)
    # Assert
    assert result.returncode == 0
