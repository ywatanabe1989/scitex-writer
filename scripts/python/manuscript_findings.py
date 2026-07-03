#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/manuscript_findings.py
# Purpose: Emit a structured MANUSCRIPT-FINDINGS feed (JSON) that the writer UI's
#          Details pane renders as non-intrusive "the paper reacts to your work"
#          notifications -- the DATA layer of the dynamic-paper experience.
#
#          The compile pipeline already COMPUTES these signals (undefined
#          references/citations in the LaTeX log; unverified claims in clew's
#          claims.json). Today they only fail loud on stderr / gate the build.
#          This turns the SAME signals into one machine-readable feed that a UI
#          (or an agent) can SUBSCRIBE to and surface inline, quietly.
#
#          IMMUTABLE ORIGINAL: this NEVER edits the manuscript or the PDF. It
#          only READS compile artifacts and WRITES the sidecar feed. The paper
#          stays the immutable source; findings are a layer on top.
#
#          Feed schema (manuscript-findings/1) -- one flat list, additive
#          (consumers ignore unknown fields):
#            {
#              "schema": "manuscript-findings/1",
#              "summary": {"total": N, "by_severity": {...}, "by_kind": {...}},
#              "findings": [
#                {
#                  "id":       "<stable per-finding id>",
#                  "kind":     "citation|reference|figure|claim|stat|...",
#                  "severity": "info|advice|warning|error",
#                  "message":  "<human-readable>",
#                  "location": {"file": str|null, "line": int|null, "page": int|null},
#                  "claim_id": str|null,   # join key into the clew provenance graph
#                  "source":   "log|clew|...",
#                }, ...
#              ]
#            }
#
#          NOT A GATE: always exits 0. The build's fail-loud gates are separate;
#          this feed is advisory and must never break a compile.
#
# Usage:
#   python manuscript_findings.py [project_dir]

import json
import re
import sys
from pathlib import Path

SCHEMA = "manuscript-findings/1"
OUTPUT_JSON = ".scitex/writer/findings.json"
CLAIMS_JSON = ".scitex/clew/runtime/claims.json"
# The LaTeX engine log the compile writes; findings read it for unresolved refs.
_LOG_CANDIDATES = (
    "logs/manuscript.log",
    "01_manuscript/logs/manuscript.log",
    "manuscript.log",
)

# Severity order (low -> high) for summary sorting / UI grouping.
_SEVERITY_ORDER = ("info", "advice", "warning", "error")

# LaTeX log patterns for unresolved cross-references / citations. LaTeX emits
# e.g. `Reference `fig:1' on page 2 undefined` and `Citation `Smith2020' ...
# undefined`. Match the KEY so the UI can anchor the finding to the token.
_UNDEF_REF_RE = re.compile(r"Reference [`']([^'\n]+)' [^\n]*?undefined")
_UNDEF_CITE_RE = re.compile(r"Citation [`']([^'\n]+)' [^\n]*?undefined")

# clew claim status -> (severity, note). verified is intentionally SILENT (a
# verified claim needs no notification -- "silent collect, notify what matters").
# unsourced folds onto suspect (operator decision; see render_clew).
_CLAIM_STATUS_SEVERITY = {
    "verified": None,
    "suspect": "advice",
    "unsourced": "advice",
    "partial": "advice",
    "unverified": "warning",
    "failed": "warning",
    "exception": "warning",
}


def _finding(kind, severity, message, source, location=None, claim_id=None, fid=None):
    """Build one finding dict. ``fid`` is a stable id used for dedup + UI keying;
    when omitted it is derived from (kind, claim_id/message)."""
    key = fid or f"{kind}:{claim_id or message}"
    return {
        "id": key,
        "kind": kind,
        "severity": severity,
        "message": message,
        "location": location or {"file": None, "line": None, "page": None},
        "claim_id": claim_id,
        "source": source,
    }


def findings_from_log(log_text):
    """Unresolved cross-references / citations from a LaTeX engine log.

    Deduplicated by key: LaTeX repeats the warning on every pass, and a key can
    recur across pages -- the UI wants ONE finding per unresolved token."""
    out = []
    seen = set()
    for key in _UNDEF_REF_RE.findall(log_text or ""):
        if ("reference", key) in seen:
            continue
        seen.add(("reference", key))
        out.append(_finding(
            "reference", "warning",
            f"Reference '{key}' is undefined -- add a \\label or fix the \\ref.",
            "log", claim_id=None, fid=f"reference:{key}"))
    for key in _UNDEF_CITE_RE.findall(log_text or ""):
        if ("citation", key) in seen:
            continue
        seen.add(("citation", key))
        out.append(_finding(
            "citation", "warning",
            f"Citation '{key}' is undefined -- add it to the bibliography.",
            "log", claim_id=key, fid=f"citation:{key}"))
    return out


def _claim_kind(claim):
    """UI kind from clew's claim_type (value -> stat; else pass through)."""
    ctype = str(claim.get("claim_type", "") or "").strip().lower()
    if ctype == "value":
        return "stat"
    return ctype or "claim"


def _claim_value(claim):
    for k in ("claim_value", "value", "display_value", "text"):
        v = claim.get(k)
        if v not in (None, ""):
            return str(v)
    return ""


def _iter_claims(data):
    """clew claims.json stores claims as a list OR a dict keyed by claim_id."""
    claims = data.get("claims", data) if isinstance(data, dict) else data
    if isinstance(claims, dict):
        out = []
        for cid, rec in claims.items():
            if isinstance(rec, dict):
                rec = dict(rec)
                rec.setdefault("claim_id", cid)
                out.append(rec)
        return out
    return [c for c in claims if isinstance(c, dict)] if isinstance(claims, list) else []


def findings_from_claims(data):
    """One finding per NON-verified clew claim. A claim that is not verified to a
    source is exactly the "this value doesn't reach its data" signal the dynamic
    paper wants to surface -- carried with its claim_id so the UI can light up
    the provenance chain."""
    out = []
    for claim in _iter_claims(data):
        status = str(claim.get("status", "") or "").strip().lower()
        # A registered-but-unverified claim (verified_at is null) reads as
        # unverified, matching render_clew's honest verdict.
        if status == "registered" and not claim.get("verified_at"):
            status = "unverified"
        severity = _CLAIM_STATUS_SEVERITY.get(status, "advice" if status else None)
        if severity is None:
            continue  # verified / unknown-empty -> stay quiet
        cid = str(claim.get("claim_id", claim.get("id", "")) or "")
        value = _claim_value(claim)
        shown = (value[:60] + "...") if len(value) > 63 else value
        detail = f" ('{shown}')" if shown else ""
        out.append(_finding(
            _claim_kind(claim), severity,
            f"Claim{detail} is not verified to a source ({status}).",
            "clew",
            location={
                "file": claim.get("file_path"),
                "line": claim.get("line_number"),
                "page": None,
            },
            claim_id=cid or None,
            fid=f"claim:{cid or shown}"))
    return out


def _read_log(project_path):
    for rel in _LOG_CANDIDATES:
        p = project_path / rel
        if p.exists():
            try:
                return p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                return ""
    return ""


def _read_claims(project_path):
    p = project_path / CLAIMS_JSON
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def collect_findings(project_dir="."):
    """Gather findings from every available producer. Missing artifacts are
    simply skipped -- an absent clew ledger or log yields fewer findings, never
    an error (this is an advisory feed)."""
    project_path = Path(project_dir).resolve()
    findings = []
    findings.extend(findings_from_log(_read_log(project_path)))
    claims = _read_claims(project_path)
    if claims is not None:
        findings.extend(findings_from_claims(claims))
    return findings


def summarize(findings):
    by_sev = {}
    by_kind = {}
    for f in findings:
        by_sev[f["severity"]] = by_sev.get(f["severity"], 0) + 1
        by_kind[f["kind"]] = by_kind.get(f["kind"], 0) + 1
    return {"total": len(findings), "by_severity": by_sev, "by_kind": by_kind}


def build_feed(findings):
    """The full feed object, findings sorted most-severe first for the UI."""
    order = {s: i for i, s in enumerate(reversed(_SEVERITY_ORDER))}
    ordered = sorted(findings, key=lambda f: order.get(f["severity"], 99))
    return {"schema": SCHEMA, "summary": summarize(ordered), "findings": ordered}


def write_feed(project_dir, feed):
    """Atomic write of the feed to <project>/.scitex/writer/findings.json."""
    out = Path(project_dir).resolve() / OUTPUT_JSON
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(feed, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out)
    return out


def main(argv):
    project_dir = argv[1] if len(argv) > 1 else "."
    feed = build_feed(collect_findings(project_dir))
    out = write_feed(project_dir, feed)
    print(f"INFO:     Wrote manuscript findings feed ({feed['summary']['total']}) -> {out}")
    return 0  # advisory feed: never gate the compile


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# EOF
