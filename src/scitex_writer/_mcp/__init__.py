#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: src/scitex_writer/_mcp/__init__.py

"""
SciTeX Writer MCP module.

Lazy re-exports from _server.py to avoid importing fastmcp
when only utility functions are needed (e.g., from Django).
"""


def __getattr__(name):
    if name in ("mcp", "run_server"):
        from scitex_writer._server import mcp, run_server

        globals()["mcp"] = mcp
        globals()["run_server"] = run_server
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "mcp",
    "run_server",
]

# EOF
