"""Smoke test: `scitex_writer._cli.commands.checks` imports cleanly."""

import importlib


def test_module_exposes_check_limits_cmd():
    # Arrange
    # Act
    module = importlib.import_module("scitex_writer._cli.commands.checks")
    # Assert
    assert hasattr(module, "check_limits_cmd")


def test_module_exposes_all_check_commands():
    # Arrange
    module = importlib.import_module("scitex_writer._cli.commands.checks")
    expected = {
        "check_limits_cmd",
        "check_overflow_cmd",
        "check_paper_symlink_cmd",
        "check_references_cmd",
    }
    # Act
    present = {name for name in expected if hasattr(module, name)}
    # Assert
    assert present == expected
