#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: src/scitex_writer/_core/_gui_runtime.py

"""Tests for the GUI runtime-state module (state file, pid checks, stop)."""

import os
import subprocess
import sys

import pytest

from scitex_writer._core import _gui_runtime


@pytest.fixture
def state_file(tmp_path):
    return tmp_path / "gui.json"


def test_read_state_missing_returns_none(state_file):
    # Arrange
    # (state_file is never created)
    # Act
    result = _gui_runtime.read_state(state_file)
    # Assert
    assert result is None


def test_read_state_corrupt_returns_none(state_file):
    # Arrange
    state_file.write_text("{not json")
    # Act
    result = _gui_runtime.read_state(state_file)
    # Assert
    assert result is None


def test_write_state_roundtrips_fields(state_file):
    # Arrange
    _gui_runtime.write_state(123, 5050, "127.0.0.1", "/proj", state_file)
    # Act
    state = _gui_runtime.read_state(state_file)
    # Assert
    assert (state["pid"], state["port"], state["host"], state["project"]) == (
        123,
        5050,
        "127.0.0.1",
        "/proj",
    )


def test_write_state_records_started_at(state_file):
    # Arrange
    _gui_runtime.write_state(123, 5050, "127.0.0.1", "/proj", state_file)
    # Act
    state = _gui_runtime.read_state(state_file)
    # Assert
    assert state["started_at"]


def test_clear_state_is_idempotent(state_file):
    # Arrange
    _gui_runtime.clear_state(state_file)
    # Act
    _gui_runtime.clear_state(state_file)
    # Assert
    assert not state_file.exists()


def test_pid_alive_true_for_own_process():
    # Arrange
    pid = os.getpid()
    # Act
    alive = _gui_runtime.pid_alive(pid)
    # Assert
    assert alive


def test_pid_alive_false_for_invalid_pid():
    # Arrange
    pid = -1
    # Act
    alive = _gui_runtime.pid_alive(pid)
    # Assert
    assert not alive


def test_pid_alive_false_for_exited_child():
    # Arrange
    child = subprocess.Popen([sys.executable, "-c", ""])
    child.wait()
    # Act
    alive = _gui_runtime.pid_alive(child.pid)
    # Assert
    assert not alive


def test_status_missing_state_reports_not_running(state_file):
    # Arrange
    # (state_file is never created)
    # Act
    result = _gui_runtime.status(state_file)
    # Assert
    assert result == {"running": False}


def test_status_live_pid_reports_running_url(state_file):
    # Arrange
    _gui_runtime.write_state(os.getpid(), 5050, "127.0.0.1", "/proj", state_file)
    # Act
    result = _gui_runtime.status(state_file)
    # Assert
    assert result["url"] == "http://127.0.0.1:5050"


def test_status_dead_pid_self_heals_state(state_file):
    # Arrange
    child = subprocess.Popen([sys.executable, "-c", ""])
    child.wait()
    _gui_runtime.write_state(child.pid, 5050, "127.0.0.1", "/proj", state_file)
    # Act
    result = _gui_runtime.status(state_file)
    # Assert
    assert result["stale_state_cleared"] and not state_file.exists()


def test_stop_without_state_is_idempotent(state_file):
    # Arrange
    # (state_file is never created)
    # Act
    result = _gui_runtime.stop(state_file)
    # Assert
    assert result == {"stopped": False, "running": False}


def test_stop_terminates_recorded_process(state_file):
    # Arrange
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    _gui_runtime.write_state(child.pid, 5050, "127.0.0.1", "/proj", state_file)
    # Act
    result = _gui_runtime.stop(state_file, timeout=5.0)
    child.wait(timeout=5)
    # Assert
    assert result["stopped"] and result["terminated"]


def test_stop_clears_state_file(state_file):
    # Arrange
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    _gui_runtime.write_state(child.pid, 5050, "127.0.0.1", "/proj", state_file)
    # Act
    _gui_runtime.stop(state_file, timeout=5.0)
    child.wait(timeout=5)
    # Assert
    assert not state_file.exists()
