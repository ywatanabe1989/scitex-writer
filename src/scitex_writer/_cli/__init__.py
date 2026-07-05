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

from . import commands  # noqa: F401 (registers all commands on main_group)
from ._core import main, main_group

# Backward-compat re-exports: before the monolith split every subcommand
# group (``bib_group``, ``compile_group``, ...) lived directly in this
# module's namespace. Command bodies now live in ``.commands.<mod>``, but
# the group objects are re-exported here so ``scitex_writer._cli.bib_group``
# (etc.) keeps working for any caller/test that imports them off this
# module, per the module docstring's "preserves ... the ``_cli.py``
# re-export" guarantee.
from .commands.bib import bib_group
from .commands.compile import compile_group
from .commands.export import export_group
from .commands.figures import figures_group
from .commands.guidelines import guidelines_group
from .commands.introspect import introspect_group
from .commands.mcp import mcp_group
from .commands.migration import migration_group
from .commands.prompts import prompts_group
from .commands.tables import tables_group

__all__ = [
    "main",
    "main_group",
    "bib_group",
    "compile_group",
    "export_group",
    "figures_group",
    "guidelines_group",
    "introspect_group",
    "mcp_group",
    "migration_group",
    "prompts_group",
    "tables_group",
]


# EOF
