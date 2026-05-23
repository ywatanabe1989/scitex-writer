"""Smoke test: `scitex_writer._cli` imports cleanly."""

import importlib


def test_module_exposes_bib_group():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli")
    # Assert
    assert hasattr(module, "bib_group")
