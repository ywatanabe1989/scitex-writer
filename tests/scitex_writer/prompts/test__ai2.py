"""Smoke test: `scitex_writer.prompts._ai2` imports cleanly."""

import importlib


def test_module_imports_calls_import_module():
    # Arrange
    # Act
    # Assert
    importlib.import_module("scitex_writer.prompts._ai2")
