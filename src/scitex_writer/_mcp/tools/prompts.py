#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_mcp/tools/prompts.py

"""Prompts MCP tools."""

from __future__ import annotations

from pathlib import Path

from fastmcp import FastMCP


def register_tools(mcp: FastMCP) -> None:
    """Register prompts tools."""

    @mcp.tool()
    def writer_prompts_asta(
        project_path: str = ".",
        search_type: str = "related",
    ) -> str:
        """[writer] Generate AI2 Asta prompt for finding related papers or collaborators.

        Args:
            project_path: Path to scitex-writer project (default: current directory)
            search_type: "related" for related papers, "coauthors" for potential collaborators

        Extracts title, abstract, keywords, authors from project and generates
        a prompt for use with AI2 Asta (Semantic Scholar AI).
        """
        from scitex_writer import prompts

        result = prompts.generate_ai2_prompt(
            Path(project_path).resolve(),
            search_type=search_type,
        )

        if not result["success"]:
            error_msg = f"Error: {result['error']}"
            if result["next_steps"]:
                error_msg += "\n\nSuggested next steps:\n"
                error_msg += "\n".join(f"  - {step}" for step in result["next_steps"])
            return error_msg

        return result["prompt"]


# EOF
