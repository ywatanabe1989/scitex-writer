"""Smoke test: `scitex_writer.checks` imports cleanly."""
import importlib


def test_module_imports():
    importlib.import_module("scitex_writer.checks")
