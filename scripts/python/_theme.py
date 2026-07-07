#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/python/_theme.py
# Purpose: Theme (light/dark) resolution for the compile flow. Extracted from
#          compile_tex_structure.py to keep that orchestrator under the line
#          limit; pure helpers, no public-API change.

import os
import sys
from pathlib import Path


def read_config_theme(base_tex: Path) -> str:
    """Read ``theme:`` from config/config_<doctype>.yaml — returns 'light' or 'dark'.

    The project root is the parent of the document dir holding base.tex (e.g.
    ``<root>/01_manuscript/base.tex`` -> ``<root>``), matching how the
    dark_mode.tex path is resolved in the compile flow.

    Fail loud (SystemExit) on an invalid theme value so a typo cannot silently
    render the wrong theme. A missing file / missing PyYAML / unreadable YAML
    degrade to 'light' (the knob simply has no effect).
    """
    doc_type = os.getenv("SCITEX_WRITER_DOC_TYPE", "manuscript")
    config_path = (
        base_tex.resolve().parent.parent / "config" / f"config_{doc_type}.yaml"
    )
    if not config_path.exists():
        return "light"
    try:
        import yaml
    except ImportError:
        return "light"
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return "light"
    theme = data.get("theme", "light")
    theme = "light" if theme is None else str(theme).strip().lower()
    if theme not in ("light", "dark"):
        print(
            f"ERROR: Invalid theme '{theme}' in {config_path.name} — "
            f"must be 'light' or 'dark'.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return theme


def resolve_dark_mode(explicit_flag: bool, base_tex: Path) -> bool:
    """Resolve effective dark mode with precedence.

    ``--dark-mode`` flag > ``SCITEX_WRITER_DARK_MODE`` env > config ``theme:``
    > light. Only a *set* (non-empty) env var short-circuits the config, so
    ``theme: dark`` takes effect when no flag/env is supplied.
    """
    if explicit_flag:
        return True
    env = os.getenv("SCITEX_WRITER_DARK_MODE")
    if env is not None and env.strip() != "":
        return env.strip().lower() == "true"
    return read_config_theme(base_tex) == "dark"


__all__ = ["read_config_theme", "resolve_dark_mode"]

# EOF
