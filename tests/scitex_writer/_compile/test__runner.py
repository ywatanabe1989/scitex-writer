#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for compilation script runner.

run_compile builds the shell command for a doc_type and hands it to a
command executor. Instead of patching five internals + the filesystem,
these tests build a REAL valid project on disk (so validation and the
script-existence check pass) and inject a recording command_runner via
the run_compile seam to capture the constructed command.
"""

import inspect
import re
import subprocess

import pytest

pytest.importorskip("git")
from pathlib import Path

from scitex_writer._compile._runner import (
    _find_output_files,
    _get_compile_script,
    run_compile,
)
from scitex_writer._compile._validator import validate_before_compile


def _build_valid_project(project_dir: Path) -> None:
    """Materialize a structurally-valid scitex-writer project on disk.

    Builds the top-level trees, then iteratively creates whatever
    validate_before_compile reports as missing until it passes — a real
    project, no mocks. Compile scripts are written as no-op executables.
    """
    for sub in (
        "config",
        "00_shared",
        "01_manuscript",
        "02_supplementary",
        "03_revision",
        "scripts",
    ):
        (project_dir / sub).mkdir(exist_ok=True)

    for _ in range(60):
        try:
            validate_before_compile(project_dir)
            break
        except Exception as exc:  # ProjectValidationError
            made = False
            for rel in re.findall(r"expected at: ([^\s)]+)", str(exc)):
                target = project_dir / rel
                if "." in target.name and target.suffix:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text("")
                else:
                    target.mkdir(parents=True, exist_ok=True)
                made = True
            if not made:
                raise
    else:  # pragma: no cover - safety net for an unexpected validator
        raise RuntimeError("could not build a valid project structure")

    for doc_type in ("manuscript", "supplementary", "revision"):
        script = project_dir / "scripts" / "shell" / f"compile_{doc_type}.sh"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("#!/bin/bash\nexit 0\n")
        script.chmod(0o755)


class _RecordingCommandRunner:
    """Real _run_sh_command stand-in: records the cmd, returns success."""

    def __init__(self):
        self.cmd = None

    def __call__(self, cmd, **kwargs):
        self.cmd = list(cmd)
        return {"stdout": "", "stderr": "", "exit_code": 0, "success": True}


@pytest.fixture
def valid_project(tmp_path):
    _build_valid_project(tmp_path)
    return tmp_path


class TestGetCompileScript:
    """_get_compile_script path generation."""

    def test_manuscript_script_path(self):
        # Arrange
        project_dir = Path("/tmp/test-project")
        # Act
        script = _get_compile_script(project_dir, "manuscript")
        # Assert
        assert script == project_dir / "scripts" / "shell" / "compile_manuscript.sh"

    def test_supplementary_script_path(self):
        # Arrange
        project_dir = Path("/tmp/test-project")
        # Act
        script = _get_compile_script(project_dir, "supplementary")
        # Assert
        assert script == project_dir / "scripts" / "shell" / "compile_supplementary.sh"

    def test_revision_script_path(self):
        # Arrange
        project_dir = Path("/tmp/test-project")
        # Act
        script = _get_compile_script(project_dir, "revision")
        # Assert
        assert script == project_dir / "scripts" / "shell" / "compile_revision.sh"


class TestRunCompileSignature:
    """Signature / defaults."""

    def test_signature_exposes_all_documented_parameters(self):
        # Arrange
        expected = {
            "doc_type",
            "project_dir",
            "timeout",
            "track_changes",
            "no_figs",
            "ppt2tif",
            "crop_tif",
            "quiet",
            "verbose",
            "force",
            "log_callback",
            "progress_callback",
        }
        # Act
        params = set(inspect.signature(run_compile).parameters)
        # Assert
        assert expected <= params

    def test_default_timeout_is_300(self):
        # Arrange
        # Act
        sig = inspect.signature(run_compile)
        # Assert
        assert sig.parameters["timeout"].default == 300

    def test_default_boolean_flags_are_false(self):
        # Arrange
        sig = inspect.signature(run_compile)
        flags = (
            "track_changes",
            "no_figs",
            "ppt2tif",
            "crop_tif",
            "quiet",
            "verbose",
            "force",
        )
        # Act
        defaults = [sig.parameters[f].default for f in flags]
        # Assert
        assert defaults == [False] * len(flags)


class TestRunCompileCommandBuilding:
    """run_compile builds the right shell command per doc_type/options."""

    def test_manuscript_no_figs_adds_no_figs_flag(self, valid_project):
        # Arrange
        runner = _RecordingCommandRunner()
        # Act
        run_compile("manuscript", valid_project, no_figs=True, command_runner=runner)
        # Assert
        assert "--no_figs" in runner.cmd

    def test_manuscript_passes_ppt2tif_flag(self, valid_project):
        # Arrange
        runner = _RecordingCommandRunner()
        # Act
        run_compile("manuscript", valid_project, ppt2tif=True, command_runner=runner)
        # Assert
        assert "--ppt2tif" in runner.cmd

    def test_manuscript_passes_crop_tif_flag(self, valid_project):
        # Arrange
        runner = _RecordingCommandRunner()
        # Act
        run_compile("manuscript", valid_project, crop_tif=True, command_runner=runner)
        # Assert
        assert "--crop_tif" in runner.cmd

    def test_manuscript_passes_verbose_flag(self, valid_project):
        # Arrange
        runner = _RecordingCommandRunner()
        # Act
        run_compile("manuscript", valid_project, verbose=True, command_runner=runner)
        # Assert
        assert "--verbose" in runner.cmd

    def test_manuscript_passes_force_flag(self, valid_project):
        # Arrange
        runner = _RecordingCommandRunner()
        # Act
        run_compile("manuscript", valid_project, force=True, command_runner=runner)
        # Assert
        assert "--force" in runner.cmd

    def test_manuscript_command_targets_manuscript_script(self, valid_project):
        # Arrange
        runner = _RecordingCommandRunner()
        # Act
        run_compile("manuscript", valid_project, command_runner=runner)
        # Assert
        assert runner.cmd[0].endswith("compile_manuscript.sh")

    def test_supplementary_with_figs_adds_figs_flag(self, valid_project):
        # Arrange
        runner = _RecordingCommandRunner()
        # Act
        run_compile(
            "supplementary", valid_project, no_figs=False, command_runner=runner
        )
        # Assert
        assert "--figs" in runner.cmd

    def test_revision_track_changes_adds_track_changes_flag(self, valid_project):
        # Arrange
        runner = _RecordingCommandRunner()
        # Act
        run_compile(
            "revision", valid_project, track_changes=True, command_runner=runner
        )
        # Assert
        assert "--track-changes" in runner.cmd


class TestFindOutputFiles:
    """_find_output_files does not produce false positives (issue #76)."""

    def test_returns_none_for_output_pdf_when_none_exists(self, tmp_path):
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        # Act
        output_pdf, _diff_pdf, _log = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert output_pdf is None

    def test_returns_none_for_diff_pdf_when_none_exists(self, tmp_path):
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        # Act
        _output_pdf, diff_pdf, _log = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert diff_pdf is None

    def test_finds_existing_output_pdf(self, tmp_path):
        # Arrange
        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        pdf = doc_dir / "manuscript.pdf"
        pdf.write_bytes(b"%PDF-1.4 test")
        # Act
        output_pdf, _diff_pdf, _log = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert output_pdf == pdf

    def test_finds_diff_pdf_independently_of_main_pdf(self, tmp_path):
        # Arrange
        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        diff = doc_dir / "manuscript_diff.pdf"
        diff.write_bytes(b"%PDF-1.4 diff")
        # Act
        _output_pdf, diff_pdf, _log = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert diff_pdf == diff

    def test_existence_check_alone_finds_stale_pdf(self, tmp_path):
        """_find_output_files only checks existence; the caller must gate on
        the subprocess exit code before treating a stale PDF as success."""
        # Arrange
        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        (doc_dir / "manuscript.pdf").write_bytes(b"%PDF-1.4 stale")
        # Act
        output_pdf, _, _ = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert output_pdf is not None


class TestShellCleanupBehavior:
    """Shell cleanup scripts propagate exit codes correctly (issue #76)."""

    _CLEANUP_FUNC = """
    echo_error() { echo "ERROR: $*" >&2; }
    echo_success() { echo "OK: $*"; }
    echo_info() { echo "INFO: $*"; }
    cleanup() {
        local compile_result=${1:-1}
        local pdf_basename
        pdf_basename=$(basename "$SCITEX_WRITER_DIFF_PDF")
        local pdf_in_logs="${LOG_DIR}/${pdf_basename}"
        if [ -f "$pdf_in_logs" ]; then
            mv "$pdf_in_logs" "$SCITEX_WRITER_DIFF_PDF"
        fi
        if [ "$compile_result" -ne 0 ]; then
            echo_error "failed (exit code: $compile_result)"
            [ -f "$SCITEX_WRITER_DIFF_PDF" ] && rm -f "$SCITEX_WRITER_DIFF_PDF"
            return 1
        fi
        if [ -f "$SCITEX_WRITER_DIFF_PDF" ]; then
            echo_success "ready"
        else
            echo_error "not created"
            return 1
        fi
    }
    """

    def _run_cleanup(self, pdf, log_dir, compile_result):
        script = (
            f'SCITEX_WRITER_DIFF_PDF="{pdf}"\n'
            f'LOG_DIR="{log_dir}"\n'
            f'mkdir -p "$LOG_DIR"\n'
            + self._CLEANUP_FUNC
            + f"\ncleanup {compile_result}\n"
        )
        return subprocess.run(["bash", "-c", script], capture_output=True, text=True)

    def test_cleanup_removes_stale_pdf_on_failure(self, tmp_path):
        # Arrange
        stale_pdf = tmp_path / "diff.pdf"
        stale_pdf.write_bytes(b"%PDF stale")
        # Act
        self._run_cleanup(stale_pdf, tmp_path / "logs", compile_result=1)
        # Assert
        assert not stale_pdf.exists()

    def test_cleanup_returns_nonzero_on_failure(self, tmp_path):
        # Arrange
        stale_pdf = tmp_path / "diff.pdf"
        stale_pdf.write_bytes(b"%PDF stale")
        # Act
        result = self._run_cleanup(stale_pdf, tmp_path / "logs", compile_result=1)
        # Assert
        assert result.returncode != 0

    def test_cleanup_keeps_pdf_on_success(self, tmp_path):
        # Arrange
        pdf = tmp_path / "diff.pdf"
        pdf.write_bytes(b"%PDF fresh")
        # Act
        self._run_cleanup(pdf, tmp_path / "logs", compile_result=0)
        # Assert
        assert pdf.exists()

    def test_cleanup_returns_zero_on_success(self, tmp_path):
        # Arrange
        pdf = tmp_path / "diff.pdf"
        pdf.write_bytes(b"%PDF fresh")
        # Act
        result = self._run_cleanup(pdf, tmp_path / "logs", compile_result=0)
        # Assert
        assert result.returncode == 0


class TestLatexdiffType:
    """latexdiff uses UNDERLINE type instead of CULINECHBAR (issue #76)."""

    @pytest.fixture
    def process_diff_content(self):
        script_path = (
            Path(__file__).resolve().parents[3]
            / "scripts"
            / "shell"
            / "modules"
            / "process_diff.sh"
        )
        return script_path.read_text()

    def test_process_diff_uses_underline_type(self, process_diff_content):
        # Arrange
        # Act
        # Assert
        assert "--type=UNDERLINE" in process_diff_content

    def test_process_diff_does_not_use_culinechbar(self, process_diff_content):
        # Arrange
        # Act
        # Assert
        assert "--type=CULINECHBAR" not in process_diff_content


class TestCompilePathUsesPythonPipelines:
    """The compile path must reach the PYTHON engine, not the old shell modules.

    `run_compile` shells out to `scripts/shell/compile_<doc_type>.sh`, so the
    heavy stages those scripts invoke ARE the compile path. Until 2.29.0 they
    invoked `modules/process_{figures,tables,diff,archive}.sh` — meaning the
    Python ports (and the four bugs they fixed) were unreachable from a real
    compile. These tests pin the delegation so it cannot silently regress.
    """

    SHELL_MODULES = [
        "process_figures.sh",
        "process_tables.sh",
        "process_diff.sh",
        "process_archive.sh",
    ]

    def _script_text(self, doc_type: str) -> str:
        project_root = Path(__file__).resolve().parents[3]
        return _get_compile_script(project_root, doc_type).read_text()

    def _delegates(self, doc_type: str, stage: str) -> bool:
        """True iff the compile script launches `stage` via the Python launcher.

        The path may or may not be quoted (`"$PROJECT_ROOT/.../x.sh" figures`
        vs `./scripts/.../x.sh figures`), so match the launcher + stage pair.
        """
        pattern = rf'modules/run_python_pipeline\.sh"?\s+{stage}\b'
        return re.search(pattern, self._script_text(doc_type)) is not None

    @pytest.mark.parametrize("doc_type", ["manuscript", "supplementary", "revision"])
    @pytest.mark.parametrize("shell_module", SHELL_MODULES)
    def test_compile_script_never_invokes_shell_module(self, doc_type, shell_module):
        # Arrange
        text = self._script_text(doc_type)
        # Act
        invocations = re.findall(rf"modules/{re.escape(shell_module)}", text)
        # Assert
        assert invocations == []

    @pytest.mark.parametrize("doc_type", ["manuscript", "supplementary", "revision"])
    def test_compile_script_delegates_figures_to_python(self, doc_type):
        # Arrange
        stage = "figures"
        # Act
        delegated = self._delegates(doc_type, stage)
        # Assert
        assert delegated

    @pytest.mark.parametrize("doc_type", ["manuscript", "supplementary", "revision"])
    def test_compile_script_delegates_tables_to_python(self, doc_type):
        # Arrange
        stage = "tables"
        # Act
        delegated = self._delegates(doc_type, stage)
        # Assert
        assert delegated

    @pytest.mark.parametrize("doc_type", ["manuscript", "supplementary"])
    def test_compile_script_delegates_diff_to_python(self, doc_type):
        # Arrange
        stage = "diff"
        # Act
        delegated = self._delegates(doc_type, stage)
        # Assert
        assert delegated

    @pytest.mark.parametrize("doc_type", ["manuscript", "supplementary", "revision"])
    def test_compile_script_delegates_archive_to_python(self, doc_type):
        # Arrange
        stage = "archive"
        # Act
        delegated = self._delegates(doc_type, stage)
        # Assert
        assert delegated


if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
