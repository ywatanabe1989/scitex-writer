#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/tools/checks.py
# Purpose: MCP tool registrations for pre-compilation project checks.
#   - writer_check_references (issue #45)
#   - writer_check_float_order (issue #44)

"""Pre-compilation check MCP tools."""

from typing import Literal

from fastmcp import FastMCP

from ..handlers import (
    check_float_order as _check_float_order,
)
from ..handlers import (
    check_references as _check_references,
)


def register_tools(mcp: FastMCP) -> None:
    """Register project-check tools."""

    @mcp.tool()
    def writer_check_references(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "all"] = "all",
        parse_log: bool = False,
    ) -> dict:
        """Validate cross-references, citations, and labels (issue #45).

        Detects undefined ``\\ref{}`` (PDF ??), undefined ``\\cite{}``,
        multiply-defined ``\\label{}``, orphan labels, and orphan bib
        entries before LaTeX compilation makes them visible. Set
        ``parse_log=True`` to also surface warnings from a previously-
        compiled ``.log`` file.
        """
        return _check_references(project_dir, doc_type, parse_log)

    @mcp.tool()
    def writer_check_float_order(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "all"] = "manuscript",
        fix: bool = False,
        dry_run: bool = False,
    ) -> dict:
        """Validate (and optionally renumber) float reference order (issue #44).

        ``fix=True`` renames figure/table files and updates ``\\ref{}``
        and ``\\label{}`` so floats appear in numerical order in the
        text. ``dry_run=True`` previews the rename without writing. At
        most one of ``fix`` / ``dry_run`` may be set.
        """
        return _check_float_order(project_dir, doc_type, fix, dry_run)


# EOF
