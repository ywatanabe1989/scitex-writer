#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-03-20
# File: src/scitex_writer/_mcp/tools/skills.py

"""Skills MCP tools for scitex-writer."""

from fastmcp import FastMCP


def register_tools(mcp: FastMCP) -> None:
    """Register skills tools."""

    @mcp.tool()
    def writer_skills_list() -> dict:
        """Enumerate every scitex-writer skill page — covering manuscript compilation (LaTeX build, PDF export), BibTeX management (merge/dedupe/enrich), figure and table reference workflows, revision cycles, and Overleaf import/export. Drop-in replacement for manually browsing `~/.claude/skills/scitex/scitex-writer/`. Use when the user asks "what scitex-writer skills are there?", "list writer skill pages", "show me the writer docs index", or is looking for guidance before compiling a manuscript, wrangling citations, or handling revisions."""
        try:
            from scitex_dev.skills import list_skills

            result = list_skills(package="scitex-writer")
            return {"success": True, "skills": result.get("scitex-writer", [])}
        except ImportError:
            return {"success": False, "error": "scitex-dev not installed"}

    @mcp.tool()
    def writer_skills_get(name: str = None) -> dict:
        """Fetch the full markdown of a scitex-writer skill page — manuscript compilation, BibTeX management, figure/table refs, revision workflows, or Overleaf sync — or the main SKILL.md overview when `name` is omitted. Drop-in replacement for `cat ~/.claude/skills/scitex/scitex-writer/<name>.md`. Use when the user asks "show me the writer skill for X", "how do I compile a manuscript with scitex-writer?", "read the bib workflow doc", "open scitex-writer SKILL.md", or needs authoritative guidance before invoking writer_* tools."""
        try:
            from scitex_dev.skills import get_skill

            content = get_skill(package="scitex-writer", name=name)
            if content:
                return {"success": True, "name": name, "content": content}
            target = f"'{name}'" if name else "SKILL.md"
            return {"success": False, "error": f"Skill {target} not found"}
        except ImportError:
            return {"success": False, "error": "scitex-dev not installed"}


# EOF
