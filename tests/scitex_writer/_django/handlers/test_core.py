"""Smoke test: `scitex_writer._django.handlers.core` imports cleanly."""

import importlib


def test_module_exposes_handle_ping():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._django.handlers.core")
    # Assert
    assert hasattr(module, "handle_ping")
