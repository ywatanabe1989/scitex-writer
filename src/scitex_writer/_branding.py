#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/_branding.py

"""Branding configuration for white-label integration.

This module provides configurable branding for scitex-writer, allowing parent
packages (e.g., scitex.writer) to rebrand documentation and tool descriptions.

Environment Variables
---------------------
SCITEX_WRITER_BRAND : str
    Package name shown in docs (default: "scitex-writer")
SCITEX_WRITER_ALIAS : str
    Import alias shown in examples (default: "sw")

Usage
-----
Parent package sets env vars before importing:

    # scitex/writer/__init__.py
    import os
    os.environ["SCITEX_WRITER_BRAND"] = "scitex.writer"
    os.environ["SCITEX_WRITER_ALIAS"] = "sw"
    from scitex_writer import *

Then docstrings will show:
    >>> import scitex.writer as sw
    >>> sw.compile.manuscript("./my-paper")

Instead of:
    >>> import scitex_writer as sw
    >>> sw.compile.manuscript("./my-paper")
"""

import os
import re
from typing import Optional

# Read branding from environment
BRAND_NAME = os.environ.get("SCITEX_WRITER_BRAND", "scitex-writer")
BRAND_ALIAS = os.environ.get("SCITEX_WRITER_ALIAS", "sw")

# Original values (for reference/restoration)
_ORIGINAL_NAME = "scitex-writer"
_ORIGINAL_MODULE = "scitex_writer"
_ORIGINAL_ALIAS = "sw"


def rebrand_text(text: Optional[str]) -> Optional[str]:
    """Apply branding to a text string (e.g., docstring).

    Parameters
    ----------
    text : str or None
        Text to rebrand.

    Returns
    -------
    str or None
        Rebranded text, or None if input was None.

    Examples
    --------
    >>> os.environ["SCITEX_WRITER_BRAND"] = "mypackage"
    >>> os.environ["SCITEX_WRITER_ALIAS"] = "mp"
    >>> rebrand_text("import scitex_writer as sw")
    'import mypackage as mp'
    """
    if text is None:
        return None

    if BRAND_NAME == _ORIGINAL_NAME and BRAND_ALIAS == _ORIGINAL_ALIAS:
        return text

    result = text

    # Derive module name from brand (e.g., "scitex.writer" -> "scitex.writer")
    brand_module = BRAND_NAME.replace("-", "_")

    # Replace "import scitex_writer as sw" with "import BRAND as ALIAS"
    result = re.sub(
        rf"import\s+{_ORIGINAL_MODULE}\s+as\s+{_ORIGINAL_ALIAS}",
        f"import {brand_module} as {BRAND_ALIAS}",
        result,
    )

    # Replace "from scitex_writer" with "from BRAND"
    result = re.sub(
        rf"from\s+{_ORIGINAL_MODULE}(\s+import|\s*\.)",
        lambda m: f"from {brand_module}{m.group(1)}",
        result,
    )

    # Replace standalone "scitex-writer" (but not in URLs or paths)
    result = re.sub(
        rf"(?<![/.\w]){re.escape(_ORIGINAL_NAME)}(?=\s|$|[,.](?!\w))",
        BRAND_NAME,
        result,
    )

    # Replace " sw." with " ALIAS." (variable usage in examples)
    result = re.sub(
        rf"(\s){_ORIGINAL_ALIAS}\.",
        lambda m: f"{m.group(1)}{BRAND_ALIAS}.",
        result,
    )

    # Replace ">>> sw." with ">>> ALIAS." (doctest examples)
    result = re.sub(
        rf"(>>>\s+){_ORIGINAL_ALIAS}\.",
        lambda m: f"{m.group(1)}{BRAND_ALIAS}.",
        result,
    )

    return result


def rebrand_docstring(obj):
    """Apply branding to an object's docstring in-place.

    Parameters
    ----------
    obj : object
        Object with __doc__ attribute (function, class, module).

    Returns
    -------
    object
        The same object with rebranded docstring.
    """
    if hasattr(obj, "__doc__") and obj.__doc__:
        try:
            obj.__doc__ = rebrand_text(obj.__doc__)
        except AttributeError:
            # Some built-in objects have read-only __doc__
            pass
    return obj


def get_branded_import_example() -> str:
    """Get the branded import statement for documentation.

    Returns
    -------
    str
        Import statement like "import scitex_writer as sw" or "from scitex import writer as sw".
    """
    brand_module = BRAND_NAME.replace("-", "_")

    if BRAND_NAME == _ORIGINAL_NAME:
        return f"import {_ORIGINAL_MODULE} as {BRAND_ALIAS}"

    # For rebranded packages, check if it's a submodule
    if "." in brand_module:
        parts = brand_module.rsplit(".", 1)
        return f"from {parts[0]} import {parts[1]} as {BRAND_ALIAS}"
    else:
        return f"import {brand_module} as {BRAND_ALIAS}"


def get_mcp_server_name() -> str:
    """Get the MCP server name based on branding.

    Returns
    -------
    str
        Server name for MCP registration.
    """
    return BRAND_NAME.replace(".", "-")


def get_mcp_instructions() -> str:
    """Get branded MCP server instructions.

    Returns
    -------
    str
        Instructions text with branding applied.
    """
    instructions = f"""
================================================================================
{BRAND_NAME} - LaTeX Manuscript Compilation System
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
  {get_branded_import_example()}
  {BRAND_ALIAS}.compile.manuscript("./my-paper")
  {BRAND_ALIAS}.project.clone("./new-paper")

Compilation (BASH_ENV workaround for AI agents):
  env -u BASH_ENV /bin/bash -c '<SCITEX_WRITER_ROOT>/compile.sh manuscript --draft'

Options: --draft, --no_figs, --no_tables, --no_diff, --dark_mode, --quiet

Output: 01_manuscript/manuscript.pdf, manuscript_diff.pdf

Highlighting for User Review:
  \\hl{{[PLACEHOLDER: description]}}  - Content user must fill in
  \\hl{{[CHECK: reason]}}             - Claims/facts to verify
"""
    return instructions


# EOF
