#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: src/scitex_writer/_server.py

"""
MCP server for SciTeX Writer - LaTeX manuscript compilation system.

Provides usage instructions for shell-based compilation workflow.
"""

from __future__ import annotations

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

Compilation (IMPORTANT for AI Agents):
  ALWAYS use absolute path to avoid working directory issues:
    /path/to/project/compile.sh manuscript --draft --quiet

  If BASH_ENV causes issues (e.g., in Claude Code), use:
    env -u BASH_ENV /bin/bash -c '/path/to/project/compile.sh manuscript --draft'

  Fast compilation (recommended for iterative editing):
    /path/to/project/compile.sh manuscript --draft --no_diff --quiet

  Full compilation with diff:
    /path/to/project/compile.sh manuscript

Editable Files (IMRAD structure):
  01_manuscript/contents/abstract.tex
  01_manuscript/contents/introduction.tex
  01_manuscript/contents/methods.tex
  01_manuscript/contents/results.tex
  01_manuscript/contents/discussion.tex

Figures:
  Location: 01_manuscript/contents/figures/caption_and_media/
  Naming:   01_my_figure.png + 01_my_figure.tex (caption)
  Cite: \\ref{fig:my_figure_01} or Figure~\\ref{fig:my_figure_01}

Tables:
  Location: 01_manuscript/contents/tables/caption_and_media/
  Naming:   01_my_table.csv + 01_my_table.tex (caption)
  Cite: \\ref{tab:my_table_01} or Table~\\ref{tab:my_table_01}

Bibliography:
  Location: 00_shared/bib_files/
  Cite: \\cite{AuthorYear} e.g., \\cite{Lamport1994}

Compile Options:
  --draft      Single-pass compilation (~5s faster)
  --no_figs    Skip figure processing (~4s faster)
  --no_tables  Skip table processing (~4s faster)
  --no_diff    Skip diff generation (~17s faster)
  --dark_mode  Black background, white text
  --quiet      Minimal output

Output:
  01_manuscript/manuscript.pdf
  01_manuscript/manuscript_diff.pdf (changes from last commit)
  02_supplementary/supplementary.pdf
  03_revision/revision.pdf
"""

mcp = FastMCP(name="scitex-writer", instructions=INSTRUCTIONS)


@mcp.tool()
def usage() -> str:
    """[writer] Get usage guide for SciTeX Writer LaTeX manuscript compilation system."""
    return INSTRUCTIONS


def run_server(transport: str = "stdio") -> None:
    """Run the MCP server."""
    mcp.run(transport=transport)


if __name__ == "__main__":
    run_server()

# EOF
