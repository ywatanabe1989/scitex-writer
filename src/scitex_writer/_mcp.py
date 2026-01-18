#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-19 05:00:00
# File: src/scitex_writer/_mcp.py

"""MCP server for SciTeX Writer - provides usage documentation to AI agents."""

from typing import Literal

from fastmcp import FastMCP

INSTRUCTIONS = """
scitex-writer - LaTeX Manuscript Compilation System

Setup (clone template):
  git clone https://github.com/ywatanabe1989/scitex-writer.git my-paper
  cd my-paper

Project Structure:
  00_shared/           - Shared metadata (title, authors, keywords, bib_files/)
  01_manuscript/       - Main manuscript
  02_supplementary/    - Supplementary materials
  03_revision/         - Revision responses

Quick Start:
  ./compile.sh manuscript       # Compile manuscript
  ./compile.sh supplementary    # Compile supplementary
  ./compile.sh revision         # Compile revision
  ./compile.sh --help-recursive # Full documentation

Editable Files (manuscript):
  01_manuscript/contents/abstract.tex
  01_manuscript/contents/introduction.tex
  01_manuscript/contents/methods.tex
  01_manuscript/contents/results.tex
  01_manuscript/contents/discussion.tex
  01_manuscript/contents/figures/caption_and_media/
  01_manuscript/contents/tables/caption_and_media/

Figure Naming:
  01_my_figure.png + 01_my_figure.tex (caption)
  Cite: \\ref{fig:my_figure_01}

Table Naming:
  01_my_table.csv + 01_my_table.tex (caption)
  Cite: \\ref{tab:my_table_01}

Compile Options:
  --draft      Single-pass compilation (~5s faster)
  --no_figs    Skip figure processing (~4s faster)
  --no_tables  Skip table processing (~4s faster)
  --no_diff    Skip diff generation (~17s faster)
  --dark_mode  Black background, white text
  --quiet      Minimal output

Output:
  01_manuscript/manuscript.pdf
  02_supplementary/supplementary.pdf
  03_revision/revision.pdf
"""

mcp = FastMCP(
    name="scitex-writer",
    instructions=INSTRUCTIONS,
)


@mcp.tool()
def scitex_writer(
    command: Literal["usage"],
    doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
    project_dir: str = ".",
) -> str:
    """SciTeX Writer - LaTeX manuscript compilation system.

    Args:
        command: Command to execute (usage)
        doc_type: Document type
        project_dir: Path to the scitex-writer project directory

    Returns:
        Usage guide for the project
    """
    if command == "usage":
        return INSTRUCTIONS
    return INSTRUCTIONS


def run_server(transport: str = "stdio") -> None:
    """Run the MCP server."""
    mcp.run(transport=transport)


if __name__ == "__main__":
    run_server()

# EOF
