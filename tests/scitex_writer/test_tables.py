"""Smoke test: `scitex_writer.tables` imports cleanly."""
import importlib


def test_module_imports():
    importlib.import_module("scitex_writer.tables")
