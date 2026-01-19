#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-20
# File: src/scitex_writer/_server.py

"""
MCP server for SciTeX Writer - LaTeX manuscript compilation system.

Provides 13 tools for manuscript operations.
"""

from __future__ import annotations

from typing import List, Literal, Optional, Union

from fastmcp import FastMCP

from ._mcp.handlers import (
    clone_project as _clone_project,
)
from ._mcp.handlers import (
    compile_manuscript as _compile_manuscript,
)
from ._mcp.handlers import (
    compile_revision as _compile_revision,
)
from ._mcp.handlers import (
    compile_supplementary as _compile_supplementary,
)
from ._mcp.handlers import (
    convert_figure as _convert_figure,
)
from ._mcp.handlers import (
    csv_to_latex as _csv_to_latex,
)
from ._mcp.handlers import (
    get_pdf as _get_pdf,
)
from ._mcp.handlers import (
    get_project_info as _get_project_info,
)
from ._mcp.handlers import (
    latex_to_csv as _latex_to_csv,
)
from ._mcp.handlers import (
    list_document_types as _list_document_types,
)
from ._mcp.handlers import (
    list_figures as _list_figures,
)
from ._mcp.handlers import (
    pdf_to_images as _pdf_to_images,
)

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
def clone_project(
    project_dir: str,
    git_strategy: Literal["child", "parent", "origin", "none"] = "child",
    branch: Optional[str] = None,
    tag: Optional[str] = None,
) -> dict:
    """[writer] Create a new LaTeX manuscript project from template."""
    return _clone_project(project_dir, git_strategy, branch, tag)


@mcp.tool()
def compile_manuscript(
    project_dir: str,
    timeout: int = 300,
    no_figs: bool = False,
    no_tables: bool = False,
    no_diff: bool = False,
    draft: bool = False,
    dark_mode: bool = False,
    quiet: bool = False,
    verbose: bool = False,
    force: bool = False,
) -> dict:
    """[writer] Compile manuscript LaTeX document to PDF."""
    return _compile_manuscript(
        project_dir,
        timeout,
        no_figs,
        no_tables,
        no_diff,
        draft,
        dark_mode,
        quiet,
        verbose,
        force,
    )


@mcp.tool()
def compile_supplementary(
    project_dir: str,
    timeout: int = 300,
    no_figs: bool = False,
    no_tables: bool = False,
    no_diff: bool = False,
    draft: bool = False,
    quiet: bool = False,
) -> dict:
    """[writer] Compile supplementary materials LaTeX document to PDF."""
    return _compile_supplementary(
        project_dir,
        timeout,
        no_figs,
        no_tables,
        no_diff,
        draft,
        quiet,
    )


@mcp.tool()
def compile_revision(
    project_dir: str,
    track_changes: bool = False,
    timeout: int = 300,
    no_diff: bool = True,
    draft: bool = False,
    quiet: bool = False,
) -> dict:
    """[writer] Compile revision document to PDF with optional change tracking."""
    return _compile_revision(
        project_dir,
        track_changes,
        timeout,
        no_diff,
        draft,
        quiet,
    )


@mcp.tool()
def get_project_info(project_dir: str) -> dict:
    """[writer] Get writer project structure and status information."""
    return _get_project_info(project_dir)


@mcp.tool()
def get_pdf(
    project_dir: str,
    doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
) -> dict:
    """[writer] Get path to compiled PDF for a document type."""
    return _get_pdf(project_dir, doc_type)


@mcp.tool()
def list_document_types() -> dict:
    """[writer] List available document types in a writer project."""
    return _list_document_types()


@mcp.tool()
def csv_to_latex(
    csv_path: str,
    output_path: Optional[str] = None,
    caption: Optional[str] = None,
    label: Optional[str] = None,
    longtable: bool = False,
) -> dict:
    """[writer] Convert CSV file to LaTeX table format."""
    return _csv_to_latex(csv_path, output_path, caption, label, longtable)


@mcp.tool()
def latex_to_csv(
    latex_path: str,
    output_path: Optional[str] = None,
    table_index: int = 0,
) -> dict:
    """[writer] Convert LaTeX table to CSV format."""
    return _latex_to_csv(latex_path, output_path, table_index)


@mcp.tool()
def pdf_to_images(
    pdf_path: str,
    output_dir: Optional[str] = None,
    pages: Optional[Union[int, List[int]]] = None,
    dpi: int = 150,
    format: Literal["png", "jpg"] = "png",
) -> dict:
    """[writer] Render PDF pages as images."""
    return _pdf_to_images(pdf_path, output_dir, pages, dpi, format)


@mcp.tool()
def list_figures(
    project_dir: str,
    extensions: Optional[List[str]] = None,
) -> dict:
    """[writer] List all figures in a writer project directory."""
    return _list_figures(project_dir, extensions)


@mcp.tool()
def convert_figure(
    input_path: str,
    output_path: str,
    dpi: int = 300,
    quality: int = 95,
) -> dict:
    """[writer] Convert figure between formats (e.g., PDF to PNG)."""
    return _convert_figure(input_path, output_path, dpi, quality)


@mcp.tool()
def scitex_writer(
    command: Literal["usage"],
    doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
    project_dir: str = ".",
) -> str:
    """SciTeX Writer - LaTeX manuscript compilation system (usage docs)."""
    return INSTRUCTIONS


def run_server(transport: str = "stdio") -> None:
    """Run the MCP server."""
    mcp.run(transport=transport)


if __name__ == "__main__":
    run_server()

# EOF
