#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/tools/archive.py

"""Archive MCP tools (versioned snapshots of the compiled outputs)."""

from typing import Literal

from fastmcp import FastMCP

from ..handlers._archive_pipeline import process as _process


def register_tools(mcp: FastMCP) -> None:
    """Register archive tools."""

    # Named for its Python API (`sw.compile.archive`), not for the CLI leaf
    # (`scitex-writer archive create`): §6 checks MCP<->Python-API parity.
    @mcp.tool()
    def writer_compile_archive(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
        no_archive: bool = False,
    ) -> dict:
        """Snapshot the compiled outputs into the versions directory.

        Copies the compiled PDF/TeX and the diff PDF/TeX to
        <archive_dir>/<stem>_<YYYYmmdd-HHMMSS>_<commit>.<ext>, plus an un-stamped
        "current" copy of each. Archives ONLY a clean working tree -- a snapshot
        stamped with a commit hash it does not actually hold would be a lie -- so
        a dirty tree returns skipped=True with a skip_reason. Returns
        {success, archive_id, archived, versions_dir, missing, skipped,
        skip_reason, error}.
        """
        return _process(project_dir, doc_type, no_archive)


# EOF
