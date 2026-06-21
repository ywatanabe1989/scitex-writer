"""Smoke test: `scitex_writer._server` imports cleanly."""

import importlib


def test_module_exposes_register_all_tools():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._server")
    # Assert
    assert hasattr(module, "register_all_tools")
