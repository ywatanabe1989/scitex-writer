#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_mcp/tools/__init__.py

"""MCP tool registration for SciTeX Writer."""

from __future__ import annotations

from fastmcp import FastMCP


def register_all_tools(mcp: FastMCP) -> None:
    """Register all MCP tools with the server."""
    from . import bib, compile, figures, guidelines, project, prompts, tables

    # Register tools from each module
    project.register_tools(mcp)
    compile.register_tools(mcp)
    tables.register_tools(mcp)
    figures.register_tools(mcp)
    bib.register_tools(mcp)
    guidelines.register_tools(mcp)
    prompts.register_tools(mcp)


__all__ = ["register_all_tools"]

# EOF
