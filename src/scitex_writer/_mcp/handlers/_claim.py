#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_claim.py

"""Claim handlers: CRUD for 00_shared/claims.json and LaTeX rendering.

Claims are traceable scientific assertions — statistics, values, citations, figure
references — stored as structured objects instead of magic numbers.

Usage in LaTeX (after render_claims is called before compile):
    \\vclaim{group_comparison}           % nature style (default)
    \\vclaim[apa]{group_comparison}      % APA style
    \\vclaim[plain]{group_comparison}    % plain text
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils import resolve_project_path
from ._claim_format import (
    CLAIM_TYPES,
    FORMAT_STYLES,
    _render_claim,
    _sanitize_id,
)

CLAIMS_FILE = "00_shared/claims.json"
CLAIMS_RENDERED = "00_shared/claims_rendered.tex"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _claims_path(project_path: Path) -> Path:
    return project_path / CLAIMS_FILE


def _load_claims(project_path: Path) -> Dict:
    """Load claims.json, returning empty structure if not found."""
    p = _claims_path(project_path)
    if not p.exists():
        return {"version": "1.0", "claims": {}}
    return json.loads(p.read_text(encoding="utf-8"))


def _save_claims(project_path: Path, data: Dict) -> None:
    """Write claims.json with consistent formatting."""
    p = _claims_path(project_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Public handler functions
# ---------------------------------------------------------------------------


def add_claim(
    project_dir: str,
    claim_id: str,
    claim_type: str,
    value: Dict[str, Any],
    context: Optional[str] = None,
    session_id: Optional[str] = None,
    output_file: Optional[str] = None,
    output_hash: Optional[str] = None,
    test: Optional[str] = None,
) -> Dict:
    """Add or update a claim in 00_shared/claims.json.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project directory.
    claim_id : str
        Unique identifier (e.g., "group_comparison"). Used in \\vclaim{id}.
    claim_type : str
        One of: statistic, value, citation, figure, table.
    value : dict
        The claim's data. For statistic: {t, df, p, d} or {F, df1, df2, p, eta2}.
        For value: {value, unit}. For citation: {text}. For figure/table: {label}.
    context : str, optional
        Human-readable description of what this claim represents.
    session_id : str, optional
        Session ID that produced this claim (for Clew traceability).
    output_file : str, optional
        File that produced this value (for Clew traceability).
    output_hash : str, optional
        SHA-256 hash of output_file at time of claim creation.
    test : str, optional
        Statistical test name (e.g., "welch_t_test") for statistic claims.

    Returns
    -------
    dict
        Success status and rendered preview for each style.
    """
    try:
        if claim_type not in CLAIM_TYPES:
            return {
                "success": False,
                "error": f"Invalid claim_type '{claim_type}'. Must be one of: {CLAIM_TYPES}",
            }

        project_path = resolve_project_path(project_dir)
        data = _load_claims(project_path)

        entry: Dict[str, Any] = {
            "type": claim_type,
            "value": value,
            "context": context,
            "session_id": session_id,
            "output_file": output_file,
            "output_hash": output_hash,
        }
        if test:
            entry["test"] = test

        data["claims"][claim_id] = entry
        _save_claims(project_path, data)

        previews = {style: _render_claim(entry, style) for style in FORMAT_STYLES}

        return {
            "success": True,
            "claim_id": claim_id,
            "claim_type": claim_type,
            "previews": previews,
            "latex_usage": f"\\vclaim{{{claim_id}}}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def list_claims(project_dir: str) -> Dict:
    """List all claims in the project.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project directory.

    Returns
    -------
    dict
        List of claims with formatted previews.
    """
    try:
        project_path = resolve_project_path(project_dir)
        data = _load_claims(project_path)
        claims = data.get("claims", {})

        result = []
        for claim_id, claim in claims.items():
            preview = _render_claim(claim, "nature")
            result.append(
                {
                    "claim_id": claim_id,
                    "type": claim.get("type", "unknown"),
                    "context": claim.get("context", ""),
                    "preview_nature": preview,
                    "has_provenance": bool(
                        claim.get("session_id") or claim.get("output_file")
                    ),
                }
            )

        return {"success": True, "count": len(result), "claims": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_claim(project_dir: str, claim_id: str) -> Dict:
    """Get details of a specific claim.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project directory.
    claim_id : str
        Claim identifier.

    Returns
    -------
    dict
        Full claim data including rendered previews for all styles.
    """
    try:
        project_path = resolve_project_path(project_dir)
        data = _load_claims(project_path)
        claim = data.get("claims", {}).get(claim_id)

        if claim is None:
            return {"success": False, "error": f"Claim not found: '{claim_id}'"}

        previews = {style: _render_claim(claim, style) for style in FORMAT_STYLES}

        return {
            "success": True,
            "claim_id": claim_id,
            "claim": claim,
            "previews": previews,
            "latex_usage": f"\\vclaim{{{claim_id}}}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def remove_claim(project_dir: str, claim_id: str) -> Dict:
    """Remove a claim from the project.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project directory.
    claim_id : str
        Claim identifier to remove.

    Returns
    -------
    dict
        Success status.
    """
    try:
        project_path = resolve_project_path(project_dir)
        data = _load_claims(project_path)

        if claim_id not in data.get("claims", {}):
            return {"success": False, "error": f"Claim not found: '{claim_id}'"}

        del data["claims"][claim_id]
        _save_claims(project_path, data)

        return {"success": True, "removed": claim_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


def format_claim(project_dir: str, claim_id: str, style: str = "nature") -> Dict:
    """Format a claim as a LaTeX string.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project directory.
    claim_id : str
        Claim identifier.
    style : str
        Format style: 'nature' (default), 'apa', or 'plain'.

    Returns
    -------
    dict
        Formatted LaTeX string for the claim.
    """
    try:
        if style not in FORMAT_STYLES:
            return {
                "success": False,
                "error": f"Invalid style '{style}'. Must be one of: {FORMAT_STYLES}",
            }

        project_path = resolve_project_path(project_dir)
        data = _load_claims(project_path)
        claim = data.get("claims", {}).get(claim_id)

        if claim is None:
            return {"success": False, "error": f"Claim not found: '{claim_id}'"}

        rendered = _render_claim(claim, style)

        return {
            "success": True,
            "claim_id": claim_id,
            "style": style,
            "rendered": rendered,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def render_claims(project_dir: str) -> Dict:
    """Render all claims to 00_shared/claims_rendered.tex.

    This is called automatically before compilation when claims.json exists.
    The generated file defines the \\vclaim{id} LaTeX macro and all claim
    renderings for all styles.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project directory.

    Returns
    -------
    dict
        Success status and path to generated file.
    """
    try:
        project_path = resolve_project_path(project_dir)
        data = _load_claims(project_path)
        claims = data.get("claims", {})

        lines = [
            "%% Auto-generated by scitex-writer — do not edit manually.",
            f"%% Source: {CLAIMS_FILE}",
            "%% To update: run writer_claim_render or recompile the project.",
            "",
            "\\makeatletter",
            "",
            "%% \\vclaim[style]{id} — render a claim inline",
            "%% Note: #-tokens doubled to ## so this block survives being",
            "%% inlined inside another macro's body (e.g., the BODY position",
            "%% of \\IfFileExists{file}{BODY}{}). Single # also works at the",
            "%% top level, so ## is the portable choice.",
            "\\providecommand{\\vclaim}[2][nature]{%",
            "  \\expandafter\\ifx\\csname v@claim@##2@##1\\endcsname\\relax",
            "    [\\texttt{claim:##2}]%",
            "  \\else",
            "    \\v@claim@maybecolor{##2}{\\csname v@claim@##2@##1\\endcsname}%",
            "  \\fi}",
            "",
            "%% \\v@claim@maybecolor{id}{rendered} — clew provenance overlay.",
            "%% When the clew presentation markers layer is ACTIVE",
            "%% (\\ifclewpresmarkers, set by --clew-overlay / the master switch)",
            "%% AND this claim id has a clew color registered (clew@hex@<id>, emitted",
            "%% into clew_rendered.tex by render_clew using the SAME sanitize as the",
            "%% v@claim@ names, so keys align), wrap the rendered value in the",
            "%% verdict-colored decoration the clew layer uses (\\clewDecorate — the",
            "%% ulem \\uwave span). The value is \\mbox-wrapped first: the \\vclaim",
            '%% value macro bundles a \\hypertarget, and ulem \\uwave chokes ("Bad',
            '%% space factor (0)") on that box unless it is a single \\hbox; claim',
            "%% values are short single units, so this is safe. Falls back to the",
            "%% PLAIN rendered value (no \\mbox, no wave) in every",
            "%% other case, guarded by \\@ifundefined so a non-overlay compile (no",
            "%% clew_rendered.tex, markers off, or claim absent from the clew feed)",
            "%% never touches an undefined color/toggle macro.",
            "\\providecommand{\\v@claim@maybecolor}[2]{%",
            "  \\@ifundefined{clew@hex@##1}{##2}{%",
            "    \\@ifundefined{ifclewpresmarkers}{##2}{%",
            "      \\ifclewpresmarkers",
            "        \\begingroup",
            "        \\edef\\v@claim@clewhex{\\csname clew@hex@##1\\endcsname}%",
            "        \\definecolor{clewVerdict}{HTML}{\\v@claim@clewhex}%",
            "        \\clewDecorate{\\mbox{##2}}%",
            "        \\endgroup",
            "      \\else ##2\\fi}}%",
            "}",
            "",
        ]

        if claims:
            lines.append("%% Rendered claims")
        else:
            lines.append("%% No claims defined yet.")

        for claim_id, claim in claims.items():
            safe_id = _sanitize_id(claim_id)
            context = claim.get("context", "")
            claim_type = claim.get("type", "unknown")
            lines.append(
                f"%% {claim_id} ({claim_type}){': ' + context if context else ''}"
            )
            # First rendering in the document creates a named PDF destination
            # via \hypertarget{vclaim-<id>}{…} — Living Paper (#133) uses this
            # so PDF.js can locate claim text for hover popups. Subsequent
            # calls don't re-emit the target (hyperref would warn on dup);
            # instead we use a one-shot flag per claim.
            flag = f"v@claim@{safe_id}@anchored"
            for style in FORMAT_STYLES:
                rendered = _render_claim(claim, style)
                macro_name = f"v@claim@{safe_id}@{style}"
                wrapped = (
                    f"\\expandafter\\ifx\\csname {flag}\\endcsname\\relax"
                    f"\\global\\@namedef{{{flag}}}{{}}"
                    f"\\hypertarget{{vclaim-{safe_id}}}{{{rendered}}}"
                    f"\\else {rendered}\\fi"
                )
                lines.append(f"\\@namedef{{{macro_name}}}{{{wrapped}}}")
            lines.append("")

        lines.append("\\makeatother")

        output_path = project_path / CLAIMS_RENDERED
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        return {
            "success": True,
            "rendered_path": str(output_path),
            "claims_count": len(claims),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


__all__ = [
    "CLAIM_TYPES",
    "FORMAT_STYLES",
    "add_claim",
    "list_claims",
    "get_claim",
    "remove_claim",
    "format_claim",
    "render_claims",
]

# EOF
