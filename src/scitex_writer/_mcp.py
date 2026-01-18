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
  Caption file format:
    %% Figure caption
    \\caption{Your caption here.}
    \\label{fig:my_figure_01}
  Cite: \\ref{fig:my_figure_01} or Figure~\\ref{fig:my_figure_01}

Tables:
  Location: 01_manuscript/contents/tables/caption_and_media/
  Naming:   01_my_table.csv + 01_my_table.tex (caption)
  Caption file format:
    %% Table caption
    \\caption{Your caption here.}
    \\label{tab:my_table_01}
  Cite: \\ref{tab:my_table_01} or Table~\\ref{tab:my_table_01}

Bibliography:
  Location: 00_shared/bib_files/
  Single file: Name it bibliography.bib to skip merge step
  Multiple files: Requires bibtexparser (pip install bibtexparser)
  Cite: \\cite{AuthorYear} e.g., \\cite{Lamport1994}

Compile Options:
  --draft      Single-pass compilation (~5s faster)
  --no_figs    Skip figure processing (~4s faster)
  --no_tables  Skip table processing (~4s faster)
  --no_diff    Skip diff generation (~17s faster)
  --dark_mode  Black background, white text
  --quiet      Minimal output

Output:
  01_manuscript/manuscript.pdf        - Main document
  01_manuscript/manuscript_diff.pdf   - Changes from last commit (red=deleted, blue=added)
  02_supplementary/supplementary.pdf
  03_revision/revision.pdf

Version Control:
  Git commit before compiling to enable diff generation
  Diff compares: last commit -> current (uncommitted) changes
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
