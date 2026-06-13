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

NM-rewrite (2026-06-13): replaced unittest.mock.patch/Mock with real
recording-fake collaborators injected through the new public
runner_fn/validator_fn/output_finder_fn/script_resolver_fn kwargs.
"""

from pathlib import Path

import pytest

pytest.importorskip("git")

from scitex_writer._compile.supplementary import compile_supplementary

# ---------------------------------------------------------------------------
# Real fakes
# ---------------------------------------------------------------------------


class _RecordingRunner:
    def __init__(self):
        self.calls: list[list[str]] = []

    def __call__(self, cmd, *args, **kwargs):
        self.calls.append(list(cmd))
        return {"exit_code": 0, "stdout": "", "stderr": "", "success": True}


def _noop_validator(project_dir: Path) -> None:
    return None


def _empty_output_finder(project_dir: Path, doc_type: str):
    return (None, None, None)


def _make_script_resolver(script_path: Path):
    def _resolver(project_dir: Path, doc_type: str) -> Path:
        return script_path

    return _resolver


def _setup_existing_script(tmp_path: Path) -> Path:
    script_dir = tmp_path / "scripts" / "shell"
    script_dir.mkdir(parents=True, exist_ok=True)
    script = script_dir / "compile_supplementary.sh"
    script.write_text("#!/bin/sh\nexit 0\n")
    return script


def _run(tmp_path: Path, runner: _RecordingRunner, **kwargs):
    script = _setup_existing_script(tmp_path)
    return compile_supplementary(
        tmp_path,
        runner_fn=runner,
        validator_fn=_noop_validator,
        output_finder_fn=_empty_output_finder,
        script_resolver_fn=_make_script_resolver(script),
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestCompileSupplementaryImport:
    def test_compile_supplementary_is_callable_after_import(self):
        # Arrange
        from scitex_writer._compile import compile_supplementary as cs

        # Act
        result = callable(cs)
        # Assert
        assert result is True


class TestCompileSupplementarySignature:
    def test_signature_includes_project_dir_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(compile_supplementary).parameters.keys())
        # Assert
        assert "project_dir" in params

    def test_signature_includes_timeout_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(compile_supplementary).parameters.keys())
        # Assert
        assert "timeout" in params

    def test_signature_includes_no_figs_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(compile_supplementary).parameters.keys())
        # Assert
        assert "no_figs" in params

    def test_signature_includes_ppt2tif_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(compile_supplementary).parameters.keys())
        # Assert
        assert "ppt2tif" in params

    def test_signature_includes_crop_tif_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(compile_supplementary).parameters.keys())
        # Assert
        assert "crop_tif" in params

    def test_signature_includes_quiet_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(compile_supplementary).parameters.keys())
        # Assert
        assert "quiet" in params

    def test_signature_includes_log_callback_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(compile_supplementary).parameters.keys())
        # Assert
        assert "log_callback" in params

    def test_signature_includes_progress_callback_parameter(self):
        # Arrange
        import inspect

        # Act
        params = list(inspect.signature(compile_supplementary).parameters.keys())
        # Assert
        assert "progress_callback" in params


class TestCompileSupplementaryDefaults:
    def test_default_timeout_is_300_seconds(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(compile_supplementary).parameters["timeout"].default
        # Assert
        assert default == 300

    def test_default_no_figs_is_false(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(compile_supplementary).parameters["no_figs"].default
        # Assert
        assert default is False

    def test_default_ppt2tif_is_false(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(compile_supplementary).parameters["ppt2tif"].default
        # Assert
        assert default is False

    def test_default_crop_tif_is_false(self):
        # Arrange
        import inspect

        # Act
        default = (
            inspect.signature(compile_supplementary).parameters["crop_tif"].default
        )
        # Assert
        assert default is False

    def test_default_quiet_is_false(self):
        # Arrange
        import inspect

        # Act
        default = inspect.signature(compile_supplementary).parameters["quiet"].default
        # Assert
        assert default is False

    def test_default_log_callback_is_none(self):
        # Arrange
        import inspect

        # Act
        default = (
            inspect.signature(compile_supplementary).parameters["log_callback"].default
        )
        # Assert
        assert default is None

    def test_default_progress_callback_is_none(self):
        # Arrange
        import inspect

        # Act
        default = (
            inspect.signature(compile_supplementary)
            .parameters["progress_callback"]
            .default
        )
        # Assert
        assert default is None


class TestCompileSupplementaryBehavior:
    def test_runner_called_exactly_once_for_default_invocation(self, tmp_path):
        # Arrange
        runner = _RecordingRunner()
        # Act
        _run(tmp_path, runner)
        # Assert
        assert len(runner.calls) == 1

    def test_command_invokes_supplementary_compile_script_path(self, tmp_path):
        # Arrange
        runner = _RecordingRunner()
        # Act
        _run(tmp_path, runner)
        # Assert
        assert any("compile_supplementary.sh" in arg for arg in runner.calls[0])

    def test_default_invocation_includes_figs_flag(self, tmp_path):
        """Supplementary defaults to figures included → --figs flag present."""
        # Arrange
        runner = _RecordingRunner()
        # Act
        _run(tmp_path, runner)
        # Assert
        assert "--figs" in runner.calls[0]

    def test_no_figs_option_suppresses_figs_flag(self, tmp_path):
        # Arrange
        runner = _RecordingRunner()
        # Act
        _run(tmp_path, runner, no_figs=True)
        # Assert
        assert "--figs" not in runner.calls[0]

    def test_ppt2tif_option_appends_ppt2tif_flag(self, tmp_path):
        # Arrange
        runner = _RecordingRunner()
        # Act
        _run(tmp_path, runner, ppt2tif=True)
        # Assert
        assert "--ppt2tif" in runner.calls[0]

    def test_crop_tif_option_appends_crop_tif_flag(self, tmp_path):
        # Arrange
        runner = _RecordingRunner()
        # Act
        _run(tmp_path, runner, crop_tif=True)
        # Assert
        assert "--crop_tif" in runner.calls[0]

    def test_quiet_option_appends_quiet_flag(self, tmp_path):
        # Arrange
        runner = _RecordingRunner()
        # Act
        _run(tmp_path, runner, quiet=True)
        # Assert
        assert "--quiet" in runner.calls[0]

    def test_multiple_options_all_present_in_command(self, tmp_path):
        # Arrange
        runner = _RecordingRunner()
        # Act
        _run(tmp_path, runner, ppt2tif=True, crop_tif=True, quiet=True)
        # Assert
        cmd = runner.calls[0]
        assert {"--ppt2tif", "--crop_tif", "--quiet"}.issubset(set(cmd))

    def test_progress_callback_receives_completion_update(self, tmp_path):
        # Arrange
        runner = _RecordingRunner()
        progress_events: list[tuple[int, str]] = []

        def record_progress(pct: int, step: str) -> None:
            progress_events.append((pct, step))

        # Act
        _run(tmp_path, runner, progress_callback=record_progress)
        # Assert
        assert any(pct == 100 for pct, _ in progress_events)

    def test_returns_compilation_result_with_success_true_on_zero_exit(self, tmp_path):
        # Arrange
        runner = _RecordingRunner()
        # Act
        result = _run(tmp_path, runner)
        # Assert
        assert result.success is True

    def test_returns_compilation_result_with_exit_code_zero_on_success(self, tmp_path):
        # Arrange
        runner = _RecordingRunner()
        # Act
        result = _run(tmp_path, runner)
        # Assert
        assert result.exit_code == 0


# EOF

if __name__ == "__main__":
    import os

    pytest.main([os.path.abspath(__file__)])
