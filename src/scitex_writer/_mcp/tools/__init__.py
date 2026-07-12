#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_mcp/tools/__init__.py

"""MCP tool registration for SciTeX Writer."""

from fastmcp import FastMCP


def register_all_tools(mcp: FastMCP) -> None:
    """Register all MCP tools with the server."""
    from . import (
        archive,
        bib,
        checks,
        citation_style,
        claim,
        cleanup,
        compile,
        diff,
        export,
        figures,
        guidelines,
        migration,
        project,
        prompts,
        skills,
        tables,
        update,
        wordcount,
    )

    # Register tools from each module
    project.register_tools(mcp)
    compile.register_tools(mcp)
    export.register_tools(mcp)
    tables.register_tools(mcp)
    figures.register_tools(mcp)
    diff.register_tools(mcp)
    archive.register_tools(mcp)
    bib.register_tools(mcp)
    guidelines.register_tools(mcp)
    prompts.register_tools(mcp)
    claim.register_tools(mcp)
    citation_style.register_tools(mcp)
    cleanup.register_tools(mcp)
    update.register_tools(mcp)
    migration.register_tools(mcp)
    skills.register_tools(mcp)
    checks.register_tools(mcp)
    wordcount.register_tools(mcp)


__all__ = ["register_all_tools"]

# EOF
