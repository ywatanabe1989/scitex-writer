"""Smoke test: `scitex_writer._dataclasses.contents._ManuscriptContents` imports cleanly."""

import importlib


def test_module_exposes_manuscript_contents():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._dataclasses.contents._ManuscriptContents")
    # Assert
    assert hasattr(module, "ManuscriptContents")
