#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_editor/_templates/__init__.py

"""HTML/CSS/JS template builder for the Writer GUI.

Generates a complete single-page application with:
- File tree sidebar
- CodeMirror 5 LaTeX editor (CDN)
- pdf.js PDF preview (CDN)
- Compilation controls
- Dark/light mode
"""

from ._html import build_html_body
from ._scripts import build_scripts
from ._styles import build_styles

_CM_CDN = "https://cdnjs.cloudflare.com/ajax/libs/codemirror/5.65.16"
_PDF_CDN = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174"


def _build_head_links() -> str:
    """Build CDN link/script tags for the HTML head."""
    cm = _CM_CDN
    css_files = [
        "codemirror.min.css",
        "addon/fold/foldgutter.min.css",
        "addon/dialog/dialog.min.css",
    ]
    js_files = [
        "codemirror.min.js",
        "mode/stex/stex.min.js",
        "addon/edit/matchbrackets.min.js",
        "addon/edit/closebrackets.min.js",
        "addon/fold/foldcode.min.js",
        "addon/fold/foldgutter.min.js",
        "addon/fold/brace-fold.min.js",
        "addon/search/search.min.js",
        "addon/search/searchcursor.min.js",
        "addon/search/jump-to-line.min.js",
        "addon/dialog/dialog.min.js",
    ]
    lines = ["<!-- CodeMirror 5 -->"]
    for f in css_files:
        lines.append(f'<link rel="stylesheet" href="{cm}/{f}">')
    for f in js_files:
        lines.append(f'<script src="{cm}/{f}"></script>')
    lines.append("<!-- pdf.js -->")
    lines.append(f'<script src="{_PDF_CDN}/pdf.min.js"></script>')
    return "\n".join(lines)


def build_html(project_dir: str = "", dark_mode: bool = False) -> str:
    """Build the complete HTML document for the writer editor.

    Parameters
    ----------
    project_dir : str
        Project directory path for display.
    dark_mode : bool
        Initial dark mode state.

    Returns
    -------
    str
        Complete HTML document string.
    """
    theme_class = "dark" if dark_mode else "light"
    head_links = _build_head_links()
    styles = build_styles()
    body = build_html_body(project_dir)
    scripts = build_scripts()

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="{theme_class}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>SciTeX Writer</title>
{head_links}
{styles}
</head>
<body>
{body}
{scripts}
</body>
</html>"""


__all__ = ["build_html"]


# EOF
