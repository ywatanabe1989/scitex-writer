"""Smoke test: `scitex_writer._cli.commands.gui` imports cleanly."""

import importlib


def test_module_exposes_launch_gui():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.gui")
    # Assert
    assert hasattr(module, "launch_gui")
