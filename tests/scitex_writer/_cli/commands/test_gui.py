#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: src/scitex_writer/_cli/commands/gui.py

"""Tests for the `scitex-writer gui` command group (real Click invocation)."""

import json

import pytest
from click.testing import CliRunner

from scitex_writer._cli._core import _TOP_RENAMES, main_group
from scitex_writer._cli.commands.gui import gui_group
from scitex_writer._core import _gui_runtime


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def isolated_state(tmp_path, monkeypatch):
    state_file = tmp_path / "gui.json"
    monkeypatch.setattr(_gui_runtime, "state_path", lambda: state_file)
    return state_file


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
