"""Smoke test: `scitex_writer.project` imports cleanly."""

import importlib


def test_module_exposes_clone():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer.project")
    # Assert
    assert hasattr(module, "clone")
