"""Smoke test: `scitex_writer._cli.commands.migration` imports cleanly."""

import importlib


def test_module_exposes_migration_group():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.migration")
    # Assert
    assert hasattr(module, "migration_group")


def test_migration_group_has_expected_subcommands():
    # Arrange
    from scitex_writer._cli.commands.migration import migration_group

    # Act
    names = set(migration_group.commands.keys())
    # Assert
    assert {"import", "export"} <= names
