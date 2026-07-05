"""Smoke test: `scitex_writer._cli.commands.project` imports cleanly."""

import importlib


def test_module_exposes_update_project():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.project")
    # Assert
    assert hasattr(module, "update_project")
