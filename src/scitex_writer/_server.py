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

# =============================================================================
# Modular Instructions
# =============================================================================

INSTRUCTIONS_HEADER = """
================================================================================
scitex-writer - LaTeX Manuscript Compilation System
================================================================================

Setup:
  git clone https://github.com/ywatanabe1989/scitex-writer.git my-paper
  cd my-paper

<SCITEX_WRITER_ROOT> Definition (IMPORTANT!):
  <SCITEX_WRITER_ROOT> = Directory where compile.sh is located
  Example: If you cloned to /home/user/my-paper, then <SCITEX_WRITER_ROOT> = /home/user/my-paper

Project Structure:
  <SCITEX_WRITER_ROOT>/
  ├── compile.sh           # Main compilation script (defines PROJECT_ROOT)
  ├── 00_shared/           # Shared metadata (title, authors, keywords, bib_files/)
  ├── 01_manuscript/       # Main manuscript
  ├── 02_supplementary/    # Supplementary materials
  └── 03_revision/         # Revision responses
"""

INSTRUCTIONS_SHARED = """
================================================================================
00_shared/ - Shared Resources
================================================================================

Directory Structure:
  <SCITEX_WRITER_ROOT>/00_shared/
  ├── title.tex              # Paper title
  ├── authors.tex            # Author list and affiliations
  ├── keywords.tex           # Keywords for the paper
  ├── journal_name.tex       # Target journal name
  └── bib_files/             # Bibliography files (AUTO-MERGED)
      ├── my_refs.bib        # Your custom references
      ├── related_work.bib   # Related work citations
      ├── methods_refs.bib   # Method-specific references
      └── bibliography.bib   # AUTO-GENERATED merged output

Bibliography (IMPORTANT):
  - Place .bib files in: <SCITEX_WRITER_ROOT>/00_shared/bib_files/
  - Multiple .bib files are AUTO-MERGED into bibliography.bib during compilation
  - Smart deduplication by DOI and title+year (no duplicates in output)
  - Hash-based caching (merge skipped if files unchanged)
  - Cite in text: \\cite{AuthorYear} e.g., \\cite{Lamport1994}

Editing Shared Metadata:
  - title.tex:        \\newcommand{\\mytitle}{Your Paper Title}
  - authors.tex:      Author names, affiliations, corresponding author
  - keywords.tex:     \\newcommand{\\mykeywords}{keyword1, keyword2, ...}
"""

INSTRUCTIONS_MANUSCRIPT = """
================================================================================
01_manuscript/ - Main Manuscript
================================================================================

Directory Structure:
  <SCITEX_WRITER_ROOT>/01_manuscript/
  ├── contents/
  │   ├── abstract.tex           # Abstract section
  │   ├── introduction.tex       # Introduction (IMRAD)
  │   ├── methods.tex            # Methods (IMRAD)
  │   ├── results.tex            # Results (IMRAD)
  │   ├── discussion.tex         # Discussion (IMRAD)
  │   ├── highlights.tex         # Paper highlights (optional)
  │   ├── data_availability.tex  # Data availability statement
  │   ├── figures/
  │   │   └── caption_and_media/ # Figure images + captions
  │   └── tables/
  │       └── caption_and_media/ # Table CSVs + captions
  └── manuscript.pdf             # OUTPUT

Figures:
  Location: <SCITEX_WRITER_ROOT>/01_manuscript/contents/figures/caption_and_media/
  Files needed:
    - 01_my_figure.png           # Image file (png/jpg/tif/pdf)
    - 01_my_figure.tex           # Caption file
  Caption format (01_my_figure.tex):
    \\caption{Your figure caption here.}
    \\label{fig:my_figure_01}
  Multi-panel figures:
    - 01a_panel_name.png, 01b_panel_name.png  # Auto-tiled
    - 01_panel_name.tex                        # Single caption for all panels
  Reference: Figure~\\ref{fig:my_figure_01}

Tables:
  Location: <SCITEX_WRITER_ROOT>/01_manuscript/contents/tables/caption_and_media/
  Files needed:
    - 01_my_table.csv            # Data file (comma-separated with headers)
    - 01_my_table.tex            # Caption file
  Caption format (01_my_table.tex):
    \\caption{Your table caption here.}
    \\label{tab:my_table_01}
  Reference: Table~\\ref{tab:my_table_01}
"""

INSTRUCTIONS_SUPPLEMENTARY = """
================================================================================
02_supplementary/ - Supplementary Materials
================================================================================

Directory Structure:
  <SCITEX_WRITER_ROOT>/02_supplementary/
  ├── contents/
  │   ├── supplementary_text.tex    # Additional methods, results
  │   ├── figures/
  │   │   └── caption_and_media/    # Supplementary figures
  │   └── tables/
  │       └── caption_and_media/    # Supplementary tables
  └── supplementary.pdf             # OUTPUT

Same conventions as manuscript:
  - Figures: S01_my_figure.png + S01_my_figure.tex
  - Tables:  S01_my_table.csv + S01_my_table.tex
  - Reference: Figure~\\ref{fig:S01_...}, Table~\\ref{tab:S01_...}
"""

INSTRUCTIONS_REVISION = """
================================================================================
03_revision/ - Revision Response
================================================================================

Directory Structure:
  <SCITEX_WRITER_ROOT>/03_revision/
  ├── base.tex                       # Main revision response document
  ├── contents/
  │   ├── editor/                    # Editor comments and responses
  │   │   ├── E_01_comments.tex      # ─┐
  │   │   ├── E_01_response.tex      # ─┼─ TRIPLET for editor comment #1
  │   │   ├── E_01_revision.tex      # ─┘
  │   │   ├── E_02_comments.tex      # ─┐
  │   │   ├── E_02_response.tex      # ─┼─ TRIPLET for editor comment #2
  │   │   └── E_02_revision.tex      # ─┘
  │   ├── reviewer1/                 # Reviewer 1 comments and responses
  │   │   ├── R1_01_comments.tex     # ─┐
  │   │   ├── R1_01_response.tex     # ─┼─ TRIPLET for reviewer 1 comment #1
  │   │   ├── R1_01_revision.tex     # ─┘
  │   │   ├── R1_02_comments.tex     # ─┐
  │   │   ├── R1_02_response.tex     # ─┼─ TRIPLET for reviewer 1 comment #2
  │   │   └── R1_02_revision.tex     # ─┘
  │   ├── reviewer2/                 # Reviewer 2 (same triplet pattern)
  │   │   └── ...
  │   ├── figures/
  │   │   └── caption_and_media/     # Revised/new figures
  │   └── tables/
  │       └── caption_and_media/     # Revised/new tables
  └── revision.pdf                   # OUTPUT

TRIPLET Structure (IMPORTANT!):
  Each reviewer comment is handled by a TRIPLET of files sharing the same number:

  ┌─────────────────────────────────────────────────────────────────────────┐
  │  TRIPLET for one comment (e.g., Reviewer 1, Comment #01)                │
  ├─────────────────────────────────────────────────────────────────────────┤
  │  R1_01_comments.tex  : Verbatim quote from reviewer's email             │
  │  R1_01_response.tex  : Your response/explanation to the reviewer        │
  │  R1_01_revision.tex  : Actual revision made in manuscript (with diff)   │
  └─────────────────────────────────────────────────────────────────────────┘

File Naming Convention:
  - Editor:     E_XX_comments.tex, E_XX_response.tex, E_XX_revision.tex
  - Reviewer 1: R1_XX_comments.tex, R1_XX_response.tex, R1_XX_revision.tex
  - Reviewer 2: R2_XX_comments.tex, R2_XX_response.tex, R2_XX_revision.tex
  (XX = two-digit number: 01, 02, 03, ...)

Example TRIPLET:
  R1_01_comments.tex  -> "The methodology section lacks detail on..."
  R1_01_response.tex  -> "Thank you for this suggestion. We have expanded..."
  R1_01_revision.tex  -> "We added the following text to Methods section: ..."
"""

INSTRUCTIONS_COMPILATION = """
================================================================================
Compilation
================================================================================

<SCITEX_WRITER_ROOT> Reminder:
  <SCITEX_WRITER_ROOT> = Directory where compile.sh is located
  ALWAYS use the absolute path to <SCITEX_WRITER_ROOT>/compile.sh

IMPORTANT for AI Agents (BASH_ENV workaround):
  Claude Code and similar tools may have BASH_ENV set, which can cause issues.
  ALWAYS use this pattern:
    env -u BASH_ENV /bin/bash -c '<SCITEX_WRITER_ROOT>/compile.sh manuscript --draft'

Commands:
  Fast compilation (recommended for iterative editing):
    env -u BASH_ENV /bin/bash -c '<SCITEX_WRITER_ROOT>/compile.sh manuscript --draft --no_diff --quiet'

  Full compilation with diff:
    env -u BASH_ENV /bin/bash -c '<SCITEX_WRITER_ROOT>/compile.sh manuscript'

  Supplementary:
    env -u BASH_ENV /bin/bash -c '<SCITEX_WRITER_ROOT>/compile.sh supplementary --draft --quiet'

  Revision:
    env -u BASH_ENV /bin/bash -c '<SCITEX_WRITER_ROOT>/compile.sh revision --draft --quiet'

Options:
  --draft      Single-pass compilation (~5s faster)
  --no_figs    Skip figure processing (~4s faster)
  --no_tables  Skip table processing (~4s faster)
  --no_diff    Skip diff generation (~17s faster)
  --dark_mode  Black background, white text
  --quiet      Minimal output

Output Files:
  <SCITEX_WRITER_ROOT>/01_manuscript/manuscript.pdf
  <SCITEX_WRITER_ROOT>/01_manuscript/manuscript_diff.pdf (changes from last commit)
  <SCITEX_WRITER_ROOT>/02_supplementary/supplementary.pdf
  <SCITEX_WRITER_ROOT>/03_revision/revision.pdf
"""

INSTRUCTIONS_TIPS = """
================================================================================
Tips for AI Agents
================================================================================

1. READ before EDIT: Always read the file first to understand existing content
2. PRESERVE structure: Keep LaTeX commands and formatting intact
3. USE labels: Reference figures/tables with \\ref{fig:label} or \\ref{tab:label}
4. COMPILE often: Check PDF output to verify formatting
5. USE ABSOLUTE PATHS: Always use <SCITEX_WRITER_ROOT>/... not relative paths

Highlighting for User Review (IMPORTANT!):
  Use \\hl{text} to highlight content that needs user attention:

    \\hl{[PLACEHOLDER: description]}  - Content user must fill in
    \\hl{[CHECK: reason]}             - Claims/facts to verify
    \\hl{[TODO: task]}                - Tasks for user to complete
    \\hl{[UNCERTAIN: note]}           - Low-confidence content

  Examples:
    The sample size was \\hl{[PLACEHOLDER: N=?]} participants.
    This achieved \\hl{[CHECK: verify accuracy]} 95\\% accuracy.

  Highlighted text appears YELLOW in the compiled PDF for easy review.
  ALWAYS use \\hl{} for placeholders and uncertain content!
"""

# Concatenate all instructions
INSTRUCTIONS = (
    INSTRUCTIONS_HEADER
    + INSTRUCTIONS_SHARED
    + INSTRUCTIONS_MANUSCRIPT
    + INSTRUCTIONS_SUPPLEMENTARY
    + INSTRUCTIONS_REVISION
    + INSTRUCTIONS_COMPILATION
    + INSTRUCTIONS_TIPS
)

# =============================================================================
# FastMCP Server
# =============================================================================

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
