#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-01-27
# File: src/scitex_writer/guidelines/__init__.py

"""IMRAD writing guidelines for scientific manuscripts.

Guidelines are templates/tips for writing manuscript sections.
Prompts can be built from guidelines + user content.

Usage::

    from scitex_writer.guidelines import get, build, list_sections

    # Get raw guidelines
    tips = get("abstract")

    # Build prompt with draft
    prompt = build("abstract", draft="My draft text...")

Custom guidelines via environment variables:
    SCITEX_WRITER_GUIDELINE_ABSTRACT=/path/to/custom.md
    SCITEX_WRITER_GUIDELINE_DIR=/path/to/guidelines/
"""

import os as _os
from pathlib import Path as _Path

# Available sections
SECTIONS = ["abstract", "introduction", "methods", "discussion", "proofread"]

# Default data directory
_DEFAULT_DIR = _Path(__file__).parent

__all__ = ["SECTIONS", "get", "build", "list_sections", "get_source"]


def _get_path(section: str) -> _Path:
    """Get path to guideline file, checking env overrides first."""
    env_key = f"SCITEX_WRITER_GUIDELINE_{section.upper()}"
    if env_path := _os.environ.get(env_key):
        return _Path(env_path)

    if guideline_dir := _os.environ.get("SCITEX_WRITER_GUIDELINE_DIR"):
        custom_path = _Path(guideline_dir) / f"{section}.md"
        if custom_path.exists():
            return custom_path

    return _DEFAULT_DIR / f"{section}_.md"


def get(section: str) -> str:
    """Get writing guidelines for a manuscript section.

    Args:
        section: One of: abstract, introduction, methods, discussion, proofread

    Returns:
        Guidelines markdown content with PLACEHOLDER marker.

    Raises:
        ValueError: If section is not recognized.
        FileNotFoundError: If guidelines file not found.
    """
    section = section.lower().strip()

    if section not in SECTIONS:
        raise ValueError(
            f"Unknown section: '{section}'. Available: {', '.join(SECTIONS)}"
        )

    path = _get_path(section)

    if not path.exists():
        raise FileNotFoundError(f"Guidelines not found: {path}")

    return path.read_text(encoding="utf-8")


def build(section: str, draft: str, placeholder: str = "PLACEHOLDER") -> str:
    """Build a prompt from guidelines and user draft.

    Args:
        section: Section name.
        draft: User's draft text.
        placeholder: Placeholder to replace (default: PLACEHOLDER).

    Returns:
        Complete prompt with draft inserted.
    """
    template = get(section)
    return template.replace(placeholder, draft)


def list_sections() -> list[str]:
    """List available sections."""
    return SECTIONS.copy()


def get_source(section: str) -> dict[str, str]:
    """Get info about where guidelines are loaded from."""
    section = section.lower().strip()

    env_key = f"SCITEX_WRITER_GUIDELINE_{section.upper()}"
    if env_path := _os.environ.get(env_key):
        return {"path": env_path, "source": "env"}

    if guideline_dir := _os.environ.get("SCITEX_WRITER_GUIDELINE_DIR"):
        custom_path = _Path(guideline_dir) / f"{section}.md"
        if custom_path.exists():
            return {"path": str(custom_path), "source": "custom_dir"}

    return {"path": str(_DEFAULT_DIR / f"{section}_.md"), "source": "default"}


# EOF
