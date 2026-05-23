"""Smoke test: `scitex_writer.writer` imports cleanly."""

import importlib


def test_module_exposes_manuscript_tree():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer.writer")
    # Assert
    assert hasattr(module, "ManuscriptTree")
