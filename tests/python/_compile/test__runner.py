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


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
