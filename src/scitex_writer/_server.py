#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_server.py

"""
MCP server for SciTeX Writer - LaTeX manuscript compilation system.

This is the main server entry point. Tools are organized in _mcp/tools/.
"""

from __future__ import annotations

from fastmcp import FastMCP

from ._branding import get_mcp_instructions, get_mcp_server_name
from ._mcp.tools import register_all_tools

# =============================================================================
# FastMCP Server (with branding support)
# =============================================================================

mcp = FastMCP(name=get_mcp_server_name(), instructions=get_mcp_instructions())


@mcp.tool()
def usage() -> str:
    """[writer] Get usage guide for SciTeX Writer LaTeX manuscript compilation system."""
    return get_mcp_instructions()


# Register all tools from modules
register_all_tools(mcp)


# =============================================================================
# Server Entry Point
# =============================================================================


def run_server(transport: str = "stdio") -> None:
    """Run the MCP server."""
    mcp.run(transport=transport)


if __name__ == "__main__":
    run_server()

# EOF
