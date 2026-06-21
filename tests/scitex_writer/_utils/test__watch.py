#!/usr/bin/env python3
"""Tests for scitex_writer._utils._watch."""

import subprocess

from scitex_writer._utils._watch import watch_manuscript


class _FakeStdout:
    """Real iterable stdout stand-in driven by a fixed list of lines."""

    def __init__(self, lines):
        self._lines = list(lines)

    def readline(self):
        # iter(readline, "") stops at the first "" -> append "" to end.
        return self._lines.pop(0) if self._lines else ""


class _FakeProcess:
    """Hand-rolled stand-in for the subprocess.Popen object.

    Records terminate/kill/wait calls so tests can assert on them, and
    streams a fixed set of stdout lines. ``readline_raises`` lets a test
    drive the KeyboardInterrupt / generic-exception code paths.
    """

    def __init__(self, lines=None, readline_raises=None):
        if readline_raises is not None:
            self.stdout = _RaisingStdout(readline_raises)
        else:
            self.stdout = _FakeStdout((lines or []) + [""])
        self.wait_calls = []
        self.terminate_count = 0
        self.kill_count = 0

    def wait(self, timeout=None):
        self.wait_calls.append(timeout)

    def terminate(self):
        self.terminate_count += 1

    def kill(self):
        self.kill_count += 1


class _RaisingStdout:
    def __init__(self, exc):
        self._exc = exc

    def readline(self):
        raise self._exc


class _RecordingPopen:
    """Real callable matching subprocess.Popen's call shape.

    Records the positional command and keyword settings, and returns a
    pre-seeded _FakeProcess. Injected via the watch_manuscript ``popen=``
    seam — no patching of subprocess.Popen.
    """

    def __init__(self, process):
        self._process = process
        self.calls = []

    def __call__(self, cmd, **kwargs):
        self.calls.append((cmd, kwargs))
        return self._process


def _make_compile_script(tmp_path):
    compile_script = tmp_path / "compile"
    compile_script.write_text("#!/bin/bash\necho 'compiling'")
    return compile_script


class TestWatchManuscriptCompileScript:
    """Tests for watch_manuscript compile script handling."""

    def test_does_not_launch_process_when_compile_script_missing(self, tmp_path):
        # Arrange
        popen = _RecordingPopen(_FakeProcess())
        # Act
        watch_manuscript(tmp_path, popen=popen)
        # Assert
        assert popen.calls == []

    def test_builds_watch_command_from_compile_script(self, tmp_path):
        # Arrange
        compile_script = _make_compile_script(tmp_path)
        popen = _RecordingPopen(_FakeProcess())
        # Act
        watch_manuscript(tmp_path, popen=popen)
        # Assert
        assert popen.calls[0][0] == [str(compile_script), "-m", "-w"]


class TestWatchManuscriptProcess:
    """Tests for watch_manuscript process handling."""

    def test_runs_process_in_project_dir(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        popen = _RecordingPopen(_FakeProcess())
        # Act
        watch_manuscript(tmp_path, popen=popen)
        # Assert
        assert popen.calls[0][1]["cwd"] == tmp_path

    def test_runs_process_capturing_stdout_pipe(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        popen = _RecordingPopen(_FakeProcess())
        # Act
        watch_manuscript(tmp_path, popen=popen)
        # Assert
        assert popen.calls[0][1]["stdout"] == subprocess.PIPE

    def test_runs_process_merging_stderr_into_stdout(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        popen = _RecordingPopen(_FakeProcess())
        # Act
        watch_manuscript(tmp_path, popen=popen)
        # Assert
        assert popen.calls[0][1]["stderr"] == subprocess.STDOUT

    def test_runs_process_in_text_mode(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        popen = _RecordingPopen(_FakeProcess())
        # Act
        watch_manuscript(tmp_path, popen=popen)
        # Assert
        assert popen.calls[0][1]["text"] is True

    def test_runs_process_line_buffered(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        popen = _RecordingPopen(_FakeProcess())
        # Act
        watch_manuscript(tmp_path, popen=popen)
        # Assert
        assert popen.calls[0][1]["bufsize"] == 1

    def test_waits_for_process_with_supplied_timeout(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        process = _FakeProcess()
        popen = _RecordingPopen(process)
        # Act
        watch_manuscript(tmp_path, timeout=30, popen=popen)
        # Assert
        assert process.wait_calls == [30]


class TestWatchManuscriptCallback:
    """Tests for watch_manuscript callback handling."""

    def test_callback_fires_once_on_compilation_line(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        process = _FakeProcess(["Starting...\n", "Compilation complete\n"])
        popen = _RecordingPopen(process)
        calls = []
        # Act
        watch_manuscript(tmp_path, on_compile=lambda: calls.append(1), popen=popen)
        # Assert
        assert calls == [1]

    def test_callback_not_fired_without_compilation_line(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        process = _FakeProcess(["Starting...\n", "Processing files...\n"])
        popen = _RecordingPopen(process)
        calls = []
        # Act
        watch_manuscript(tmp_path, on_compile=lambda: calls.append(1), popen=popen)
        # Assert
        assert calls == []

    def test_callback_exception_does_not_propagate(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        process = _FakeProcess(["Compilation complete\n"])
        popen = _RecordingPopen(process)

        def _boom():
            raise RuntimeError("Callback failed")

        completed = False
        # Act
        watch_manuscript(tmp_path, on_compile=_boom, popen=popen)
        completed = True
        # Assert
        assert completed is True


class TestWatchManuscriptExceptions:
    """Tests for watch_manuscript exception handling."""

    def test_keyboard_interrupt_terminates_process(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        process = _FakeProcess(readline_raises=KeyboardInterrupt())
        popen = _RecordingPopen(process)
        # Act
        watch_manuscript(tmp_path, popen=popen)
        # Assert
        assert process.terminate_count == 1

    def test_generic_exception_terminates_process(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        process = _FakeProcess(readline_raises=RuntimeError("Connection lost"))
        popen = _RecordingPopen(process)
        # Act
        watch_manuscript(tmp_path, popen=popen)
        # Assert
        assert process.terminate_count == 1


class TestWatchManuscriptParameters:
    """Tests for watch_manuscript parameter defaults."""

    def test_runs_with_default_parameters(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        process = _FakeProcess()
        popen = _RecordingPopen(process)
        # Act
        watch_manuscript(tmp_path, popen=popen)
        # Assert
        assert len(popen.calls) == 1

    def test_default_timeout_is_none(self, tmp_path):
        # Arrange
        _make_compile_script(tmp_path)
        process = _FakeProcess()
        popen = _RecordingPopen(process)
        # Act
        watch_manuscript(tmp_path, popen=popen)
        # Assert
        assert process.wait_calls == [None]


if __name__ == "__main__":
    import os

    import pytest

    pytest.main([os.path.abspath(__file__)])
