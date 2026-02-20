#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_claim.py

"""Claim handlers: CRUD for 00_shared/claims.json and LaTeX rendering.

Claims are traceable scientific assertions — statistics, values, citations, figure
references — stored as structured objects instead of magic numbers.

Usage in LaTeX (after render_claims is called before compile):
    \\stxclaim{group_comparison}           % nature style (default)
    \\stxclaim[apa]{group_comparison}      % APA style
    \\stxclaim[plain]{group_comparison}    % plain text
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Optional

from ..utils import resolve_project_path

CLAIM_TYPES = ("statistic", "value", "citation", "figure", "table")
FORMAT_STYLES = ("nature", "apa", "plain")
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


def _sanitize_id(claim_id: str) -> str:
    """Sanitize claim ID for use in LaTeX macro names (letters only)."""
    return re.sub(r"[^a-zA-Z0-9]", "", claim_id)


def _format_p(p: float, style: str) -> str:
    """Format p-value according to style."""
    if p < 0.001:
        return "< 0.001" if style != "apa" else "< .001"
    if p < 0.01:
        fmt = f"{p:.3f}"
        return fmt if style != "apa" else fmt.lstrip("0")
    fmt = f"{p:.3f}"
    return f"= {fmt}" if style != "apa" else f"= {fmt.lstrip('0')}"


def _format_statistic(value: Dict, style: str) -> str:
    """Format a statistic claim."""
    t = value.get("t")
    f = value.get("F")
    df = value.get("df")
    df1 = value.get("df1")
    df2 = value.get("df2")
    p = value.get("p")
    d = value.get("d")
    eta2 = value.get("eta2")
    r = value.get("r")

    parts = []

    if t is not None and df is not None:
        if style == "plain":
            parts.append(f"t({df}) = {t:.2f}")
        else:
            parts.append(f"$t({df}) = {t:.2f}$")
    elif f is not None and df1 is not None and df2 is not None:
        if style == "plain":
            parts.append(f"F({df1},{df2}) = {f:.2f}")
        else:
            parts.append(f"$F({df1},{df2}) = {f:.2f}$")
    elif r is not None:
        if style == "plain":
            parts.append(f"r = {r:.2f}")
        else:
            parts.append(f"$r = {r:.2f}$")

    if p is not None:
        p_str = _format_p(p, style)
        if style == "plain":
            parts.append(f"p {p_str}")
        else:
            parts.append(f"$p {p_str}$")

    if d is not None:
        if style == "apa":
            label = "Cohen's $d$"
            val_str = f"{d:.2f}"
            parts.append(f"{label} = {val_str}")
        elif style == "plain":
            parts.append(f"d = {d:.2f}")
        else:
            parts.append(f"$d = {d:.2f}$")
    elif eta2 is not None:
        if style == "plain":
            parts.append(f"eta2 = {eta2:.3f}")
        else:
            label = "$\\eta^2$" if style == "nature" else "$\\eta^2_p$"
            parts.append(f"{label} = {eta2:.3f}")

    return ", ".join(parts) if parts else str(value)


def _format_value(value: Dict, style: str) -> str:
    """Format a value claim."""
    v = value.get("value", "")
    unit = value.get("unit", "")
    if unit:
        return f"{v} {unit}" if style == "plain" else f"${v}$ {unit}"
    return str(v)


def _format_citation(value: Dict, style: str) -> str:
    """Format a citation claim — just returns user-supplied text."""
    return str(value.get("text", ""))


def _format_figure(value: Dict, style: str) -> str:
    """Format a figure reference."""
    label = value.get("label", "")
    return f"\\ref{{{label}}}"


def _format_table(value: Dict, style: str) -> str:
    """Format a table reference."""
    label = value.get("label", "")
    return f"\\ref{{{label}}}"


def _render_claim(claim: Dict, style: str) -> str:
    """Render a single claim as a LaTeX string."""
    claim_type = claim.get("type", "value")
    value = claim.get("value", {})
    if isinstance(value, str):
        return value
    formatters = {
        "statistic": _format_statistic,
        "value": _format_value,
        "citation": _format_citation,
        "figure": _format_figure,
        "table": _format_table,
    }
    fn = formatters.get(claim_type, _format_value)
    return fn(value, style)


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
        Unique identifier (e.g., "group_comparison"). Used in \\stxclaim{id}.
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
            "latex_usage": f"\\stxclaim{{{claim_id}}}",
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
            "latex_usage": f"\\stxclaim{{{claim_id}}}",
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
    The generated file defines the \\stxclaim{id} LaTeX macro and all claim
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
            "%% To update: run writer_render_claims or recompile the project.",
            "",
            "\\makeatletter",
            "",
            "%% \\stxclaim[style]{id} — render a claim inline",
            "\\@ifundefined{stxclaim}{%",
            "  \\newcommand{\\stxclaim}[2][nature]{%",
            "    \\@ifundefined{stx@claim@#2@#1}{[\\texttt{claim:#2}]}{%",
            "      \\csname stx@claim@#2@#1\\endcsname}%",
            "  }%",
            "}{}",
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
            for style in FORMAT_STYLES:
                rendered = _render_claim(claim, style)
                macro_name = f"stx@claim@{safe_id}@{style}"
                lines.append(f"\\@namedef{{{macro_name}}}{{{rendered}}}")
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
