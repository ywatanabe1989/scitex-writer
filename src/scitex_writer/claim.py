#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/claim.py

"""Claim functions for traceable scientific assertions in manuscripts.

Usage::

    import scitex_writer as sw

    # Add a statistical claim
    sw.claim.add(
        "./my-paper", "group_comparison", "statistic",
        {"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        context="Group A vs B alpha power comparison",
    )

    # List all claims
    sw.claim.list("./my-paper")

    # Format for inline display
    sw.claim.format("./my-paper", "group_comparison", style="apa")

    # Render to LaTeX (auto-called before compile)
    sw.claim.render("./my-paper")

In LaTeX (after render):
    \\stxclaim{group_comparison}           % nature style: t(34) = 4.23, p < 0.001, d = 0.87
    \\stxclaim[apa]{group_comparison}      % APA style:    t(34) = 4.23, p < .001, Cohen's d = 0.87
    \\stxclaim[plain]{group_comparison}    % plain text:   t(34) = 4.23, p < 0.001, d = 0.87
"""

from ._mcp.handlers._claim import add_claim as _add_claim
from ._mcp.handlers._claim import format_claim as _format_claim
from ._mcp.handlers._claim import get_claim as _get_claim
from ._mcp.handlers._claim import list_claims as _list_claims
from ._mcp.handlers._claim import remove_claim as _remove_claim
from ._mcp.handlers._claim import render_claims as _render_claims


def add(
    project_dir,
    claim_id,
    claim_type,
    value,
    context=None,
    session_id=None,
    output_file=None,
    output_hash=None,
    test=None,
):
    """Add or update a claim in 00_shared/claims.json."""
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


def list(project_dir):  # noqa: A001
    """List all claims in the project."""
    return _list_claims(project_dir)


def get(project_dir, claim_id):
    """Get full details of a specific claim."""
    return _get_claim(project_dir, claim_id)


def remove(project_dir, claim_id):
    """Remove a claim from the project."""
    return _remove_claim(project_dir, claim_id)


def format(project_dir, claim_id, style="nature"):  # noqa: A001
    """Render a claim as a formatted LaTeX string."""
    return _format_claim(project_dir, claim_id, style)


def render(project_dir):
    """Generate 00_shared/claims_rendered.tex from claims.json."""
    return _render_claims(project_dir)


__all__ = ["add", "list", "get", "remove", "format", "render"]

# EOF
