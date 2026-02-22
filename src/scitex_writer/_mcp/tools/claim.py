#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/tools/claim.py

"""Claim MCP tools — traceable scientific assertions in LaTeX manuscripts."""


from typing import Any, Dict, Optional

from fastmcp import FastMCP

from ..handlers._claim import (
    add_claim as _add_claim,
)
from ..handlers._claim import (
    format_claim as _format_claim,
)
from ..handlers._claim import (
    get_claim as _get_claim,
)
from ..handlers._claim import (
    list_claims as _list_claims,
)
from ..handlers._claim import (
    remove_claim as _remove_claim,
)
from ..handlers._claim import (
    render_claims as _render_claims,
)


def register_tools(mcp: FastMCP) -> None:
    """Register claim tools with the MCP server."""

    @mcp.tool()
    def writer_add_claim(
        project_dir: str,
        claim_id: str,
        claim_type: str,
        value: Dict[str, Any],
        context: Optional[str] = None,
        session_id: Optional[str] = None,
        output_file: Optional[str] = None,
        output_hash: Optional[str] = None,
        test: Optional[str] = None,
    ) -> dict:
        """[writer] Add or update a claim in 00_shared/claims.json.

        Claims are traceable scientific assertions — statistics, values, citations —
        stored as structured objects instead of hardcoded magic numbers.

        After adding claims, use writer_render_claims (or recompile) to generate
        the LaTeX macro file. Then use \\stxclaim{claim_id} in your manuscript.

        claim_type options:
          - statistic: value={t, df, p, d} or {F, df1, df2, p, eta2} or {r, p}
          - value: value={value, unit}
          - citation: value={text}
          - figure: value={label}
          - table: value={label}

        Examples:
          writer_add_claim("./paper", "group_comparison", "statistic",
                           {"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
                           context="Group A vs B alpha power")
          writer_add_claim("./paper", "replic_rate", "citation",
                           {"text": "70\\\\%"}, context="Baker 2016 replication")
        """
        return _add_claim(
            project_dir,
            claim_id,
            claim_type,
            value,
            context,
            session_id,
            output_file,
            output_hash,
            test,
        )

    @mcp.tool()
    def writer_list_claims(project_dir: str) -> dict:
        """[writer] List all claims in the project.

        Returns each claim's ID, type, context, and a nature-style preview.
        """
        return _list_claims(project_dir)

    @mcp.tool()
    def writer_get_claim(project_dir: str, claim_id: str) -> dict:
        """[writer] Get full details of a specific claim including all style renderings.

        Returns the raw claim data and rendered previews for nature, apa, and plain styles.
        """
        return _get_claim(project_dir, claim_id)

    @mcp.tool()
    def writer_remove_claim(project_dir: str, claim_id: str) -> dict:
        """[writer] Remove a claim from 00_shared/claims.json.

        Note: Re-run writer_render_claims after removal to update claims_rendered.tex.
        """
        return _remove_claim(project_dir, claim_id)

    @mcp.tool()
    def writer_format_claim(
        project_dir: str,
        claim_id: str,
        style: str = "nature",
    ) -> dict:
        """[writer] Render a claim as a formatted LaTeX string.

        style options:
          - nature: p < 0.001, standard journal format (default)
          - apa: p < .001, APA Publication Manual format
          - plain: plain text without LaTeX math delimiters
        """
        return _format_claim(project_dir, claim_id, style)

    @mcp.tool()
    def writer_render_claims(project_dir: str) -> dict:
        """[writer] Generate 00_shared/claims_rendered.tex from claims.json.

        This file defines the \\stxclaim[style]{id} LaTeX macro and all claim
        renderings. It is included automatically in the manuscript preamble
        (via \\IfFileExists in packages.tex) and is regenerated before each compile.

        Run this explicitly after modifying claims to update the rendered file
        without a full recompilation.
        """
        return _render_claims(project_dir)


# EOF
