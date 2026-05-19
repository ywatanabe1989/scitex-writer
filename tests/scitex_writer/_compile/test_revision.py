#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for revision response compilation.

Tests compile_revision function with various options:
- track_changes: Enable change tracking (diff highlighting)
- log_callback: Live logging
- progress_callback: Progress tracking
"""

import pytest

pytest.importorskip("git")
from pathlib import Path
from unittest.mock import Mock, patch

from scitex_writer._compile.revision import compile_revision
from scitex_writer._dataclasses import CompilationResult


class TestCompileRevision:
    """Test suite for compile_revision function."""

    def test_import_callable_cr(self):
        """Test that compile_revision can be imported."""
        # Arrange
        # Act
        from scitex_writer._compile import compile_revision as cr

        # Assert
        assert callable(cr)

    def test_signature_project_dir_in_params_and_track_changes_in_params_(self):
        """Test function signature has expected parameters."""
        # Arrange
        import inspect

        sig = inspect.signature(compile_revision)
        # Act
        params = list(sig.parameters.keys())

        # Assert
        assert ('project_dir' in params) and ('track_changes' in params) and ('timeout' in params) and ('log_callback' in params) and ('progress_callback' in params)

    def test_default_parameters_sig_parameters_track_changes_default_is_false_and_(self):
        """Test default parameter values."""
        # Arrange
        import inspect

        # Act
        sig = inspect.signature(compile_revision)

        # Assert
        assert (sig.parameters['track_changes'].default is False) and (sig.parameters['timeout'].default == 300) and (sig.parameters['log_callback'].default is None) and (sig.parameters['progress_callback'].default is None)

    @patch("scitex_writer._compile.revision.run_compile")
    def test_calls_run_compile_with_revision_type(self, mock_run_compile):
        """Test that compile_revision calls run_compile with 'revision' doc_type."""
        # Arrange
        mock_run_compile.return_value = CompilationResult(
            success=True,
            exit_code=0,
            stdout="",
            stderr="",
            duration=1.0,
        )

        project_dir = Path("/tmp/test-project")
        compile_revision(project_dir)

        mock_run_compile.assert_called_once()
        # Act
        args, kwargs = mock_run_compile.call_args
        # Assert
        assert (args[0] == 'revision') and (args[1] == project_dir)

    @patch("scitex_writer._compile.revision.run_compile")
    def test_passes_track_changes_option(self, mock_run_compile):
        """Test that track_changes option is passed to run_compile."""
        # Arrange
        mock_run_compile.return_value = CompilationResult(
            success=True,
            exit_code=0,
            stdout="",
            stderr="",
            duration=1.0,
        )

        project_dir = Path("/tmp/test-project")
        compile_revision(project_dir, track_changes=True)

        # Act
        _, kwargs = mock_run_compile.call_args
        # Assert
        assert kwargs["track_changes"] is True

    @patch("scitex_writer._compile.revision.run_compile")
    def test_passes_callbacks_kwargs_log_callback_is_log_callback_and_kwargs_pro(self, mock_run_compile):
        """Test that callbacks are passed to run_compile."""
        # Arrange
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
        compile_revision(
            project_dir,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )

        # Act
        _, kwargs = mock_run_compile.call_args
        # Assert
        assert (kwargs['log_callback'] is log_callback) and (kwargs['progress_callback'] is progress_callback)

    @patch("scitex_writer._compile.revision.run_compile")
    def test_passes_timeout_kwargs_timeout_600(self, mock_run_compile):
        """Test that timeout is passed to run_compile."""
        # Arrange
        mock_run_compile.return_value = CompilationResult(
            success=True,
            exit_code=0,
            stdout="",
            stderr="",
            duration=1.0,
        )

        project_dir = Path("/tmp/test-project")
        compile_revision(project_dir, timeout=600)

        # Act
        _, kwargs = mock_run_compile.call_args
        # Assert
        assert kwargs["timeout"] == 600

    @patch("scitex_writer._compile.revision.run_compile")
    def test_returns_compilation_result(self, mock_run_compile):
        """Test that function returns CompilationResult."""
        # Arrange
        expected_result = CompilationResult(
            success=True,
            exit_code=0,
            stdout="Test output",
            stderr="",
            duration=2.5,
        )
        mock_run_compile.return_value = expected_result

        project_dir = Path("/tmp/test-project")
        # Act
        result = compile_revision(project_dir)

        # Assert
        assert (result is expected_result) and (result.success is True) and (result.exit_code == 0) and (result.duration == 2.5)


# EOF

if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
