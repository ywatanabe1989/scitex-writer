#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/citation_style.py

"""Citation-style functions.

Usage::

    import scitex_writer as sw
    result = sw.citation_style.apply("./my-paper", style="nature")

Sets the active ``\\bibliographystyle`` in 00_shared/latex_styles/bibliography.tex
(resolved from ``config/config_<doc>.yaml`` key ``citation.style`` or the
``SCITEX_WRITER_CITATION_STYLE`` env var when ``style`` is omitted). Pure-Python
port of ``scripts/shell/modules/apply_citation_style.sh``.
"""

from typing import Literal as _Literal
from typing import Optional as _Optional

from ._mcp.handlers._citation_style import apply as _apply

try:
    from scitex_dev.decorators import supports_return_as as _supports_return_as
except ImportError:  # scitex_dev optional -- degrade to a no-op decorator

    def _supports_return_as(fn):
        return fn


@_supports_return_as
def apply(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision"] = "manuscript",
    style: _Optional[str] = None,
) -> dict:
    """Set the active bibliography citation style in bibliography.tex.

    Returns ``{success, changed, current_style, new_style, backup_path,
    message, error}``.
    """
    return _apply(project_dir, doc_type, style)


__all__ = ["apply"]

# EOF
