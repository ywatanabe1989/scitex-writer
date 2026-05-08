"""Smoke test: `scitex_writer.export._arxiv_packager` imports cleanly."""
import importlib


def test_module_imports():
    importlib.import_module("scitex_writer.export._arxiv_packager")
