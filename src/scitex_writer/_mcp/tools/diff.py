#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/tools/diff.py

"""Version-diff MCP tools (latexdiff pipeline)."""

from typing import Literal, Optional

from fastmcp import FastMCP

from ..._utils._latexmk import DEFAULT_TIMEOUT_SEC
from ..handlers._diff_pipeline import process as _process


def register_tools(mcp: FastMCP) -> None:
    """Register version-diff tools."""

    # Named for its Python API (`sw.compile.diff`), not for the CLI leaf
    # (`scitex-writer diff render`): §6 checks MCP<->Python-API parity.
    @mcp.tool()
    def writer_compile_diff(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
        no_diff: bool = False,
        diff_from: Optional[str] = None,
        timeout_sec: int = DEFAULT_TIMEOUT_SEC,
    ) -> dict:
        """Build the version-diff PDF: git history -> latexdiff -> latexmk.

        Reads the PREVIOUS version of the compiled .tex out of git history (or the
        commit given as diff_from), runs latexdiff against the current one, stamps
        a metadata + fancyhdr signature block, and compiles the result with
        latexmk bounded by timeout_sec. With NO previous version this FAILS rather
        than emitting an unmarked PDF that looks like "nothing changed"; a missing
        latexdiff/latexmk fails with an install hint. no_diff=True skips
        everything. Returns {success, from_hash, to_hash, diff_tex, diff_pdf,
        pdf_bytes, skipped, error}.
        """
        return _process(project_dir, doc_type, no_diff, diff_from, timeout_sec)


# EOF
