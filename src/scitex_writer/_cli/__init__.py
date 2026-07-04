#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/__init__.py

"""scitex-writer CLI (Click-based, audit-compliant).

Thin orchestrator: the root group + dispatch live in ``._core`` and the
command groups live in ``.commands`` (imported here for its registration
side effect). This preserves the entry point ``scitex_writer._cli:main``
and the ``_cli.py`` re-export.

Subcommand groups:
    mcp        - MCP server commands
    guidelines - IMRAD writing guidelines (abstract/introduction/methods/...)
    prompts    - Action prompts (Asta)
    compile    - Compile LaTeX to PDF (manuscript/supplementary/revision/content)
    export     - Export manuscript for submission
    bib        - Bibliography management
    tables     - Table management
    figures    - Figure management
    gui        - Browser-based editor
    update     - Update engine files in a project
    migration  - Import/export Overleaf
    introspect - Python package introspection

Top-level convenience commands:
    list-python-apis   - alias for `introspect api scitex_writer`
    show-usage         - print the long usage guide

All LaTeX-domain command names (`compile manuscript`, `bib`, `figures`,
`tables`, etc.) are preserved verbatim — they are the canonical vocabulary
of the package and are referenced from skills, READMEs, and external docs.
"""

from __future__ import annotations

from ._core import main, main_group
from . import commands  # noqa: F401 (registers all commands on main_group)

__all__ = ["main", "main_group"]


# EOF
