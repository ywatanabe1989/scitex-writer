#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-08
# File: scripts/python/compile_content_document.py

"""Build a complete LaTeX document from body content with color mode support.

Usage:
    python compile_content_document.py --body-file body.tex --output out.tex --color-mode dark
    python compile_content_document.py --body-text "\\section{Test}" --output out.tex
    python compile_content_document.py --body-file full.tex --output out.tex --complete-document
"""

import argparse
import re
import sys
from pathlib import Path

# Monaco/VS Code dark theme colors (single source of truth)
MONACO_BG = "1E1E1E"
MONACO_FG = "D4D4D4"

DARK_MODE_COMMANDS = f"""\
% Dark mode styling - matches Monaco/VS Code editor (#{MONACO_BG})
\\definecolor{{MonacoBg}}{{HTML}}{{{MONACO_BG}}}
\\definecolor{{MonacoFg}}{{HTML}}{{{MONACO_FG}}}
\\pagecolor{{MonacoBg}}
\\color{{MonacoFg}}
\\makeatletter
\\@ifpackageloaded{{hyperref}}{{%
  \\hypersetup{{
    colorlinks=true,
    linkcolor=cyan!80!white,
    citecolor=green!70!white,
    urlcolor=blue!60!white,
  }}%
}}{{}}
\\makeatother"""

DOCUMENT_TEMPLATE = """\
\\documentclass[11pt]{{article}}

% Essential packages
\\usepackage[english]{{babel}}
\\usepackage[T1]{{fontenc}}
\\usepackage[utf8]{{inputenc}}
\\usepackage[table,svgnames]{{xcolor}}
\\usepackage{{amsmath, amssymb}}
\\usepackage{{graphicx}}
\\usepackage{{booktabs}}
\\usepackage{{hyperref}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}
\\usepackage{{pagecolor}}

\\begin{{document}}
{color_commands}
{body_content}

\\end{{document}}
"""


def get_color_commands(color_mode: str) -> str:
    """Get LaTeX color commands for the specified mode."""
    if color_mode == "dark":
        return DARK_MODE_COMMANDS
    return ""


def inject_color_into_document(latex_content: str, color_mode: str) -> str:
    """Inject color mode styling into an existing complete LaTeX document."""
    color_commands = get_color_commands(color_mode)
    if not color_commands:
        return latex_content

    pattern = r"(\\begin\{document\})"
    match = re.search(pattern, latex_content)

    if match:
        pos = match.end()
        return latex_content[:pos] + "\n" + color_commands + "\n" + latex_content[pos:]
    return color_commands + "\n" + latex_content


def wrap_body_content(body_content: str, color_mode: str) -> str:
    """Wrap body content into a complete LaTeX document."""
    color_commands = get_color_commands(color_mode)
    return DOCUMENT_TEMPLATE.format(
        color_commands=color_commands,
        body_content=body_content,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Build LaTeX document from body content with color mode."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--body-file", help="File containing LaTeX body content")
    group.add_argument("--body-text", help="Inline LaTeX body content")
    parser.add_argument("--output", required=True, help="Output .tex file path")
    parser.add_argument(
        "--color-mode",
        default="light",
        choices=["light", "dark"],
        help="Color mode (default: light)",
    )
    parser.add_argument(
        "--complete-document",
        action="store_true",
        help="Input is a complete document (inject color only)",
    )
    args = parser.parse_args()

    # Read body content
    if args.body_file:
        body_path = Path(args.body_file)
        if not body_path.exists():
            print(f"ERROR: Body file not found: {args.body_file}", file=sys.stderr)
            sys.exit(1)
        content = body_path.read_text(encoding="utf-8")
    else:
        content = args.body_text

    # Build document
    if args.complete_document:
        result = inject_color_into_document(content, args.color_mode)
    else:
        result = wrap_body_content(content, args.color_mode)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(result, encoding="utf-8")

    print(f"Document written: {args.output}")


if __name__ == "__main__":
    main()

# EOF
