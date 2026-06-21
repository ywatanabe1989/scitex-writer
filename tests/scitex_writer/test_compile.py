"""Smoke test: `scitex_writer.compile` imports cleanly."""

import importlib


def test_module_exposes_manuscript():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer.compile")
    # Assert
    assert hasattr(module, "manuscript")
