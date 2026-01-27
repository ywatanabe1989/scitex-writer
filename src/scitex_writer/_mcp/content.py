#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_mcp/content.py

"""Content compilation for LaTeX snippets and sections.

Provides quick compilation of raw LaTeX content with color mode support.
"""

from __future__ import annotations

import re
import subprocess
import tempfile
from pathlib import Path
from typing import Literal, Optional

from .utils import resolve_project_path


def compile_content(
    latex_content: str,
    project_dir: Optional[str] = None,
    color_mode: Literal["light", "dark", "sepia", "paper"] = "light",
    section_name: str = "content",
    timeout: int = 60,
    keep_aux: bool = False,
) -> dict:
    """Compile raw LaTeX content to PDF.

    Creates a standalone document from the provided LaTeX content and compiles
    it to PDF. Supports various color modes for comfortable viewing and can
    link to project bibliography for citation rendering.

    Args:
        latex_content: Raw LaTeX content to compile. Can be:
            - A complete document (with \\documentclass)
            - Document body only (will be wrapped automatically)
        project_dir: Optional path to scitex-writer project for bibliography.
        color_mode: Color theme for output:
            - 'light': Default white background
            - 'dark': Dark gray background with light text
            - 'sepia': Warm cream background for comfortable reading
            - 'paper': Pure white, optimized for printing
        section_name: Name for the output (used in filename).
        timeout: Compilation timeout in seconds.
        keep_aux: Keep auxiliary files (.aux, .log, etc.) after compilation.

    Returns:
        Dict with success status, output_pdf path, log, and any errors.
    """
    try:
        temp_dir = Path(tempfile.mkdtemp(prefix=f"scitex_content_{section_name}_"))
        tex_file = temp_dir / f"{section_name}.tex"
        pdf_file = temp_dir / f"{section_name}.pdf"

        is_complete_document = "\\documentclass" in latex_content

        if is_complete_document:
            final_content = _inject_color_mode(latex_content, color_mode)
        else:
            final_content = _create_content_document(
                latex_content, color_mode, project_dir
            )

        tex_file.write_text(final_content, encoding="utf-8")

        if project_dir:
            _setup_bibliography(temp_dir, project_dir)

        cmd = [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-jobname={section_name}",
            str(tex_file),
        ]

        result = subprocess.run(
            cmd,
            cwd=str(temp_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        log_content = _read_log_file(temp_dir, section_name)

        if not keep_aux:
            _cleanup_aux_files(temp_dir, section_name)

        if result.returncode == 0 and pdf_file.exists():
            return {
                "success": True,
                "output_pdf": str(pdf_file),
                "temp_dir": str(temp_dir),
                "color_mode": color_mode,
                "log": log_content,
                "message": f"Content compiled successfully: {section_name}",
            }
        else:
            return {
                "success": False,
                "output_pdf": None,
                "temp_dir": str(temp_dir),
                "color_mode": color_mode,
                "log": log_content,
                "stdout": result.stdout[-2000:]
                if len(result.stdout) > 2000
                else result.stdout,
                "stderr": result.stderr[-2000:]
                if len(result.stderr) > 2000
                else result.stderr,
                "error": f"Compilation failed with exit code {result.returncode}",
            }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Content compilation timed out after {timeout} seconds",
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
        }


def _setup_bibliography(temp_dir: Path, project_dir: str) -> None:
    """Set up bibliography files in temp directory."""
    project_path = resolve_project_path(project_dir)
    bib_dir = project_path / "00_shared" / "bib_files"
    if bib_dir.exists():
        for bib_file in bib_dir.glob("*.bib"):
            link_path = temp_dir / bib_file.name
            if not link_path.exists():
                link_path.symlink_to(bib_file)


def _read_log_file(temp_dir: Path, section_name: str) -> str:
    """Read and truncate log file content."""
    log_file = temp_dir / f"{section_name}.log"
    if log_file.exists():
        content = log_file.read_text(encoding="utf-8", errors="replace")
        return content[-5000:] if len(content) > 5000 else content
    return ""


def _cleanup_aux_files(temp_dir: Path, section_name: str) -> None:
    """Remove auxiliary files from compilation."""
    aux_extensions = [
        ".aux",
        ".log",
        ".fls",
        ".fdb_latexmk",
        ".synctex.gz",
        ".out",
        ".bbl",
        ".blg",
        ".toc",
        ".lof",
        ".lot",
    ]
    for ext in aux_extensions:
        aux_file = temp_dir / f"{section_name}{ext}"
        if aux_file.exists():
            aux_file.unlink()


def _inject_color_mode(latex_content: str, color_mode: str) -> str:
    """Inject color mode styling into an existing LaTeX document."""
    color_commands = _get_color_commands(color_mode)
    if not color_commands:
        return latex_content

    begin_doc_pattern = r"(\\begin\{document\})"
    match = re.search(begin_doc_pattern, latex_content)

    if match:
        insert_pos = match.end()
        return (
            latex_content[:insert_pos]
            + "\n"
            + color_commands
            + "\n"
            + latex_content[insert_pos:]
        )
    else:
        return color_commands + "\n" + latex_content


def _get_color_commands(color_mode: str) -> str:
    """Get LaTeX color commands for the specified color mode."""
    color_configs = {
        "light": "",
        "dark": """% Dark mode styling
\\pagecolor{black!95!white}
\\color{white}
\\makeatletter
\\@ifpackageloaded{hyperref}{%
  \\hypersetup{
    colorlinks=true,
    linkcolor=cyan!80!white,
    citecolor=green!70!white,
    urlcolor=blue!60!white,
  }%
}{}
\\makeatother""",
        "sepia": """% Sepia mode styling
\\pagecolor{Sepia!15!white}
\\color{black!85!Sepia}
\\makeatletter
\\@ifpackageloaded{hyperref}{%
  \\hypersetup{
    colorlinks=true,
    linkcolor=brown!70!black,
    citecolor=olive!70!black,
    urlcolor=teal!70!black,
  }%
}{}
\\makeatother""",
        "paper": "",
    }
    return color_configs.get(color_mode, "")


def _create_content_document(
    body_content: str, color_mode: str, project_dir: Optional[str]
) -> str:
    """Create a complete LaTeX document wrapping the body content."""
    color_commands = _get_color_commands(color_mode)
    bib_line = "\\bibliography{bibliography}" if project_dir else ""

    return f"""\\documentclass[11pt]{{article}}

% Essential packages
\\usepackage[english]{{babel}}
\\usepackage[T1]{{fontenc}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[table,svgnames]{{xcolor}}
\\usepackage{{amsmath, amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{hyperref}}
\\usepackage[numbers]{{natbib}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}
\\usepackage{{pagecolor}}

\\begin{{document}}
{color_commands}
{body_content}

{bib_line}
\\end{{document}}
"""


__all__ = ["compile_content"]

# EOF
