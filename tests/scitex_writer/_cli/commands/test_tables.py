"""Smoke test: `scitex_writer._cli.commands.tables` imports cleanly."""

import importlib


def test_module_exposes_tables_group():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.tables")
    # Assert
    assert hasattr(module, "tables_group")


def test_tables_group_has_expected_subcommands():
    # Arrange
    from scitex_writer._cli.commands.tables import tables_group

    # Act
    names = set(tables_group.commands.keys())
    # Assert
    assert {"list", "add", "remove", "archive"} <= names
