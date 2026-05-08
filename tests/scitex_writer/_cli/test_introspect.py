"""Smoke test: `scitex_writer._cli.introspect` imports cleanly."""

import importlib


def test_module_imports():
    importlib.import_module("scitex_writer._cli.introspect")
