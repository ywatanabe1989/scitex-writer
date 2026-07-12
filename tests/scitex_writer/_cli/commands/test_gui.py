#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: src/scitex_writer/_cli/commands/gui.py

"""Tests for the `scitex-writer gui` command group (real Click invocation)."""

import json
import os
import socket
import subprocess
import sys

import pytest
from click.testing import CliRunner

from scitex_writer._cli._core import _TOP_RENAMES, main_group
from scitex_writer._cli.commands.gui import gui_group
from scitex_writer._core import _gui_runtime


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def isolated_state(tmp_path):
    state_file = tmp_path / "gui.json"
    os.environ["SCITEX_WRITER_GUI_STATE"] = str(state_file)
    yield state_file
    os.environ.pop("SCITEX_WRITER_GUI_STATE", None)


@pytest.fixture
def held_port():
    """Bind a real listening socket and yield the port it holds."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    try:
        yield sock.getsockname()[1]
    finally:
        sock.close()


@pytest.fixture
def live_pid():
    """A real, live child process whose pid can stand in for a running server."""
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    try:
        yield child.pid
    finally:
        child.kill()
        child.wait()


@pytest.fixture
def dead_pid():
    """A pid of a real process that has already exited and been reaped."""
    child = subprocess.Popen([sys.executable, "-c", "pass"])
    child.wait()
    return child.pid


def _serve(state_file, project, *args):
    """Run `gui serve` as a real subprocess against an isolated state file."""
    env = dict(os.environ, SCITEX_WRITER_GUI_STATE=str(state_file))
    return subprocess.run(
        [sys.executable, "-m", "scitex_writer", "gui", "serve", str(project), *args],
        capture_output=True,
        text=True,
        timeout=60,
        env=env,
    )


def test_gui_group_registered_on_main_group():
    # Arrange
    commands = main_group.commands
    # Act
    present = "gui" in commands
    # Assert
    assert present


def test_gui_group_has_canonical_verbs():
    # Arrange
    verbs = set(gui_group.commands)
    # Act
    canonical = {"open", "serve", "status", "stop"}
    # Assert
    assert canonical <= verbs


def test_gui_not_rewritten_by_top_renames():
    # Arrange
    renames = _TOP_RENAMES
    # Act
    rewritten = "gui" in renames
    # Assert
    assert not rewritten


def test_launch_gui_alias_is_hidden():
    # Arrange
    command = main_group.commands["launch-gui"]
    # Act
    hidden = command.hidden
    # Assert
    assert hidden


def test_launch_gui_alias_warns_deprecated(runner):
    # Arrange
    args = ["launch-gui", "--dry-run"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert "deprecated" in result.output


def test_gui_open_dry_run_exits_zero(runner):
    # Arrange
    args = ["gui", "open", "--dry-run"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert result.exit_code == 0


def test_gui_open_dry_run_json_shape(runner):
    # Arrange
    args = ["gui", "open", "--dry-run", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    payload = json.loads(result.output)
    # Assert
    assert payload["would_open"]


def test_gui_serve_dry_run_exits_zero(runner):
    # Arrange
    args = ["gui", "serve", "--dry-run"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert result.exit_code == 0


def test_gui_serve_dry_run_json_shape(runner):
    # Arrange
    args = ["gui", "serve", "--dry-run", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    payload = json.loads(result.output)
    # Assert
    assert payload["would_serve"]


def test_gui_status_json_not_running(runner, isolated_state):
    # Arrange
    args = ["gui", "status", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    payload = json.loads(result.output)
    # Assert
    assert payload == {"running": False}


def test_gui_status_human_not_running(runner, isolated_state):
    # Arrange
    args = ["gui", "status"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert "Not running" in result.output


def test_gui_stop_json_idempotent(runner, isolated_state):
    # Arrange
    args = ["gui", "stop", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    payload = json.loads(result.output)
    # Assert
    assert payload == {"stopped": False, "running": False}


def test_gui_stop_dry_run_reports_would_stop(runner, isolated_state):
    # Arrange
    _gui_runtime.write_state(os.getpid(), 31298, "127.0.0.1", "/proj", isolated_state)
    args = ["gui", "stop", "--dry-run", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    payload = json.loads(result.output)
    # Assert
    assert payload["would_stop"]


def test_gui_stop_dry_run_leaves_server_state(runner, isolated_state):
    # Arrange
    _gui_runtime.write_state(os.getpid(), 31298, "127.0.0.1", "/proj", isolated_state)
    args = ["gui", "stop", "--dry-run"]
    # Act
    runner.invoke(main_group, args)
    # Assert
    assert isolated_state.exists()


def test_gui_stop_without_yes_refuses(runner, isolated_state):
    # Arrange
    _gui_runtime.write_state(os.getpid(), 31298, "127.0.0.1", "/proj", isolated_state)
    args = ["gui", "stop"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert "without --yes" in result.output and isolated_state.exists()


# =========================================================================
# Fixed port: bind exactly what was asked for, or fail loud
# =========================================================================


def test_gui_serve_default_port_is_fixed_slot(runner):
    # Arrange
    args = ["gui", "serve", "--dry-run", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    payload = json.loads(result.output)
    # Assert
    assert payload["port"] == 31298


def test_gui_open_default_port_is_fixed_slot(runner):
    # Arrange
    args = ["gui", "open", "--dry-run", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    payload = json.loads(result.output)
    # Assert
    assert payload["port"] == 31298


def test_gui_serve_fails_when_port_held(isolated_state, held_port, tmp_path):
    # Arrange
    project = tmp_path
    # Act
    result = _serve(isolated_state, project, "--port", str(held_port))
    # Assert
    assert result.returncode != 0 and "already in use" in result.stderr


def test_gui_serve_never_drifts_to_another_port(isolated_state, held_port, tmp_path):
    # Arrange
    project = tmp_path
    # Act
    _serve(isolated_state, project, "--port", str(held_port))
    # Assert
    assert not isolated_state.exists()


def test_gui_serve_refuses_second_running_instance(isolated_state, live_pid, tmp_path):
    # Arrange
    _gui_runtime.write_state(
        live_pid, 31298, "127.0.0.1", str(tmp_path), isolated_state
    )
    # Act
    result = _serve(isolated_state, tmp_path)
    # Assert
    assert result.returncode != 0 and "already running" in result.stderr


def test_gui_serve_names_running_instance_url(isolated_state, live_pid, tmp_path):
    # Arrange
    _gui_runtime.write_state(
        live_pid, 31298, "127.0.0.1", str(tmp_path), isolated_state
    )
    # Act
    result = _serve(isolated_state, tmp_path)
    # Assert
    assert "http://127.0.0.1:31298" in result.stderr


def test_gui_serve_proceeds_after_stale_state(
    isolated_state, dead_pid, held_port, tmp_path
):
    # Arrange — the recorded pid is really dead, so status() self-heals and
    # serving proceeds; the port guard is then what stops us, proving we got
    # past the state check rather than being blocked by the stale file.
    _gui_runtime.write_state(
        dead_pid, 31298, "127.0.0.1", str(tmp_path), isolated_state
    )
    # Act
    result = _serve(isolated_state, tmp_path, "--port", str(held_port))
    # Assert
    assert "already in use" in result.stderr
