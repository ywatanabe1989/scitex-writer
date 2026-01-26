#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_cli.py

"""CLI entry point redirect.

The CLI implementation has been moved to the _cli/ package.
This file provides backward compatibility for the entry point.
"""

from ._cli import main

__all__ = ["main"]

# EOF
