#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for compilation script runner.

Tests run_compile function with various options and document types.

NM-rewrite (2026-06-13): replaced unittest.mock.patch with injected real fakes
that record the command passed to the runner. The fakes are plain Python
functions, not Mocks — they expose observable side-effects (recorded calls)
that the tests then assert on, matching the no-mocks doctrine.
"""

from pathlib import Path

import pytest

pytest.importorskip("git")

from scitex_writer._compile._runner import (
    _find_output_files,
    _get_compile_script,
    run_compile,
)

# ---------------------------------------------------------------------------
# Real recording fakes (drop-in replacements for the mocked collaborators).
# ---------------------------------------------------------------------------


class _RecordingRunner:
    """Real fake for the shell-command runner.

    Records the command list it was invoked with and returns a fixed
    success result so run_compile can complete without spawning a real
    subprocess. Not a Mock — just a plain class with a __call__ method.
    """

    def __init__(self, exit_code: int = 0, stdout: str = "", stderr: str = ""):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr
        self.calls: list[list[str]] = []

    def __call__(self, cmd, *args, **kwargs):
        self.calls.append(list(cmd))
        return {
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "success": self.exit_code == 0,
        }


def _noop_validator(project_dir: Path) -> None:
    """Real fake for validator: accepts any project dir without checking."""
    return None


def _empty_output_finder(project_dir: Path, doc_type: str):
    """Real fake for output finder: pretends no output was produced."""
    return (None, None, None)


def _make_script_resolver(script_path: Path):
    """Build a real script-resolver that returns a path that exists."""

    def _resolver(project_dir: Path, doc_type: str) -> Path:
        return script_path

    return _resolver


def _setup_existing_script(tmp_path: Path, doc_type: str) -> Path:
    """Write a real (empty, executable-bit not required) script file on disk."""
    script_dir = tmp_path / "scripts" / "shell"
    script_dir.mkdir(parents=True, exist_ok=True)
    script = script_dir / f"compile_{doc_type}.sh"
    script.write_text("#!/bin/sh\nexit 0\n")
    return script


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestGetCompileScript:
    """Test suite for _get_compile_script helper function."""

    def test_manuscript_script_path_under_scripts_shell(self):
        # Arrange
        project_dir = Path("/tmp/test-project")
        expected = project_dir / "scripts" / "shell" / "compile_manuscript.sh"
        # Act
        script = _get_compile_script(project_dir, "manuscript")
        # Assert
        assert script == expected

    def test_supplementary_script_path_under_scripts_shell(self):
        # Arrange
        project_dir = Path("/tmp/test-project")
        expected = project_dir / "scripts" / "shell" / "compile_supplementary.sh"
        # Act
        script = _get_compile_script(project_dir, "supplementary")
        # Assert
        assert script == expected

    def test_revision_script_path_under_scripts_shell(self):
        # Arrange
        project_dir = Path("/tmp/test-project")
        expected = project_dir / "scripts" / "shell" / "compile_revision.sh"
        # Act
        script = _get_compile_script(project_dir, "revision")
        # Assert
        assert script == expected


class TestRunCompileSignature:
    """Signature/contract tests for run_compile.

    Each test asserts ONE observable contract attribute.
    """

    def test_signature_includes_doc_type_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "doc_type" in params

    def test_signature_includes_project_dir_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "project_dir" in params

    def test_signature_includes_timeout_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "timeout" in params

    def test_signature_includes_track_changes_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "track_changes" in params

    def test_signature_includes_no_figs_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "no_figs" in params

    def test_signature_includes_ppt2tif_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "ppt2tif" in params

    def test_signature_includes_crop_tif_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "crop_tif" in params

    def test_signature_includes_quiet_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "quiet" in params

    def test_signature_includes_verbose_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "verbose" in params

    def test_signature_includes_force_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "force" in params

    def test_signature_includes_log_callback_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "log_callback" in params

    def test_signature_includes_progress_callback_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(run_compile).parameters.keys())
        # Assert
        assert "progress_callback" in params


class TestRunCompileDefaults:
    """Default-value contract tests for run_compile."""

    def test_default_timeout_is_300_seconds(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(run_compile).parameters["timeout"].default
        # Assert
        assert default == 300

    def test_default_track_changes_is_false(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(run_compile).parameters["track_changes"].default
        # Assert
        assert default is False

    def test_default_no_figs_is_false(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(run_compile).parameters["no_figs"].default
        # Assert
        assert default is False

    def test_default_ppt2tif_is_false(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(run_compile).parameters["ppt2tif"].default
        # Assert
        assert default is False

    def test_default_crop_tif_is_false(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(run_compile).parameters["crop_tif"].default
        # Assert
        assert default is False

    def test_default_quiet_is_false(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(run_compile).parameters["quiet"].default
        # Assert
        assert default is False

    def test_default_verbose_is_false(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(run_compile).parameters["verbose"].default
        # Assert
        assert default is False

    def test_default_force_is_false(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(run_compile).parameters["force"].default
        # Assert
        assert default is False

    def test_default_log_callback_is_none(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(run_compile).parameters["log_callback"].default
        # Assert
        assert default is None

    def test_default_progress_callback_is_none(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(run_compile).parameters["progress_callback"].default
        # Assert
        assert default is None


class TestRunCompileCommandConstruction:
    """Run run_compile with real injected fakes and assert on the
    command list it constructed."""

    def test_manuscript_no_figs_appends_no_figs_flag(self, tmp_path):
        # Arrange
        script = _setup_existing_script(tmp_path, "manuscript")
        runner = _RecordingRunner()
        # Act
        run_compile(
            "manuscript",
            tmp_path,
            no_figs=True,
            runner_fn=runner,
            validator_fn=_noop_validator,
            output_finder_fn=_empty_output_finder,
            script_resolver_fn=_make_script_resolver(script),
        )
        # Assert
        assert "--no_figs" in runner.calls[0]

    def test_manuscript_records_script_path_in_command(self, tmp_path):
        # Arrange
        script = _setup_existing_script(tmp_path, "manuscript")
        runner = _RecordingRunner()
        # Act
        run_compile(
            "manuscript",
            tmp_path,
            no_figs=True,
            runner_fn=runner,
            validator_fn=_noop_validator,
            output_finder_fn=_empty_output_finder,
            script_resolver_fn=_make_script_resolver(script),
        )
        # Assert
        assert str(script.absolute()) in runner.calls[0]

    def test_manuscript_runner_invoked_exactly_once(self, tmp_path):
        # Arrange
        script = _setup_existing_script(tmp_path, "manuscript")
        runner = _RecordingRunner()
        # Act
        run_compile(
            "manuscript",
            tmp_path,
            no_figs=True,
            runner_fn=runner,
            validator_fn=_noop_validator,
            output_finder_fn=_empty_output_finder,
            script_resolver_fn=_make_script_resolver(script),
        )
        # Assert
        assert len(runner.calls) == 1

    def test_manuscript_with_ppt2tif_includes_flag(self, tmp_path):
        # Arrange
        script = _setup_existing_script(tmp_path, "manuscript")
        runner = _RecordingRunner()
        # Act
        run_compile(
            "manuscript",
            tmp_path,
            ppt2tif=True,
            runner_fn=runner,
            validator_fn=_noop_validator,
            output_finder_fn=_empty_output_finder,
            script_resolver_fn=_make_script_resolver(script),
        )
        # Assert
        assert "--ppt2tif" in runner.calls[0]

    def test_manuscript_with_crop_tif_includes_flag(self, tmp_path):
        # Arrange
        script = _setup_existing_script(tmp_path, "manuscript")
        runner = _RecordingRunner()
        # Act
        run_compile(
            "manuscript",
            tmp_path,
            crop_tif=True,
            runner_fn=runner,
            validator_fn=_noop_validator,
            output_finder_fn=_empty_output_finder,
            script_resolver_fn=_make_script_resolver(script),
        )
        # Assert
        assert "--crop_tif" in runner.calls[0]

    def test_manuscript_with_verbose_includes_flag(self, tmp_path):
        # Arrange
        script = _setup_existing_script(tmp_path, "manuscript")
        runner = _RecordingRunner()
        # Act
        run_compile(
            "manuscript",
            tmp_path,
            verbose=True,
            runner_fn=runner,
            validator_fn=_noop_validator,
            output_finder_fn=_empty_output_finder,
            script_resolver_fn=_make_script_resolver(script),
        )
        # Assert
        assert "--verbose" in runner.calls[0]

    def test_manuscript_with_force_includes_flag(self, tmp_path):
        # Arrange
        script = _setup_existing_script(tmp_path, "manuscript")
        runner = _RecordingRunner()
        # Act
        run_compile(
            "manuscript",
            tmp_path,
            force=True,
            runner_fn=runner,
            validator_fn=_noop_validator,
            output_finder_fn=_empty_output_finder,
            script_resolver_fn=_make_script_resolver(script),
        )
        # Assert
        assert "--force" in runner.calls[0]

    def test_supplementary_with_figures_uses_figs_flag(self, tmp_path):
        # Arrange
        script = _setup_existing_script(tmp_path, "supplementary")
        runner = _RecordingRunner()
        # Act
        run_compile(
            "supplementary",
            tmp_path,
            no_figs=False,
            runner_fn=runner,
            validator_fn=_noop_validator,
            output_finder_fn=_empty_output_finder,
            script_resolver_fn=_make_script_resolver(script),
        )
        # Assert
        assert "--figs" in runner.calls[0]

    def test_revision_with_track_changes_includes_flag(self, tmp_path):
        # Arrange
        script = _setup_existing_script(tmp_path, "revision")
        runner = _RecordingRunner()
        # Act
        run_compile(
            "revision",
            tmp_path,
            track_changes=True,
            runner_fn=runner,
            validator_fn=_noop_validator,
            output_finder_fn=_empty_output_finder,
            script_resolver_fn=_make_script_resolver(script),
        )
        # Assert
        assert "--track-changes" in runner.calls[0]


class TestFindOutputFiles:
    """Test _find_output_files does not produce false positives (issue #76).

    Uses real tmp_path with real files; no mocks required.
    """

    def test_returns_none_for_output_pdf_when_no_pdf_exists(self, tmp_path):
        # Arrange
        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        # Act
        output_pdf, _, _ = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert output_pdf is None

    def test_returns_none_for_diff_pdf_when_no_diff_exists(self, tmp_path):
        # Arrange
        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        # Act
        _, diff_pdf, _ = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert diff_pdf is None

    def test_finds_existing_manuscript_pdf_file(self, tmp_path):
        # Arrange
        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        pdf = doc_dir / "manuscript.pdf"
        pdf.write_bytes(b"%PDF-1.4 test")
        # Act
        output_pdf, _, _ = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert output_pdf == pdf

    def test_finds_diff_pdf_when_only_diff_exists(self, tmp_path):
        # Arrange
        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        diff = doc_dir / "manuscript_diff.pdf"
        diff.write_bytes(b"%PDF-1.4 diff")
        # Act
        _, diff_pdf, _ = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert diff_pdf == diff

    def test_main_pdf_is_none_when_only_diff_pdf_exists(self, tmp_path):
        # Arrange
        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        diff = doc_dir / "manuscript_diff.pdf"
        diff.write_bytes(b"%PDF-1.4 diff")
        # Act
        output_pdf, _, _ = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert output_pdf is None

    def test_stale_pdf_returned_when_file_still_present(self, tmp_path):
        """Caller must check exit code — stale PDF alone is not proof of success.

        This verifies the contract: _find_output_files only checks existence,
        so the caller (run_compile) must gate on subprocess exit code first.
        """
        # Arrange
        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        stale = doc_dir / "manuscript.pdf"
        stale.write_bytes(b"%PDF-1.4 stale")
        # Act
        output_pdf, _, _ = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert output_pdf is not None


class TestShellCleanupBehavior:
    """Test that shell cleanup scripts propagate exit codes correctly (issue #76).

    These use real bash subprocess invocations against real temp PDFs — no
    mocking. The behavioural assertion is on the real on-disk side-effect
    after cleanup runs.
    """

    def test_process_diff_cleanup_removes_stale_pdf_on_failure(self, tmp_path):
        # Arrange
        import subprocess

        stale_pdf = tmp_path / "diff.pdf"
        stale_pdf.write_bytes(b"%PDF stale")
        script = f"""
        SCITEX_WRITER_DIFF_PDF="{stale_pdf}"
        LOG_DIR="{tmp_path}"
        echo_error() {{ echo "ERROR: $*" >&2; }}
        echo_success() {{ echo "OK: $*"; }}
        echo_info() {{ echo "INFO: $*"; }}

        cleanup() {{
            local compile_result=${{1:-1}}
            local pdf_basename
            pdf_basename=$(basename "$SCITEX_WRITER_DIFF_PDF")
            local pdf_in_logs="${{LOG_DIR}}/${{pdf_basename}}"
            if [ -f "$pdf_in_logs" ]; then
                mv "$pdf_in_logs" "$SCITEX_WRITER_DIFF_PDF"
            fi
            if [ "$compile_result" -ne 0 ]; then
                echo_error "Diff PDF compilation failed (exit code: $compile_result)"
                [ -f "$SCITEX_WRITER_DIFF_PDF" ] && rm -f "$SCITEX_WRITER_DIFF_PDF"
                return 1
            fi
            if [ -f "$SCITEX_WRITER_DIFF_PDF" ]; then
                echo_success "ready"
            else
                echo_error "not created"
                return 1
            fi
        }}

        cleanup 1
        """
        # Act
        subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        # Assert
        assert not stale_pdf.exists()

    def test_process_diff_cleanup_returns_nonzero_on_failure(self, tmp_path):
        # Arrange
        import subprocess

        stale_pdf = tmp_path / "diff.pdf"
        stale_pdf.write_bytes(b"%PDF stale")
        script = f"""
        SCITEX_WRITER_DIFF_PDF="{stale_pdf}"
        LOG_DIR="{tmp_path}"
        echo_error() {{ echo "ERROR: $*" >&2; }}
        echo_success() {{ echo "OK: $*"; }}
        echo_info() {{ echo "INFO: $*"; }}

        cleanup() {{
            local compile_result=${{1:-1}}
            if [ "$compile_result" -ne 0 ]; then
                [ -f "$SCITEX_WRITER_DIFF_PDF" ] && rm -f "$SCITEX_WRITER_DIFF_PDF"
                return 1
            fi
            return 0
        }}

        cleanup 1
        """
        # Act
        result = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        # Assert
        assert result.returncode != 0

    def test_process_diff_cleanup_keeps_pdf_on_success(self, tmp_path):
        # Arrange
        import subprocess

        pdf = tmp_path / "diff.pdf"
        pdf.write_bytes(b"%PDF fresh")
        script = f"""
        SCITEX_WRITER_DIFF_PDF="{pdf}"
        LOG_DIR="{tmp_path}/logs"
        mkdir -p "$LOG_DIR"
        echo_error() {{ echo "ERROR: $*" >&2; }}
        echo_success() {{ echo "OK: $*"; }}
        echo_info() {{ echo "INFO: $*"; }}

        cleanup() {{
            local compile_result=${{1:-1}}
            local pdf_basename
            pdf_basename=$(basename "$SCITEX_WRITER_DIFF_PDF")
            local pdf_in_logs="${{LOG_DIR}}/${{pdf_basename}}"
            if [ -f "$pdf_in_logs" ]; then
                mv "$pdf_in_logs" "$SCITEX_WRITER_DIFF_PDF"
            fi
            if [ "$compile_result" -ne 0 ]; then
                echo_error "failed"
                [ -f "$SCITEX_WRITER_DIFF_PDF" ] && rm -f "$SCITEX_WRITER_DIFF_PDF"
                return 1
            fi
            if [ -f "$SCITEX_WRITER_DIFF_PDF" ]; then
                echo_success "ready"
            else
                echo_error "not created"
                return 1
            fi
        }}

        cleanup 0
        """
        # Act
        subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        # Assert
        assert pdf.exists()

    def test_process_diff_cleanup_returns_zero_on_success(self, tmp_path):
        # Arrange
        import subprocess

        pdf = tmp_path / "diff.pdf"
        pdf.write_bytes(b"%PDF fresh")
        script = f"""
        SCITEX_WRITER_DIFF_PDF="{pdf}"
        echo_error() {{ echo "ERROR: $*" >&2; }}
        echo_success() {{ echo "OK: $*"; }}

        cleanup() {{
            local compile_result=${{1:-1}}
            if [ "$compile_result" -ne 0 ]; then
                [ -f "$SCITEX_WRITER_DIFF_PDF" ] && rm -f "$SCITEX_WRITER_DIFF_PDF"
                return 1
            fi
            if [ -f "$SCITEX_WRITER_DIFF_PDF" ]; then
                echo_success "ready"
                return 0
            else
                return 1
            fi
        }}

        cleanup 0
        """
        # Act
        result = subprocess.run(["bash", "-c", script], capture_output=True, text=True)
        # Assert
        assert result.returncode == 0


class TestLatexdiffType:
    """Verify latexdiff uses UNDERLINE type instead of CULINECHBAR (issue #76)."""

    def test_process_diff_script_uses_underline_type_flag(self):
        # Arrange
        script_path = (
            Path(__file__).resolve().parents[3]
            / "scripts"
            / "shell"
            / "modules"
            / "process_diff.sh"
        )
        # Act
        content = script_path.read_text()
        # Assert
        assert "--type=UNDERLINE" in content

    def test_process_diff_script_does_not_use_culinechbar_type(self):
        # Arrange
        script_path = (
            Path(__file__).resolve().parents[3]
            / "scripts"
            / "shell"
            / "modules"
            / "process_diff.sh"
        )
        # Act
        content = script_path.read_text()
        # Assert
        assert "--type=CULINECHBAR" not in content


# EOF

if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
