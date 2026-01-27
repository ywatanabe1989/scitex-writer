#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: src/scitex_writer/_mcp/__init__.py

"""
SciTeX Writer MCP module.

Re-exports from _server.py.
"""

from scitex_writer._server import mcp, run_server

__all__ = [
    "mcp",
    "run_server",
]

# EOF
