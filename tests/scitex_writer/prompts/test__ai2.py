"""Smoke test: `scitex_writer.prompts._ai2` imports cleanly."""

import importlib


def test_module_exposes_generate_ai2_prompt():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer.prompts._ai2")
    # Assert
    assert hasattr(module, "generate_ai2_prompt")
