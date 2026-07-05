"""Smoke test: `scitex_writer._cli.commands.guidelines` imports cleanly."""

import importlib


def test_module_exposes_guidelines_group():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.guidelines")
    # Assert
    assert hasattr(module, "guidelines_group")


def test_guidelines_group_has_list_subcommand():
    # Arrange
    from scitex_writer._cli.commands.guidelines import guidelines_group

    # Act
    names = set(guidelines_group.commands.keys())
    # Assert
    assert "list" in names
