#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: src/scitex_writer/__init__.py

"""SciTeX Writer - LaTeX manuscript compilation system with MCP server."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("scitex-writer")
except PackageNotFoundError:
    __version__ = "3.0.0"  # fallback for development

__all__ = ["__version__"]

# EOF
