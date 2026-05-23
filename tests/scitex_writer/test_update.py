"""Smoke test: `scitex_writer.update` imports cleanly."""

import importlib


def test_module_exposes_project():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer.update")
    # Assert
    assert hasattr(module, "project")
