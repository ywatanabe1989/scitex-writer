"""Canonical MCP server entry — re-exports from scitex_writer._server.

The ecosystem-wide audit (`scitex-dev ecosystem audit-mcp-tools`) probes
`<pkg>._mcp_server.mcp` to find each peer's FastMCP instance. The actual
implementation has lived at `scitex_writer._server` since the early
`_server.py` days; this shim aligns the import path with the audit
contract without forcing a file move that would churn callers.
"""

from __future__ import annotations

from ._server import mcp, run_server

__all__ = ["mcp", "run_server"]
