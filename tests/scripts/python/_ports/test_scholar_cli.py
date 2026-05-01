#!/usr/bin/env python3
"""Tests for scholar CLI shell-out helpers."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

from scitex_writer._ports import scholar_cli


def test_scholar_cli_on_path_checks_which_first():
    with mock.patch.object(scholar_cli.shutil, "which", return_value="/usr/bin/stub"):
        assert scholar_cli.scholar_cli_on_path() is True


def test_scholar_cli_falls_back_to_python_module():
    with mock.patch.object(scholar_cli.shutil, "which", return_value=None):
        # If scitex_scholar is importable, fallback succeeds
        if scholar_cli._python_module_available():
            assert scholar_cli.scholar_cli_on_path() is True
        else:
            assert scholar_cli.scholar_cli_on_path() is False


def test_enrich_bib_when_no_cli_returns_install_message():
    with (
        mock.patch.object(scholar_cli.shutil, "which", return_value=None),
        mock.patch.object(scholar_cli, "_python_module_available", return_value=False),
    ):
        ok, msg = scholar_cli.enrich_bib(Path("/tmp/x.bib"), "proj")
        assert ok is False
        assert "pip install" in msg
