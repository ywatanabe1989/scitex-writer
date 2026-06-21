"""Smoke test: `scitex_writer._cli.introspect` imports cleanly."""

import importlib


def test_module_exposes_cmd_list_python_apis():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.introspect")
    # Assert
    assert hasattr(module, "cmd_list_python_apis")
