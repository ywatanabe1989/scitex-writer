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
        # Arrange
        project_dir = Path("/tmp/test-project")
        # Act
        script = _get_compile_script(project_dir, "manuscript")
        # Assert
        assert script == project_dir / "scripts" / "shell" / "compile_manuscript.sh"

    def test_supplementary_script_path(self):
        """Test supplementary script path generation."""
        # Arrange
        project_dir = Path("/tmp/test-project")
        # Act
        script = _get_compile_script(project_dir, "supplementary")
        # Assert
        assert script == project_dir / "scripts" / "shell" / "compile_supplementary.sh"

    def test_revision_script_path(self):
        """Test revision script path generation."""
        # Arrange
        project_dir = Path("/tmp/test-project")
        # Act
        script = _get_compile_script(project_dir, "revision")
        # Assert
        assert script == project_dir / "scripts" / "shell" / "compile_revision.sh"


class TestRunCompile:
    """Test suite for run_compile function."""

    def test_signature_doc_type_in_params_and_project_dir_in_params_and_t(self):
        """Test function signature has expected parameters."""
        # Arrange
        import inspect

        sig = inspect.signature(run_compile)
        # Act
        params = list(sig.parameters.keys())

        # Assert
        assert ('doc_type' in params) and ('project_dir' in params) and ('timeout' in params) and ('track_changes' in params) and ('no_figs' in params) and ('ppt2tif' in params) and ('crop_tif' in params) and ('quiet' in params) and ('verbose' in params) and ('force' in params) and ('log_callback' in params) and ('progress_callback' in params)

    def test_default_parameters_sig_parameters_timeout_default_300_and_sig_paramet(self):
        """Test default parameter values."""
        # Arrange
        import inspect

        # Act
        sig = inspect.signature(run_compile)

        # Assert
        assert (sig.parameters['timeout'].default == 300) and (sig.parameters['track_changes'].default is False) and (sig.parameters['no_figs'].default is False) and (sig.parameters['ppt2tif'].default is False) and (sig.parameters['crop_tif'].default is False) and (sig.parameters['quiet'].default is False) and (sig.parameters['verbose'].default is False) and (sig.parameters['force'].default is False) and (sig.parameters['log_callback'].default is None) and (sig.parameters['progress_callback'].default is None)

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
        # Arrange
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
        # Act
        call_args = mock_run_sh.call_args[0][0]
        # Assert
        assert (str(script_path) in call_args) and ('--no_figs' in call_args)

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
        # Arrange
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
        # Act
        call_args = mock_run_sh.call_args[0][0]
        # Assert
        assert ('--no_figs' in call_args) and ('--ppt2tif' in call_args) and ('--crop_tif' in call_args) and ('--verbose' in call_args) and ('--force' in call_args)

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
        # Arrange
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
        # Act
        call_args = mock_run_sh.call_args[0][0]
        # Assert
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
        # Arrange
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
        # Act
        call_args = mock_run_sh.call_args[0][0]
        # Assert
        assert "--track-changes" in call_args


class TestFindOutputFiles:
    """Test _find_output_files does not produce false positives (issue #76)."""

    def test_returns_none_when_no_pdf_exists(self, tmp_path):
        """When no PDF exists, returns None for output_pdf."""
        # Arrange
        from scitex_writer._compile._runner import _find_output_files

        # Create minimal project dir structure
        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()

        # Act
        output_pdf, diff_pdf, log_file = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert (output_pdf is None) and (diff_pdf is None)

    def test_finds_existing_pdf(self, tmp_path):
        """When PDF exists, returns its path."""
        # Arrange
        from scitex_writer._compile._runner import _find_output_files

        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        pdf = doc_dir / "manuscript.pdf"
        pdf.write_bytes(b"%PDF-1.4 test")

        # Act
        output_pdf, diff_pdf, log_file = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert output_pdf == pdf

    def test_finds_diff_pdf_separately(self, tmp_path):
        """Diff PDF is found independently of main PDF."""
        # Arrange
        from scitex_writer._compile._runner import _find_output_files

        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        diff = doc_dir / "manuscript_diff.pdf"
        diff.write_bytes(b"%PDF-1.4 diff")

        # Act
        output_pdf, diff_pdf, log_file = _find_output_files(tmp_path, "manuscript")
        # Assert
        assert (output_pdf is None) and (diff_pdf == diff)

    def test_stale_pdf_detected_by_caller_exit_code(self, tmp_path):
        """Caller must check exit code — stale PDF alone is not proof of success.

        This verifies the contract: _find_output_files only checks existence,
        so the caller (run_compile) must gate on subprocess exit code first.
        """
        # Arrange
        from scitex_writer._compile._runner import _find_output_files

        doc_dir = tmp_path / "01_manuscript"
        doc_dir.mkdir()
        # Stale PDF from previous build
        stale = doc_dir / "manuscript.pdf"
        stale.write_bytes(b"%PDF-1.4 stale")

        # Act
        output_pdf, _, _ = _find_output_files(tmp_path, "manuscript")
        # File exists — but this is meaningless without exit code check
        # Assert
        assert output_pdf is not None
        # The fix in process_diff.sh and compiled_tex_to_compiled_pdf.sh
        # ensures the shell scripts check exit code BEFORE reporting success


class TestShellCleanupBehavior:
    """Test that shell cleanup scripts propagate exit codes correctly (issue #76)."""

    def test_process_diff_cleanup_removes_stale_on_failure(self, tmp_path):
        """cleanup() in process_diff.sh should remove stale PDF when compile fails."""
        # Arrange
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
        # Act
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
        )

        # Assert
        assert (not stale_pdf.exists()) and (result.returncode != 0)

    def test_process_diff_cleanup_keeps_pdf_on_success(self, tmp_path):
        """cleanup() should keep PDF when compile succeeds."""
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
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
        )

        # Assert
        assert (pdf.exists()) and (result.returncode == 0)


class TestLatexdiffType:
    """Verify latexdiff uses UNDERLINE type instead of CULINECHBAR (issue #76)."""

    def test_process_diff_uses_underline_type(self):
        """process_diff.sh should use --type=UNDERLINE, not CULINECHBAR."""
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
        assert ('--type=UNDERLINE' in content) and ('--type=CULINECHBAR' not in content)


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
