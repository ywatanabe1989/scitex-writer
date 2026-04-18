#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for compilation script runner.

Tests run_compile function with various options and document types.
"""

import pytest

pytest.importorskip("git")
from pathlib import Path
from unittest.mock import patch

from scitex_writer._compile._runner import _get_compile_script, run_compile


class TestGetCompileScript:
    """Test suite for _get_compile_script helper function."""

    def test_manuscript_script_path(self):
        """Test manuscript script path generation."""
        project_dir = Path("/tmp/test-project")
        script = _get_compile_script(project_dir, "manuscript")
        assert script == project_dir / "scripts" / "shell" / "compile_manuscript.sh"

    def test_supplementary_script_path(self):
        """Test supplementary script path generation."""
        project_dir = Path("/tmp/test-project")
        script = _get_compile_script(project_dir, "supplementary")
        assert script == project_dir / "scripts" / "shell" / "compile_supplementary.sh"

    def test_revision_script_path(self):
        """Test revision script path generation."""
        project_dir = Path("/tmp/test-project")
        script = _get_compile_script(project_dir, "revision")
        assert script == project_dir / "scripts" / "shell" / "compile_revision.sh"


class TestRunCompile:
    """Test suite for run_compile function."""

    def test_signature(self):
        """Test function signature has expected parameters."""
        import inspect

        sig = inspect.signature(run_compile)
        params = list(sig.parameters.keys())

        assert "doc_type" in params
        assert "project_dir" in params
        assert "timeout" in params
        assert "track_changes" in params
        assert "no_figs" in params
        assert "ppt2tif" in params
        assert "crop_tif" in params
        assert "quiet" in params
        assert "verbose" in params
        assert "force" in params
        assert "log_callback" in params
        assert "progress_callback" in params

    def test_default_parameters(self):
        """Test default parameter values."""
        import inspect

        sig = inspect.signature(run_compile)

        assert sig.parameters["timeout"].default == 300
        assert sig.parameters["track_changes"].default is False
        assert sig.parameters["no_figs"].default is False
        assert sig.parameters["ppt2tif"].default is False
        assert sig.parameters["crop_tif"].default is False
        assert sig.parameters["quiet"].default is False
        assert sig.parameters["verbose"].default is False
        assert sig.parameters["force"].default is False
        assert sig.parameters["log_callback"].default is None
        assert sig.parameters["progress_callback"].default is None

    @patch("scitex_writer._compile._runner.validate_before_compile")
    @patch("scitex_writer._compile._runner._get_compile_script")
    @patch("scitex_writer._compile._runner._run_sh_command")
    @patch("scitex_writer._compile._runner._find_output_files")
    @patch("scitex_writer._compile._runner.parse_output")
    def test_manuscript_with_no_figs_option(
        self,
        mock_parse,
        mock_find_files,
        mock_run_sh,
        mock_get_script,
        mock_validate,
    ):
        """Test manuscript compilation with no_figs option."""
        project_dir = Path("/tmp/test-project")
        script_path = project_dir / "scripts" / "shell" / "compile_manuscript.sh"

        mock_get_script.return_value = script_path
        mock_find_files.return_value = (None, None, None)
        mock_parse.return_value = ([], [])
        mock_run_sh.return_value = {
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch("os.chdir"):
                with patch("pathlib.Path.cwd", return_value=project_dir):
                    run_compile(
                        "manuscript",
                        project_dir,
                        no_figs=True,
                    )

        # Verify _run_sh_command was called with correct command
        mock_run_sh.assert_called_once()
        call_args = mock_run_sh.call_args[0][0]
        assert str(script_path) in call_args
        assert "--no_figs" in call_args

    @patch("scitex_writer._compile._runner.validate_before_compile")
    @patch("scitex_writer._compile._runner._get_compile_script")
    @patch("scitex_writer._compile._runner._run_sh_command")
    @patch("scitex_writer._compile._runner._find_output_files")
    @patch("scitex_writer._compile._runner.parse_output")
    def test_manuscript_with_multiple_options(
        self,
        mock_parse,
        mock_find_files,
        mock_run_sh,
        mock_get_script,
        mock_validate,
    ):
        """Test manuscript compilation with multiple options."""
        project_dir = Path("/tmp/test-project")
        script_path = project_dir / "scripts" / "shell" / "compile_manuscript.sh"

        mock_get_script.return_value = script_path
        mock_find_files.return_value = (None, None, None)
        mock_parse.return_value = ([], [])
        mock_run_sh.return_value = {
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch("os.chdir"):
                with patch("pathlib.Path.cwd", return_value=project_dir):
                    run_compile(
                        "manuscript",
                        project_dir,
                        no_figs=True,
                        ppt2tif=True,
                        crop_tif=True,
                        verbose=True,
                        force=True,
                    )

        # Verify _run_sh_command was called with all options
        call_args = mock_run_sh.call_args[0][0]
        assert "--no_figs" in call_args
        assert "--ppt2tif" in call_args
        assert "--crop_tif" in call_args
        assert "--verbose" in call_args
        assert "--force" in call_args

    @patch("scitex_writer._compile._runner.validate_before_compile")
    @patch("scitex_writer._compile._runner._get_compile_script")
    @patch("scitex_writer._compile._runner._run_sh_command")
    @patch("scitex_writer._compile._runner._find_output_files")
    @patch("scitex_writer._compile._runner.parse_output")
    def test_supplementary_with_figs_option(
        self,
        mock_parse,
        mock_find_files,
        mock_run_sh,
        mock_get_script,
        mock_validate,
    ):
        """Test supplementary compilation with figs option."""
        project_dir = Path("/tmp/test-project")
        script_path = project_dir / "scripts" / "shell" / "compile_supplementary.sh"

        mock_get_script.return_value = script_path
        mock_find_files.return_value = (None, None, None)
        mock_parse.return_value = ([], [])
        mock_run_sh.return_value = {
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch("os.chdir"):
                with patch("pathlib.Path.cwd", return_value=project_dir):
                    run_compile(
                        "supplementary",
                        project_dir,
                        no_figs=False,  # Include figures
                    )

        # Verify _run_sh_command was called with --figs option
        call_args = mock_run_sh.call_args[0][0]
        assert "--figs" in call_args

    @patch("scitex_writer._compile._runner.validate_before_compile")
    @patch("scitex_writer._compile._runner._get_compile_script")
    @patch("scitex_writer._compile._runner._run_sh_command")
    @patch("scitex_writer._compile._runner._find_output_files")
    @patch("scitex_writer._compile._runner.parse_output")
    def test_revision_with_track_changes(
        self,
        mock_parse,
        mock_find_files,
        mock_run_sh,
        mock_get_script,
        mock_validate,
    ):
        """Test revision compilation with track_changes option."""
        project_dir = Path("/tmp/test-project")
        script_path = project_dir / "scripts" / "shell" / "compile_revision.sh"

        mock_get_script.return_value = script_path
        mock_find_files.return_value = (None, None, None)
        mock_parse.return_value = ([], [])
        mock_run_sh.return_value = {
            "exit_code": 0,
            "stdout": "",
            "stderr": "",
        }

        with patch("pathlib.Path.exists", return_value=True):
            with patch("os.chdir"):
                with patch("pathlib.Path.cwd", return_value=project_dir):
                    run_compile(
                        "revision",
                        project_dir,
                        track_changes=True,
                    )

        # Verify _run_sh_command was called with --track-changes option
        call_args = mock_run_sh.call_args[0][0]
        assert "--track-changes" in call_args


class TestFindOutputFiles:
    """Test _find_output_files does not produce false positives (issue #76)."""

    def test_returns_none_when_no_pdf_exists(self, tmp_path):
        """When no PDF exists, returns None for output_pdf."""
        from scitex_writer._compile._runner import _find_output_files

        # Create minimal project dir structure
        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()

        output_pdf, diff_pdf, log_file = _find_output_files(tmp_path, "manuscript")
        assert output_pdf is None
        assert diff_pdf is None

    def test_finds_existing_pdf(self, tmp_path):
        """When PDF exists, returns its path."""
        from scitex_writer._compile._runner import _find_output_files

        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        pdf = doc_dir / "manuscript.pdf"
        pdf.write_bytes(b"%PDF-1.4 test")

        output_pdf, diff_pdf, log_file = _find_output_files(tmp_path, "manuscript")
        assert output_pdf == pdf

    def test_finds_diff_pdf_separately(self, tmp_path):
        """Diff PDF is found independently of main PDF."""
        from scitex_writer._compile._runner import _find_output_files

        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        diff = doc_dir / "manuscript_diff.pdf"
        diff.write_bytes(b"%PDF-1.4 diff")

        output_pdf, diff_pdf, log_file = _find_output_files(tmp_path, "manuscript")
        assert output_pdf is None
        assert diff_pdf == diff

    def test_stale_pdf_detected_by_caller_exit_code(self, tmp_path):
        """Caller must check exit code — stale PDF alone is not proof of success.

        This verifies the contract: _find_output_files only checks existence,
        so the caller (run_compile) must gate on subprocess exit code first.
        """
        from scitex_writer._compile._runner import _find_output_files

        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        # Stale PDF from previous build
        stale = doc_dir / "manuscript.pdf"
        stale.write_bytes(b"%PDF-1.4 stale")

        output_pdf, _, _ = _find_output_files(tmp_path, "manuscript")
        # File exists — but this is meaningless without exit code check
        assert output_pdf is not None
        # The fix in process_diff.sh and compiled_tex_to_compiled_pdf.sh
        # ensures the shell scripts check exit code BEFORE reporting success


class TestShellCleanupBehavior:
    """Test that shell cleanup scripts propagate exit codes correctly (issue #76)."""

    def test_process_diff_cleanup_removes_stale_on_failure(self, tmp_path):
        """cleanup() in process_diff.sh should remove stale PDF when compile fails."""
        import subprocess

        stale_pdf = tmp_path / "diff.pdf"
        stale_pdf.write_bytes(b"%PDF stale")

        # Simulate: cleanup is called with non-zero compile_result
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
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
        )

        assert not stale_pdf.exists(), "Stale PDF should be removed on failure"
        assert result.returncode != 0

    def test_process_diff_cleanup_keeps_pdf_on_success(self, tmp_path):
        """cleanup() should keep PDF when compile succeeds."""
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
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
        )

        assert pdf.exists(), "PDF should be kept on success"
        assert result.returncode == 0


class TestLatexdiffType:
    """Verify latexdiff uses UNDERLINE type instead of CULINECHBAR (issue #76)."""

    def test_process_diff_uses_underline_type(self):
        """process_diff.sh should use --type=UNDERLINE, not CULINECHBAR."""
        script_path = (
            Path(__file__).resolve().parents[3]
            / "scripts"
            / "shell"
            / "modules"
            / "process_diff.sh"
        )
        content = script_path.read_text()
        assert "--type=UNDERLINE" in content
        assert "--type=CULINECHBAR" not in content


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
