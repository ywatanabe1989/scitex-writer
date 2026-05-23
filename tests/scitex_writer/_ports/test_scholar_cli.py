#!/usr/bin/env python3
"""Tests for scholar CLI shell-out helpers."""

from __future__ import annotations

from pathlib import Path

from scitex_writer._ports import scholar_cli


def test_on_path_true_when_which_finds_the_binary():
    # Arrange
    which = lambda _name: "/usr/bin/stub"  # noqa: E731 - tiny injected fake
    module_check = lambda: False  # noqa: E731
    # Act
    result = scholar_cli.scholar_cli_on_path(which=which, module_check=module_check)
    # Assert
    assert result is True


def test_on_path_falls_back_to_python_module_when_binary_absent():
    # Arrange
    which = lambda _name: None  # noqa: E731 - binary not on PATH
    module_check = lambda: True  # noqa: E731 - module importable
    # Act
    result = scholar_cli.scholar_cli_on_path(which=which, module_check=module_check)
    # Assert
    assert result is True


def test_on_path_false_when_neither_binary_nor_module_present():
    # Arrange
    which = lambda _name: None  # noqa: E731
    module_check = lambda: False  # noqa: E731
    # Act
    result = scholar_cli.scholar_cli_on_path(which=which, module_check=module_check)
    # Assert
    assert result is False


def test_enrich_bib_without_cli_reports_failure():
    # Arrange
    cli_available = lambda: False  # noqa: E731 - scholar not installed
    # Act
    ok, _msg = scholar_cli.enrich_bib(
        Path("/tmp/x.bib"), "proj", cli_available=cli_available
    )
    # Assert
    assert ok is False


def test_enrich_bib_without_cli_message_points_at_pip_install():
    # Arrange
    cli_available = lambda: False  # noqa: E731
    # Act
    _ok, msg = scholar_cli.enrich_bib(
        Path("/tmp/x.bib"), "proj", cli_available=cli_available
    )
    # Assert
    assert "pip install" in msg
