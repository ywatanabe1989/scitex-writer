#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_server.py

"""
MCP server for SciTeX Writer - LaTeX manuscript compilation system.

This is the main server entry point. Tools are organized in _mcp/tools/.
"""

from __future__ import annotations

from fastmcp import FastMCP

from ._mcp.tools import register_all_tools

# =============================================================================
# Instructions
# =============================================================================

INSTRUCTIONS = """
================================================================================
scitex-writer - LaTeX Manuscript Compilation System
================================================================================

Setup:
  git clone https://github.com/ywatanabe1989/scitex-writer.git my-paper
  cd my-paper

<SCITEX_WRITER_ROOT> = Directory where compile.sh is located

Project Structure:
  <SCITEX_WRITER_ROOT>/
  ├── compile.sh           # Main compilation script
  ├── 00_shared/           # Shared metadata (title, authors, keywords, bib_files/)
  ├── 01_manuscript/       # Main manuscript
  ├── 02_supplementary/    # Supplementary materials
  └── 03_revision/         # Revision responses

00_shared/bib_files/:
  - Place .bib files here, they are AUTO-MERGED into bibliography.bib
  - Smart deduplication by DOI and title+year
  - Cite: \\cite{AuthorYear}

01_manuscript/contents/:
  - abstract.tex, introduction.tex, methods.tex, results.tex, discussion.tex
  - figures/caption_and_media/ (01_figure.png + 01_figure.tex)
  - tables/caption_and_media/ (01_table.csv + 01_table.tex)

Compilation (BASH_ENV workaround for AI agents):
  env -u BASH_ENV /bin/bash -c '<SCITEX_WRITER_ROOT>/compile.sh manuscript --draft'

Options: --draft, --no_figs, --no_tables, --no_diff, --dark_mode, --quiet

Output: 01_manuscript/manuscript.pdf, manuscript_diff.pdf

Highlighting for User Review:
  \\hl{[PLACEHOLDER: description]}  - Content user must fill in
  \\hl{[CHECK: reason]}             - Claims/facts to verify
"""

# =============================================================================
# FastMCP Server
# =============================================================================

mcp = FastMCP(name="scitex-writer", instructions=INSTRUCTIONS)


@mcp.tool()
def usage() -> str:
    """[writer] Get usage guide for SciTeX Writer LaTeX manuscript compilation system."""
    return INSTRUCTIONS


# Register all tools from modules
register_all_tools(mcp)


# =============================================================================
# Server Entry Point
# =============================================================================


def run_server(transport: str = "stdio") -> None:
    """Run the MCP server."""
    mcp.run(transport=transport)


if __name__ == "__main__":
    run_server()

# EOF
