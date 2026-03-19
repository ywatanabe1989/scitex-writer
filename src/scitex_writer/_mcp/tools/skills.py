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
        """List available skill pages for scitex-writer."""
        try:
            from scitex_dev.skills import list_skills

            result = list_skills(package="scitex-writer")
            return {"success": True, "skills": result.get("scitex-writer", [])}
        except ImportError:
            return {"success": False, "error": "scitex-dev not installed"}

    @mcp.tool()
    def writer_skills_get(name: str = None) -> dict:
        """Get a skill page for scitex-writer. Without name, returns main SKILL.md."""
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
