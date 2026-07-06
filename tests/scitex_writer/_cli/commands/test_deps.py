#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: src/scitex_writer/_cli/commands/deps.py

"""Tests for the `scitex-writer deps` CLI command (real Click invocation)."""

import importlib
import json

import pytest
from click.testing import CliRunner

from scitex_writer._cli._core import main_group
from scitex_writer._core._system_deps import APT_PACKAGES


@pytest.fixture
def runner():
    return CliRunner()


def test_module_exposes_deps_cmd():
    # Arrange
    name = "scitex_writer._cli.commands.deps"
    # Act
    module = importlib.import_module(name)
    # Assert
    assert hasattr(module, "deps_cmd")


def test_deps_registered_on_main_group():
    # Arrange
    commands = main_group.commands
    # Act
    present = "deps" in commands
    # Assert
    assert present


def test_deps_default_exits_zero(runner):
    # Arrange
    args = ["deps"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert result.exit_code == 0


def test_deps_default_prints_one_package_per_line(runner):
    # Arrange
    args = ["deps"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert result.output.splitlines() == APT_PACKAGES


def test_deps_apt_exits_zero(runner):
    # Arrange
    args = ["deps", "--apt"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert result.exit_code == 0


def test_deps_apt_starts_with_apt_get_install(runner):
    # Arrange
    args = ["deps", "--apt"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert result.output.strip().startswith(
        "apt-get install -y --no-install-recommends "
    )


def test_deps_apt_contains_every_package(runner):
    # Arrange
    args = ["deps", "--apt"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert all(pkg in result.output for pkg in APT_PACKAGES)


def test_deps_apt_has_core_latex(runner):
    # Arrange
    args = ["deps", "--apt"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert "texlive-latex-base" in result.output


def test_deps_apt_has_parallel(runner):
    # Arrange
    args = ["deps", "--apt"]
    # Act
    result = runner.invoke(main_group, args)
    # Assert
    assert "parallel" in result.output


def test_deps_json_lists_packages_in_order(runner):
    # Arrange
    args = ["deps", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    payload = json.loads(result.output)
    # Assert
    assert [row["package"] for row in payload] == APT_PACKAGES


def test_deps_json_tags_every_row_with_writer_provider(runner):
    # Arrange
    args = ["deps", "--json"]
    # Act
    result = runner.invoke(main_group, args)
    payload = json.loads(result.output)
    # Assert
    assert all(row["provider"] == "scitex-writer" for row in payload)
