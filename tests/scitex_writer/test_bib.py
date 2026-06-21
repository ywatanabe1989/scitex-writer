"""Smoke test: `scitex_writer.bib` imports cleanly."""

import importlib


def test_module_exposes_merge():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer.bib")
    # Assert
    assert hasattr(module, "merge")
