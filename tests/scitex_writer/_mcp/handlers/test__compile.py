"""Smoke test: `scitex_writer._mcp.handlers._compile` imports cleanly."""

import importlib


def test_module_exposes_compile_manuscript():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._mcp.handlers._compile")
    # Assert
    assert hasattr(module, "compile_manuscript")
