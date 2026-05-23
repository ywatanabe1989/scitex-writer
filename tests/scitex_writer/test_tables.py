"""Smoke test: `scitex_writer.tables` imports cleanly."""

import importlib


def test_module_exposes_csv_to_latex():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer.tables")
    # Assert
    assert hasattr(module, "csv_to_latex")
