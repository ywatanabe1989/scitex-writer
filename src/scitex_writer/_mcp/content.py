#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-08
# File: src/scitex_writer/_mcp/content.py

"""Content compilation for LaTeX snippets and sections.

Thin wrapper delegating to _compile.content for business logic.
"""

from __future__ import annotations

from typing import Literal, Optional

from .._compile.content import compile_content as _compile_content


def compile_content(
    latex_content: str,
    project_dir: Optional[str] = None,
    color_mode: Literal["light", "dark"] = "light",
    name: str = "content",
    timeout: int = 60,
    keep_aux: bool = False,
) -> dict:
    """Compile raw LaTeX content to PDF.

    Thin wrapper around _compile.content.compile_content.
    See that module for full documentation.
    """
    return _compile_content(
        latex_content,
        project_dir=project_dir,
        color_mode=color_mode,
        name=name,
        timeout=timeout,
        keep_aux=keep_aux,
    )


__all__ = ["compile_content"]

# EOF
