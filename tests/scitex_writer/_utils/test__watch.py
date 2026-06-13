#!/usr/bin/env python3
"""Tests for scitex_writer._utils._watch."""

import subprocess

import pytest

from scitex_writer._utils import _watch as watch_mod
from scitex_writer._utils._watch import watch_manuscript


class _FakeStdout:
    """Mimics subprocess Popen.stdout for readline-iteration tests."""

    def __init__(self, lines=None, side_effect=None):
        self._lines = list(lines or [])
        self._side_effect = side_effect

    def readline(self):
        if self._side_effect is not None:
            exc = self._side_effect
            # Raise once, then clear so subsequent calls return ""
            self._side_effect = None
            raise exc
        if self._lines:
            return self._lines.pop(0)
        return ""


class _FakePopen:
    """Drop-in replacement for subprocess.Popen capturing call args."""

    def __init__(self, lines=None, readline_exc=None):
        self.stdout = _FakeStdout(lines, readline_exc)
        self.wait_calls = []
        self.terminate_calls = 0
        self.kill_calls = 0
        self.last_args = None
        self.last_kwargs = None

    def __call__(self, *args, **kwargs):
        # Capture invocation for test inspection.
        self.last_args = args
        self.last_kwargs = kwargs
        return self

    def wait(self, timeout=None):
        self.wait_calls.append(timeout)

    def terminate(self):
        self.terminate_calls += 1

    def kill(self):
        self.kill_calls += 1


@pytest.fixture
def fake_popen():
    """Replace subprocess.Popen on the _watch module with a recorder."""
    fake = _FakePopen(lines=[""])
    original = watch_mod.subprocess.Popen
    watch_mod.subprocess.Popen = fake
    try:
        yield fake
    finally:
        watch_mod.subprocess.Popen = original


@pytest.fixture
def project_with_compile_script(tmp_path):
    """Project dir containing a compile script."""
    compile_script = tmp_path / "compile"
    compile_script.write_text("#!/bin/bash\necho 'compiling'")
    return tmp_path


class _CallbackRecorder:
    """Records callback invocations, optionally raising."""

    def __init__(self, raise_exc=None):
        self.call_count = 0
        self.raise_exc = raise_exc

    def __call__(self):
        self.call_count += 1
        if self.raise_exc is not None:
            raise self.raise_exc


class TestWatchManuscriptCompileScript:
    """Tests for watch_manuscript compile script handling."""

    def test_does_not_invoke_popen_when_script_missing(self, tmp_path, fake_popen):
        """Verify Popen is not called when compile script doesn't exist."""
        # Arrange
        # tmp_path has no compile script
        # Act
        watch_manuscript(tmp_path)
        # Assert
        assert fake_popen.last_args is None

    def test_creates_correct_command_for_watch_mode(
        self, project_with_compile_script, fake_popen
    ):
        """Verify correct command is built for watch mode."""
        # Arrange
        expected_cmd = [
            str(project_with_compile_script / "compile"),
            "-m",
            "-w",
        ]
        # Act
        watch_manuscript(project_with_compile_script)
        # Assert
        assert fake_popen.last_args[0] == expected_cmd


class TestWatchManuscriptProcess:
    """Tests for watch_manuscript process handling."""

    def test_runs_popen_with_project_dir_as_cwd(
        self, project_with_compile_script, fake_popen
    ):
        """Verify Popen receives the project dir as cwd."""
        # Arrange
        # fake_popen replaces subprocess.Popen
        # Act
        watch_manuscript(project_with_compile_script)
        # Assert
        assert fake_popen.last_kwargs["cwd"] == project_with_compile_script

    def test_runs_popen_with_pipe_stdout(self, project_with_compile_script, fake_popen):
        """Verify Popen routes stdout through a pipe."""
        # Arrange
        # fake_popen replaces subprocess.Popen
        # Act
        watch_manuscript(project_with_compile_script)
        # Assert
        assert fake_popen.last_kwargs["stdout"] == subprocess.PIPE

    def test_runs_popen_with_stderr_redirected_to_stdout(
        self, project_with_compile_script, fake_popen
    ):
        """Verify Popen redirects stderr to stdout."""
        # Arrange
        # fake_popen replaces subprocess.Popen
        # Act
        watch_manuscript(project_with_compile_script)
        # Assert
        assert fake_popen.last_kwargs["stderr"] == subprocess.STDOUT

    def test_runs_popen_with_text_mode_enabled(
        self, project_with_compile_script, fake_popen
    ):
        """Verify Popen runs in text mode."""
        # Arrange
        # fake_popen replaces subprocess.Popen
        # Act
        watch_manuscript(project_with_compile_script)
        # Assert
        assert fake_popen.last_kwargs["text"] is True

    def test_runs_popen_with_line_buffering(
        self, project_with_compile_script, fake_popen
    ):
        """Verify Popen uses line-buffered output."""
        # Arrange
        # fake_popen replaces subprocess.Popen
        # Act
        watch_manuscript(project_with_compile_script)
        # Assert
        assert fake_popen.last_kwargs["bufsize"] == 1

    def test_waits_for_process_completion_with_supplied_timeout(
        self, project_with_compile_script, fake_popen
    ):
        """Verify process.wait is invoked with the supplied timeout."""
        # Arrange
        # fake_popen replaces subprocess.Popen
        # Act
        watch_manuscript(project_with_compile_script, timeout=30)
        # Assert
        assert fake_popen.wait_calls == [30]


class TestWatchManuscriptCallback:
    """Tests for watch_manuscript callback handling."""

    def test_invokes_callback_on_compilation_event(
        self, project_with_compile_script, fake_popen
    ):
        """Verify callback is called when 'Compilation' appears in output."""
        # Arrange
        fake_popen.stdout = _FakeStdout(["Starting...\n", "Compilation complete\n", ""])
        callback = _CallbackRecorder()
        # Act
        watch_manuscript(project_with_compile_script, on_compile=callback)
        # Assert
        assert callback.call_count == 1

    def test_does_not_invoke_callback_without_compilation_keyword(
        self, project_with_compile_script, fake_popen
    ):
        """Verify callback is not called for non-compilation output."""
        # Arrange
        fake_popen.stdout = _FakeStdout(["Starting...\n", "Processing files...\n", ""])
        callback = _CallbackRecorder()
        # Act
        watch_manuscript(project_with_compile_script, on_compile=callback)
        # Assert
        assert callback.call_count == 0

    def test_callback_error_does_not_abort_watch_loop(
        self, project_with_compile_script, fake_popen
    ):
        """Verify watch_manuscript returns normally if callback raises."""
        # Arrange
        fake_popen.stdout = _FakeStdout(["Compilation complete\n", ""])
        callback = _CallbackRecorder(raise_exc=Exception("Callback failed"))
        # Act
        watch_manuscript(project_with_compile_script, on_compile=callback)
        # Assert
        assert callback.call_count == 1


class TestWatchManuscriptExceptions:
    """Tests for watch_manuscript exception handling."""

    def test_keyboard_interrupt_terminates_process(
        self, project_with_compile_script, fake_popen
    ):
        """Verify KeyboardInterrupt triggers process.terminate()."""
        # Arrange
        fake_popen.stdout = _FakeStdout(side_effect=KeyboardInterrupt())
        # Act
        watch_manuscript(project_with_compile_script)
        # Assert
        assert fake_popen.terminate_calls == 1

    def test_generic_runtime_error_terminates_process(
        self, project_with_compile_script, fake_popen
    ):
        """Verify generic exceptions trigger process.terminate()."""
        # Arrange
        fake_popen.stdout = _FakeStdout(side_effect=RuntimeError("Connection lost"))
        # Act
        watch_manuscript(project_with_compile_script)
        # Assert
        assert fake_popen.terminate_calls == 1


class TestWatchManuscriptParameters:
    """Tests for watch_manuscript parameter defaults."""

    def test_runs_without_explicit_interval_argument(
        self, project_with_compile_script, fake_popen
    ):
        """Verify watch_manuscript runs without an explicit interval argument."""
        # Arrange
        # fake_popen replaces subprocess.Popen
        # Act
        watch_manuscript(project_with_compile_script)
        # Assert
        assert fake_popen.wait_calls == [None]

    def test_timeout_defaults_to_none_in_wait_call(
        self, project_with_compile_script, fake_popen
    ):
        """Verify timeout defaults to None when not supplied."""
        # Arrange
        # fake_popen replaces subprocess.Popen
        # Act
        watch_manuscript(project_with_compile_script)
        # Assert
        assert fake_popen.wait_calls == [None]


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
