"""Smoke test: `scitex_writer._cli.commands.export` imports cleanly."""

import importlib


def test_module_exposes_export_group():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.export")
    # Assert
    assert hasattr(module, "export_group")


def test_export_group_has_manuscript_subcommand():
    # Arrange
    from scitex_writer._cli.commands.export import export_group

    # Act
    names = set(export_group.commands.keys())
    # Assert
    assert "manuscript" in names
