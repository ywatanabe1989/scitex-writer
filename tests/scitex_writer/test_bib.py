"""Smoke test: `scitex_writer.bib` imports cleanly."""

import importlib


def test_module_imports():
    importlib.import_module("scitex_writer.bib")
