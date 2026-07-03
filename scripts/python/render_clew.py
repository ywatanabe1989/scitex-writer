#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/render_clew.py
# Purpose: Pre-compile generation step -- emit 00_shared/clew_rendered.tex from
#          scitex-clew's runtime export (.scitex/clew/runtime/claims.json,
#          schema v1.3) before the manuscript is flattened. scitex-clew stays
#          RENDERER-AGNOSTIC (it exports JSON, not TeX by design), so turning
#          that JSON into the LaTeX the clew presentation layer consumes is
#          WRITER's job. packages.tex already \input{00_shared/clew_rendered.tex}
#          (skipped if absent), so once this writes the file it is picked up.
#
#          Output contract (see 00_shared/latex_styles/clew_presentation.tex +
#          demo/clew_rendered.sample.tex):
#            \makeatletter
#            \definecolor{clewVerified|Suspect|Unsourced|Unverified|Exception}{HTML}{hex}
#            \def\clew@total{N} \def\clew@verified{M} \def\clew@allverified{0|1}
#            \@namedef{clew@val@<id>}{value}      (id sanitized to [a-zA-Z0-9])
#            \@namedef{clew@hex@<id>}{6hex}
#            \@namedef{clew@status@<id>}{status}
#            \makeatother
#
#          Claim VALUES are emitted VERBATIM -- clew provides display-ready
#          strings (the sample carries intentional math like $\times$ and
#          pre-escaped \_), so we do NOT re-escape (that would double-escape).
#
#          FAIL LOUD: if claims.json exists but is malformed / unreadable, exit
#          non-zero so the compile aborts rather than shipping a stale or empty
#          clew_rendered.tex. No-op (exit 0) when claims.json is absent -- the
#          clew layer is optional.
#
# Usage:
#   python render_clew.py [project_dir]

import json
import re
import sys
from pathlib import Path

CLAIMS_JSON = ".scitex/clew/runtime/claims.json"
OUTPUT_TEX = "00_shared/clew_rendered.tex"

# status -> the \definecolor name the presentation layer expects.
# `unsourced` (clew unified 1.6 / claims.json 1.4, additive) is its OWN amber
# bucket -- "unproven, not wrong" -- distinct from the red `unverified`/`failed`
# mismatch-or-missing state; it is NOT folded into red.
_STATUS_COLOR = {
    "verified": "clewVerified",
    "suspect": "clewSuspect",
    "unsourced": "clewUnsourced",
    "unverified": "clewUnverified",
    "exception": "clewException",
}
# Schema-version tolerance: clew's unified feed 1.5 RENAMED the red state
# "unverified" -> "failed" (and 1.3 claims.json "partial" -> "suspect").
# Normalize incoming status/palette keys to the internal buckets above, so
# BOTH the pre-1.5 and 1.5+ feeds render correctly with no version gate.
# `unsourced` is deliberately absent here: it is its own bucket, never a synonym.
_STATUS_SYNONYMS = {
    "failed": "unverified",
    "partial": "suspect",
}
# Fallback palette (matches clew_presentation.tex's \providecolor + the sample);
# only used when claims.json does not carry a palette hex for a state.
# These are FALLBACK-ONLY: clew's emitted top-level palette is the single
# source of truth (rendered into \definecolor by _resolve_palette below), and
# each claim's per-entry display_color overrides even that. This dict only
# fills a state clew did not emit. unsourced amber MIRRORS clew's current
# registered-source-gate emission (b26a00, unified 1.6) so there is no drift;
# when clew+figrecipe converge one canonical CUD-safe palette, render inherits
# it via the emitted palette with NO change here.
_DEFAULT_PALETTE = {
    "verified": "2E7D32",
    "suspect": "F9A825",
    "unsourced": "B26A00",
    "unverified": "C62828",
    "exception": "6A1B9A",
}


def sanitize_id(claim_id):
    """[a-zA-Z0-9]-only key -- the SAME transform clew_presentation.tex applies
    to \\clewval{id}, so the emitted macro name matches the call site."""
    return re.sub(r"[^a-zA-Z0-9]", "", str(claim_id))


def _hex(value):
    """Normalize a color to bare 6-hex uppercase, or None."""
    if not value:
        return None
    h = str(value).lstrip("#").strip().upper()
    return h if re.fullmatch(r"[0-9A-F]{6}", h) else None


def _first(d, *keys):
    """First present, non-empty value among ``keys`` in dict ``d``."""
    for k in keys:
        v = d.get(k)
        if v not in (None, ""):
            return v
    return None


def _claim_value(claim):
    """The display string for a claim. clew stores it display-ready; try the
    known field names in order (`claim_value` is the clew 0.2.19 key)."""
    v = _first(
        claim, "claim_value", "value", "display_value", "latex", "rendered_value", "text"
    )
    return "" if v is None else str(v)


def _verdict(claim):
    """Map a claim to one of the 4 presentation states (verified / suspect /
    unverified / exception).

    clew v1.3 emits a 4-state ``status`` directly (pass through). clew 0.2.19
    emits ``status: registered`` + a ``verified_at`` (or null) and NO
    verdict/color -- so a claim is ``verified`` only once chain-verified
    (``verified_at`` set), else ``unverified`` (red). A registered-but-unverified
    claim renders RED, honestly (never green until verified)."""
    status = str(claim.get("status", "")).strip().lower()
    status = _STATUS_SYNONYMS.get(status, status)  # 1.5 "failed" -> red bucket
    if status in _STATUS_COLOR:
        return status
    return "verified" if claim.get("verified_at") else "unverified"


def _resolve_palette(data):
    """status -> hex, from the top-level palette (dict or list of entries),
    falling back to the default palette for any missing state. Palette keys
    are normalized through the status synonyms (1.5 keys the red state
    "failed"), so the feed's hex lands on the right internal bucket."""
    palette = dict(_DEFAULT_PALETTE)
    raw = data.get("palette") or data.get("display_palette") or {}
    if isinstance(raw, dict):
        for status, color in raw.items():
            h = _hex(color if not isinstance(color, dict) else _first(color, "hex", "color"))
            key = _STATUS_SYNONYMS.get(str(status).lower(), str(status).lower())
            if h:
                palette[key] = h
    return palette


def _aggregate(data, claims):
    """(total, verified, allverified) from the attestation block, else counted
    from the claims themselves. Accepts both attestation shapes: the flat
    {verified_count, unverified_count} (<=1.4) and the 1.5 nested
    {counts: {total, verified, ...}, badge_state}."""
    att = data.get("attestation") or {}
    counts = att.get("counts") if isinstance(att.get("counts"), dict) else {}
    verified = counts.get("verified", att.get("verified_count"))
    total = counts.get("total")
    if not isinstance(total, int):
        unverified = att.get("unverified_count")
        if isinstance(verified, int) and isinstance(unverified, int):
            total = verified + unverified
    if not (isinstance(total, int) and isinstance(verified, int)):
        # No usable attestation -- count via the resolved verdict.
        total = len(claims)
        verified = sum(1 for c in claims if _verdict(c) == "verified")
    allverified = 1 if (total > 0 and verified == total) else 0
    return total, verified, allverified


def _iter_claims(data):
    """The claim records, whether claims.json stores them as a list or a dict
    keyed by claim_id."""
    claims = data.get("claims", data)
    if isinstance(claims, dict):
        out = []
        for cid, rec in claims.items():
            rec = dict(rec)
            rec.setdefault("claim_id", cid)
            out.append(rec)
        return out
    return list(claims) if isinstance(claims, list) else []


def render_clew_tex(data):
    r"""Render the clew_rendered.tex body from a parsed claims.json (v1.3)."""
    claims = _iter_claims(data)
    palette = _resolve_palette(data)
    total, verified, allverified = _aggregate(data, claims)

    lines = ["\\makeatletter", ""]
    lines.append("%% --- palette (from clew claims.json; writer has \\providecolor fallbacks) ---")
    for status, name in _STATUS_COLOR.items():
        lines.append(f"\\definecolor{{{name}}}{{HTML}}{{{palette[status]}}}")
    lines += ["", "%% --- aggregate ---"]
    lines.append(f"\\def\\clew@total{{{total}}}")
    lines.append(f"\\def\\clew@verified{{{verified}}}")
    lines.append(f"\\def\\clew@allverified{{{allverified}}}")
    lines += ["", "%% --- per-claim data (id sanitized to [a-zA-Z0-9]) ---"]

    for claim in claims:
        cid = sanitize_id(_first(claim, "claim_id", "id") or "")
        if not cid:
            continue
        # Resolve the 4-state verdict (v1.3 status pass-through, or 0.2.19
        # registered->verified/unverified), then the color: a per-claim color
        # field if clew emitted one (v1.3), else the palette entry for the
        # verdict (0.2.19 has no color, so derive it).
        verdict = _verdict(claim)
        # `display_color` is the frozen contract name (clew 0.4.0 emits it);
        # color/hex are accepted aliases. Fall back to the verdict palette.
        color = _hex(_first(claim, "display_color", "color", "hex")) or palette.get(verdict)
        value = _claim_value(claim)
        lines.append(f"%% {claim.get('claim_id', cid)} [{verdict}]")
        lines.append(f"\\@namedef{{clew@val@{cid}}}{{{value}}}")
        if color:
            lines.append(f"\\@namedef{{clew@hex@{cid}}}{{{color}}}")
        lines.append(f"\\@namedef{{clew@status@{cid}}}{{{verdict}}}")
        lines.append("")

    lines.append("\\makeatother")
    return "\n".join(lines) + "\n"


def main(argv):
    project_dir = argv[1] if len(argv) > 1 else "."
    project_path = Path(project_dir).resolve()
    claims_json = project_path / CLAIMS_JSON

    if not claims_json.exists():
        return 0  # clew layer optional -- no-op

    try:
        data = json.loads(claims_json.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(
            f"ERRO:     Cannot read clew claims.json ({claims_json}): {exc}. "
            f"Fix it or remove it; compiling now would ship a stale/empty "
            f"clew_rendered.tex.",
            file=sys.stderr,
        )
        return 1

    try:
        tex = render_clew_tex(data)
    except Exception as exc:  # malformed schema -- surface, don't ship stale
        print(
            f"ERRO:     Failed to render clew_rendered.tex from {claims_json}: "
            f"{exc}.",
            file=sys.stderr,
        )
        return 1

    out = project_path / OUTPUT_TEX
    try:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(tex, encoding="utf-8")
    except OSError as exc:
        print(f"ERRO:     Cannot write {out}: {exc}", file=sys.stderr)
        return 1

    n = len(_iter_claims(data))
    print(f"INFO:     Rendered clew_rendered.tex ({n} claims) from clew claims.json")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# EOF
