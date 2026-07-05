"""Smoke test: `scitex_writer._cli.commands.figures` imports cleanly."""

import importlib


def test_module_exposes_figures_group():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.figures")
    # Assert
    assert hasattr(module, "figures_group")


def test_figures_group_has_expected_subcommands():
    # Arrange
    from scitex_writer._cli.commands.figures import figures_group

    # Act
    names = set(figures_group.commands.keys())
    # Assert
    assert {"list", "add", "remove", "archive"} <= names
