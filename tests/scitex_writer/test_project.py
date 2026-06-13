"""Smoke test: `scitex_writer.project` imports cleanly."""

import importlib


def test_project_module_imports_without_error():
    """Smoke: target module imports without error and is not None."""
    # Arrange
    target = "scitex_writer.project"
    # Act
    module = importlib.import_module(target)
    # Assert
    assert module is not None
