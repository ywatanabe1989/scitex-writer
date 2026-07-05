"""Smoke test: `scitex_writer._cli.commands.introspect` imports cleanly."""

import importlib


def test_module_exposes_introspect_group():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.introspect")
    # Assert
    assert hasattr(module, "introspect_group")


def test_introspect_group_has_show_api_subcommand():
    # Arrange
    from scitex_writer._cli.commands.introspect import introspect_group

    # Act
    names = set(introspect_group.commands.keys())
    # Assert
    assert "show-api" in names
