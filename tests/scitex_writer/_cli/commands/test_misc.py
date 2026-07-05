"""Smoke test: `scitex_writer._cli.commands.misc` imports cleanly."""

import importlib


def test_module_exposes_list_python_apis():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.misc")
    # Assert
    assert hasattr(module, "list_python_apis")


def test_module_exposes_show_usage():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.misc")
    # Assert
    assert hasattr(module, "show_usage")
