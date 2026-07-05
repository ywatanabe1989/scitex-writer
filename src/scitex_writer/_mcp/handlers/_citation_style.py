#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_citation_style.py

"""Citation-style handler: set the active \\bibliographystyle in bibliography.tex.

A pure-Python port of ``scripts/shell/modules/apply_citation_style.sh``. Line-based
(no ``sed`` escaping pitfalls): find the ACTIVE (uncommented, line-start)
``\\bibliographystyle``; if it already matches the target, no-op; else back up the
file, comment out the active style line(s), uncomment ``% \\bibliographystyle{target}``
if the target is present as a commented option, else insert it into the
bibliographystyle block. Fail-loud on a missing bib file; honest no-op when no
style is configured.
"""

import os
import re
from pathlib import Path
from typing import Optional

from ..._dataclasses import CitationStyleResult
from ..utils import resolve_project_path

BIB_REL = "00_shared/latex_styles/bibliography.tex"
DOC_DIRS = {
    "manuscript": "01_manuscript",
    "supplementary": "02_supplementary",
    "revision": "03_revision",
}

# Active (uncommented) \bibliographystyle{...} at line start (allow leading ws).
_ACTIVE_RE = re.compile(r"^([ \t]*)\\bibliographystyle\{([^}]*)\}")
# Any \bibliographystyle line (active OR commented) -- to locate the block.
_ANY_RE = re.compile(r"\\bibliographystyle\{([^}]*)\}")
# The environment variable the shell read (config .citation.style is mapped to it).
_ENV_VAR = "SCITEX_WRITER_CITATION_STYLE"


def _resolve_style(
    project_path: Path, doc_type: str, style: Optional[str]
) -> Optional[str]:
    """Target style: explicit arg > config ``citation.style`` > env; else None."""
    if style:
        return style
    config_path = project_path / "config" / f"config_{doc_type}.yaml"
    if config_path.is_file():
        try:
            import yaml

            data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
            citation = data.get("citation") if isinstance(data, dict) else None
            if isinstance(citation, dict) and citation.get("style"):
                return str(citation["style"]).strip()
        except Exception:
            pass  # config unreadable -> fall through to env (advisory, not fatal)
    env = os.environ.get(_ENV_VAR)
    return env.strip() if env else None


def apply(
    project_dir: str, doc_type: str = "manuscript", style: Optional[str] = None
) -> dict:
    """Set the active bibliography citation style in bibliography.tex.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project directory.
    doc_type : str
        One of 'manuscript' (default), 'supplementary', 'revision'.
    style : str, optional
        Target style (e.g. 'nature', 'ieee'). When omitted, resolved from
        ``config/config_<doc_type>.yaml`` key ``citation.style`` or the
        ``SCITEX_WRITER_CITATION_STYLE`` env var.

    Returns
    -------
    dict
        Serialized :class:`CitationStyleResult`. Fail-loud (explicit error) on a
        missing bib file; honest no-op (success, changed=False) when no style is
        configured or the style is already active.
    """
    try:
        if doc_type not in DOC_DIRS:
            return {
                "success": False,
                "error": (
                    f"Invalid doc_type '{doc_type}'. Must be one of: {tuple(DOC_DIRS)}"
                ),
            }

        project_path = resolve_project_path(project_dir)
        target = _resolve_style(project_path, doc_type, style)
        if not target:
            return CitationStyleResult(
                success=True,
                changed=False,
                message=(
                    "No citation style configured "
                    "(config citation.style / SCITEX_WRITER_CITATION_STYLE); "
                    "leaving bibliography.tex unchanged."
                ),
            ).to_dict()

        bib = project_path / BIB_REL
        if not bib.is_file():
            return {
                "success": False,
                "error": (
                    f"Bibliography file not found: {bib}. "
                    f"Run `scitex-writer update-project` or check the project layout."
                ),
            }

        lines = bib.read_text(encoding="utf-8").splitlines(keepends=True)

        current = None
        for ln in lines:
            m = _ACTIVE_RE.match(ln)
            if m:
                current = m.group(2)
                break

        if current == target:
            result = CitationStyleResult(
                success=True,
                changed=False,
                current_style=current,
                new_style=target,
                message=f"Citation style already set to '{target}'.",
            )
            result.validate()
            return result.to_dict()

        backup = bib.with_suffix(bib.suffix + ".bak")
        backup.write_text("".join(lines), encoding="utf-8")

        # Comment out every active \bibliographystyle line.
        new_lines = ["% " + ln if _ACTIVE_RE.match(ln) else ln for ln in lines]

        # Uncomment the target if it exists as a commented option, else insert it.
        commented_re = re.compile(
            r"^%+\s*\\bibliographystyle\{" + re.escape(target) + r"\}"
        )
        uncommented = False
        for i, ln in enumerate(new_lines):
            if commented_re.match(ln):
                new_lines[i] = re.sub(r"^%+\s?", "", ln)
                uncommented = True
                break

        if not uncommented:
            # Insert after the LAST \bibliographystyle-related line so it lands in
            # the style block; append if there is none.
            insert_at = None
            for i, ln in enumerate(new_lines):
                if _ANY_RE.search(ln):
                    insert_at = i + 1
            newline = f"\\bibliographystyle{{{target}}}\n"
            if insert_at is None:
                new_lines.append(newline)
            else:
                new_lines.insert(insert_at, newline)

        bib.write_text("".join(new_lines), encoding="utf-8")

        result = CitationStyleResult(
            success=True,
            changed=True,
            current_style=current,
            new_style=target,
            backup_path=str(backup),
            message=f"Citation style changed: {current} -> {target}",
        )
        result.validate()
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": str(e)}


__all__ = ["apply"]

# EOF
