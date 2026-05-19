"""Smoke test: `scitex_writer._mcp.handlers._update._handler` imports cleanly."""

import importlib


def test_module_imports_calls_import_module():
    # Arrange
    # Act
    # Assert
    importlib.import_module("scitex_writer._mcp.handlers._update._handler")
