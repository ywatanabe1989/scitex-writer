"""Smoke test: `scitex_writer.export._arxiv_packager` imports cleanly."""

import importlib


def test_module_exposes_package_submission():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer.export._arxiv_packager")
    # Assert
    assert hasattr(module, "package_submission")
