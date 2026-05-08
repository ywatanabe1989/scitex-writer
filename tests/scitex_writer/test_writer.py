"""Smoke test: `scitex_writer.writer` imports cleanly."""
import importlib


def test_module_imports():
    importlib.import_module("scitex_writer.writer")
