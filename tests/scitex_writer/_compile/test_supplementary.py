#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for supplementary materials compilation.

Tests compile_supplementary function with various options:
- no_figs: Exclude figures (default includes figures)
- ppt2tif: PowerPoint to TIF conversion
- crop_tif: TIF cropping
- quiet: Output verbosity
- log_callback: Live logging
- progress_callback: Progress tracking
"""

import pytest

pytest.importorskip("git")
from pathlib import Path
from unittest.mock import Mock, patch

from scitex_writer._compile.supplementary import compile_supplementary
from scitex_writer._dataclasses import CompilationResult


class TestCompileSupplementary:
    """Test suite for compile_supplementary function."""

    def test_import(self):
        """Test that compile_supplementary can be imported."""
        from scitex_writer._compile import compile_supplementary as cs

        assert callable(cs)

    def test_signature(self):
        """Test function signature has expected parameters."""
        import inspect

        sig = inspect.signature(compile_supplementary)
        params = list(sig.parameters.keys())

        assert "project_dir" in params
        assert "timeout" in params
        assert "no_figs" in params
        assert "ppt2tif" in params
        assert "crop_tif" in params
        assert "quiet" in params
        assert "log_callback" in params
        assert "progress_callback" in params

    def test_default_parameters(self):
        """Test default parameter values."""
        import inspect

        sig = inspect.signature(compile_supplementary)

        assert sig.parameters["timeout"].default == 300
        assert sig.parameters["no_figs"].default is False
        assert sig.parameters["ppt2tif"].default is False
        assert sig.parameters["crop_tif"].default is False
        assert sig.parameters["quiet"].default is False
        assert sig.parameters["log_callback"].default is None
        assert sig.parameters["progress_callback"].default is None

    @patch("scitex_writer._compile.supplementary.run_compile")
    def test_calls_run_compile_with_supplementary_type(self, mock_run_compile):
        """Test that compile_supplementary calls run_compile with 'supplementary' doc_type."""
        mock_run_compile.return_value = CompilationResult(
            success=True,
            exit_code=0,
            stdout="",
            stderr="",
            duration=1.0,
        )

        project_dir = Path("/tmp/test-project")
        compile_supplementary(project_dir)

        mock_run_compile.assert_called_once()
        args, kwargs = mock_run_compile.call_args
        assert args[0] == "supplementary"
        assert args[1] == project_dir

    @patch("scitex_writer._compile.supplementary.run_compile")
    def test_passes_no_figs_option(self, mock_run_compile):
        """Test that no_figs option is passed to run_compile."""
        mock_run_compile.return_value = CompilationResult(
            success=True,
            exit_code=0,
            stdout="",
            stderr="",
            duration=1.0,
        )

        project_dir = Path("/tmp/test-project")
        compile_supplementary(project_dir, no_figs=True)

        _, kwargs = mock_run_compile.call_args
        assert kwargs["no_figs"] is True

    @patch("scitex_writer._compile.supplementary.run_compile")
    def test_passes_ppt2tif_option(self, mock_run_compile):
        """Test that ppt2tif option is passed to run_compile."""
        mock_run_compile.return_value = CompilationResult(
            success=True,
            exit_code=0,
            stdout="",
            stderr="",
            duration=1.0,
        )

        project_dir = Path("/tmp/test-project")
        compile_supplementary(project_dir, ppt2tif=True)

        _, kwargs = mock_run_compile.call_args
        assert kwargs["ppt2tif"] is True

    @patch("scitex_writer._compile.supplementary.run_compile")
    def test_passes_crop_tif_option(self, mock_run_compile):
        """Test that crop_tif option is passed to run_compile."""
        mock_run_compile.return_value = CompilationResult(
            success=True,
            exit_code=0,
            stdout="",
            stderr="",
            duration=1.0,
        )

        project_dir = Path("/tmp/test-project")
        compile_supplementary(project_dir, crop_tif=True)

        _, kwargs = mock_run_compile.call_args
        assert kwargs["crop_tif"] is True

    @patch("scitex_writer._compile.supplementary.run_compile")
    def test_passes_quiet_option(self, mock_run_compile):
        """Test that quiet option is passed to run_compile."""
        mock_run_compile.return_value = CompilationResult(
            success=True,
            exit_code=0,
            stdout="",
            stderr="",
            duration=1.0,
        )

        project_dir = Path("/tmp/test-project")
        compile_supplementary(project_dir, quiet=True)

        _, kwargs = mock_run_compile.call_args
        assert kwargs["quiet"] is True

    @patch("scitex_writer._compile.supplementary.run_compile")
    def test_passes_callbacks(self, mock_run_compile):
        """Test that callbacks are passed to run_compile."""
        mock_run_compile.return_value = CompilationResult(
            success=True,
            exit_code=0,
            stdout="",
            stderr="",
            duration=1.0,
        )

        log_callback = Mock()
        progress_callback = Mock()

        project_dir = Path("/tmp/test-project")
        compile_supplementary(
            project_dir,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )

        _, kwargs = mock_run_compile.call_args
        assert kwargs["log_callback"] is log_callback
        assert kwargs["progress_callback"] is progress_callback

    @patch("scitex_writer._compile.supplementary.run_compile")
    def test_passes_multiple_options(self, mock_run_compile):
        """Test that multiple options are passed correctly."""
        mock_run_compile.return_value = CompilationResult(
            success=True,
            exit_code=0,
            stdout="",
            stderr="",
            duration=1.0,
        )

        project_dir = Path("/tmp/test-project")
        compile_supplementary(
            project_dir,
            ppt2tif=True,
            crop_tif=True,
            quiet=True,
        )

        _, kwargs = mock_run_compile.call_args
        assert kwargs["ppt2tif"] is True
        assert kwargs["crop_tif"] is True
        assert kwargs["quiet"] is True

    @patch("scitex_writer._compile.supplementary.run_compile")
    def test_returns_compilation_result(self, mock_run_compile):
        """Test that function returns CompilationResult."""
        expected_result = CompilationResult(
            success=True,
            exit_code=0,
            stdout="Test output",
            stderr="",
            duration=2.5,
        )
        mock_run_compile.return_value = expected_result

        project_dir = Path("/tmp/test-project")
        result = compile_supplementary(project_dir)

        assert result is expected_result
        assert result.success is True
        assert result.exit_code == 0
        assert result.duration == 2.5


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
