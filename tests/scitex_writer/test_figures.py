"""Smoke test: `scitex_writer.figures` imports cleanly."""

import importlib


def test_module_exposes_convert():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer.figures")
    # Assert
    assert hasattr(module, "convert")
