#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_mcp/tools/guidelines.py

"""Guidelines MCP tools."""

from __future__ import annotations

from fastmcp import FastMCP


def register_tools(mcp: FastMCP) -> None:
    """Register guidelines tools."""

    @mcp.tool()
    def writer_guideline_list() -> str:
        """[writer] List available IMRAD writing guideline sections.

        Returns list of sections: abstract, introduction, methods, discussion, proofread.
        """
        from scitex_writer import guidelines

        sections = guidelines.list_sections()
        return "Available guideline sections:\n" + "\n".join(
            f"  - {s}" for s in sections
        )

    @mcp.tool()
    def writer_guideline_get(section: str) -> str:
        """[writer] Get IMRAD writing guideline for a manuscript section.

        Args:
            section: Section name (abstract, introduction, methods, discussion, proofread)

        Returns guideline with template structure and examples.
        Use writer_guideline_build() to combine with a draft for editing prompts.
        """
        from scitex_writer import guidelines

        try:
            return guidelines.get(section)
        except ValueError as e:
            return f"Error: {e}\n\nAvailable sections: {', '.join(guidelines.list_sections())}"
        except FileNotFoundError as e:
            return f"Error: {e}"

    @mcp.tool()
    def writer_guideline_build(section: str, draft: str) -> str:
        """[writer] Build editing prompt by combining guideline with draft text.

        Args:
            section: Section name (abstract, introduction, methods, discussion, proofread)
            draft: The draft text to be reviewed/edited

        Returns a complete prompt with guideline + draft for AI-assisted editing.
        """
        from scitex_writer import guidelines

        try:
            return guidelines.build(section, draft)
        except ValueError as e:
            return f"Error: {e}\n\nAvailable sections: {', '.join(guidelines.list_sections())}"
        except FileNotFoundError as e:
            return f"Error: {e}"


# EOF
