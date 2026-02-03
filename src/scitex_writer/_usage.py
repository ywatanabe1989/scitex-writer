#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-04
# File: src/scitex_writer/_usage.py

"""Usage guide content for scitex-writer.

This module contains the usage documentation text, separate from branding logic.
"""

from ._branding import BRAND_ALIAS, BRAND_NAME, get_branded_import_example

_USAGE_TEMPLATE = """
================================================================================
{brand_name} - LaTeX Manuscript Compilation System
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
  - Cite: \\cite{{AuthorYear}}

01_manuscript/contents/:
  - abstract.tex, introduction.tex, methods.tex, results.tex, discussion.tex
  - figures/caption_and_media/ (01_figure.png + 01_figure.tex)
  - tables/caption_and_media/ (01_table.csv + 01_table.tex)

Python API:
  {import_example}
  {alias}.compile.manuscript("./my-paper")
  {alias}.project.clone("./new-paper")

CLI:
  scitex-writer usage                    # Show this guide
  scitex-writer compile manuscript .     # Compile manuscript
  scitex-writer mcp list-tools           # List MCP tools

MCP Tool:
  writer_usage()                         # Returns this guide

Compilation (BASH_ENV workaround for AI agents):
  env -u BASH_ENV /bin/bash -c '<SCITEX_WRITER_ROOT>/compile.sh manuscript --draft'

Options: --draft, --no_figs, --no_tables, --no_diff, --dark_mode, --quiet

Output: 01_manuscript/manuscript.pdf, manuscript_diff.pdf

Highlighting for User Review:
  \\hl{{[PLACEHOLDER: description]}}  - Content user must fill in
  \\hl{{[CHECK: reason]}}             - Claims/facts to verify
"""


def get_usage() -> str:
    """Get the usage guide with branding applied.

    Returns
    -------
    str
        Formatted usage guide string.
    """
    return _USAGE_TEMPLATE.format(
        brand_name=BRAND_NAME,
        import_example=get_branded_import_example(),
        alias=BRAND_ALIAS,
    )


__all__ = ["get_usage"]

# EOF
