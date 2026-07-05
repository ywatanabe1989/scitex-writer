"""Smoke test: `scitex_writer._cli.commands.prompts` imports cleanly."""

import importlib


def test_module_exposes_prompts_group():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.prompts")
    # Assert
    assert hasattr(module, "prompts_group")


def test_prompts_group_has_show_asta_subcommand():
    # Arrange
    from scitex_writer._cli.commands.prompts import prompts_group

    # Act
    names = set(prompts_group.commands.keys())
    # Assert
    assert "show-asta" in names
