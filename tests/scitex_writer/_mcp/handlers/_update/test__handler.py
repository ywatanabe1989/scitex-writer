"""Smoke test: `scitex_writer._mcp.handlers._update._handler` imports cleanly."""

import importlib


def test_module_exposes_collect_sync_files():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._mcp.handlers._update._handler")
    # Assert
    assert hasattr(module, "collect_sync_files")
