"""Smoke test: `scitex_writer._cli.commands.mcp` imports cleanly."""

import importlib


def test_module_exposes_mcp_group():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.mcp")
    # Assert
    assert hasattr(module, "mcp_group")


def test_mcp_group_has_expected_subcommands():
    # Arrange
    from scitex_writer._cli.commands.mcp import mcp_group

    # Act
    names = set(mcp_group.commands.keys())
    # Assert
    assert {"install", "list-tools", "doctor", "start"} <= names
