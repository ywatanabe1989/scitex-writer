#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: src/scitex_writer/_cli/commands/engines.py

"""Tests for the `scitex-writer list-engines` CLI command (real Click invocation)."""

import importlib
import json

import pytest
from click.testing import CliRunner

from scitex_writer._cli._core import main_group


@pytest.fixture
def runner():
    return CliRunner()


def test_module_exposes_list_engines_cmd():
    # Arrange
    name = "scitex_writer._cli.commands.engines"
    # Act
    module = importlib.import_module(name)
    # Assert
    assert hasattr(module, "list_engines_cmd")


def test_engines_registered_on_main_group():
    # Arrange
    commands = main_group.commands
    # Act
    present = "list-engines" in commands
    # Assert
    assert present


def test_engines_default_exits_zero(runner):
    # Arrange
    args = ["list-engines"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert result.exit_code == 0


def test_engines_default_lists_all_three(runner):
    # Arrange
    args = ["list-engines"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert all(e in result.output for e in ("tectonic", "latexmk", "3pass"))


def test_engines_json_exits_zero(runner):
    # Arrange
    args = ["list-engines", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert result.exit_code == 0


def test_engines_json_lists_all_three_in_order(runner):
    # Arrange
    args = ["list-engines", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    payload = json.loads(result.output)
    # Assert
    assert [row["engine"] for row in payload] == ["tectonic", "latexmk", "3pass"]


def test_engines_json_rows_have_available_key(runner):
    # Arrange
    args = ["list-engines", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    payload = json.loads(result.output)
    # Assert
    assert all(isinstance(row["available"], bool) for row in payload)
