"""Smoke test: `scitex_writer.migration._overleaf_export` imports cleanly."""

import importlib


def test_module_exposes_to_overleaf():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer.migration._overleaf_export")
    # Assert
    assert hasattr(module, "to_overleaf")
