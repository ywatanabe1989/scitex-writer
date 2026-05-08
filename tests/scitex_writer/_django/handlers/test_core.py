"""Smoke test: `scitex_writer._django.handlers.core` imports cleanly."""

import importlib


def test_module_imports():
    importlib.import_module("scitex_writer._django.handlers.core")
