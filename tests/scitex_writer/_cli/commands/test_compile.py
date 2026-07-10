"""Smoke test: `scitex_writer._cli.commands.compile` imports cleanly."""

import importlib


def test_module_exposes_compile_group():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.compile")
    # Assert
    assert hasattr(module, "compile_group")


def test_compile_group_has_expected_subcommands():
    # Arrange
    from scitex_writer._cli.commands.compile import compile_group

    # Act
    names = set(compile_group.commands.keys())
    # Assert
    assert {"manuscript", "supplementary", "revision", "content"} <= names


def test_compile_group_is_visible_in_help():
    # Arrange
    from scitex_writer._cli.commands.compile import compile_group

    # Act
    hidden = compile_group.hidden
    # Assert
    assert hidden is False
