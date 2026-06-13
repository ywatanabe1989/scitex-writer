#!/usr/bin/env python3
"""Tests for scholar CLI shell-out helpers."""

from __future__ import annotations

from pathlib import Path

import pytest

from scitex_writer._ports import scholar_cli


@pytest.fixture
def stub_which():
    """Replace shutil.which on the scholar_cli module; restore on teardown."""
    original = scholar_cli.shutil.which
    state = {"return": None}

    def _which(_name):
        return state["return"]

    scholar_cli.shutil.which = _which
    try:
        yield state
    finally:
        scholar_cli.shutil.which = original


@pytest.fixture
def stub_python_module():
    """Replace _python_module_available; restore on teardown."""
    original = scholar_cli._python_module_available
    state = {"return": False}

    def _avail():
        return state["return"]

    scholar_cli._python_module_available = _avail
    try:
        yield state
    finally:
        scholar_cli._python_module_available = original


def test_scholar_cli_on_path_returns_true_when_binary_present(stub_which):
    """Verify scholar_cli_on_path returns True when which() finds the binary."""
    # Arrange
    stub_which["return"] = "/usr/bin/stub"
    # Act
    result = scholar_cli.scholar_cli_on_path()
    # Assert
    assert result is True


def test_scholar_cli_on_path_falls_back_to_module_when_binary_missing(stub_which):
    """Verify the python-module fallback decides the result when which() is None."""
    # Arrange
    stub_which["return"] = None
    expected = scholar_cli._python_module_available()
    # Act
    result = scholar_cli.scholar_cli_on_path()
    # Assert
    assert result is expected


def test_enrich_bib_returns_false_when_cli_unavailable(stub_which, stub_python_module):
    """Verify enrich_bib returns ok=False when neither CLI nor module is available."""
    # Arrange
    stub_which["return"] = None
    stub_python_module["return"] = False
    # Act
    ok, _msg = scholar_cli.enrich_bib(Path("/tmp/x.bib"), "proj")
    # Assert
    assert ok is False


def test_enrich_bib_install_message_mentions_pip_install(
    stub_which, stub_python_module
):
    """Verify enrich_bib install hint mentions 'pip install' when no CLI."""
    # Arrange
    stub_which["return"] = None
    stub_python_module["return"] = False
    # Act
    _ok, msg = scholar_cli.enrich_bib(Path("/tmp/x.bib"), "proj")
    # Assert
    assert "pip install" in msg
