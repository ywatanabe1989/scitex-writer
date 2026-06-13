"""Smoke test: `scitex_writer.writer` imports cleanly."""

import importlib


def test_writer_module_imports_without_error():
    """Smoke: target module imports without error and is not None."""
    # Arrange
    target = "scitex_writer.writer"
    # Act
    module = importlib.import_module(target)
    # Assert
    assert module is not None
