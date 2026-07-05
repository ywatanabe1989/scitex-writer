"""Smoke test: `scitex_writer._cli.commands.bib` imports cleanly."""

import importlib


def test_module_exposes_bib_group():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.bib")
    # Assert
    assert hasattr(module, "bib_group")


def test_bib_group_has_expected_subcommands():
    # Arrange
    from scitex_writer._cli.commands.bib import bib_group

    # Act
    names = set(bib_group.commands.keys())
    # Assert
    assert {"list-files", "list-entries", "get", "add", "remove", "merge"} <= names
