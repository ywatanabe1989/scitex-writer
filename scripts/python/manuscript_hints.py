#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/manuscript_hints.py
# Purpose: Emit a structured MANUSCRIPT-HINTS feed (JSON) that the writer UI's
#          Details pane renders as non-intrusive, Overleaf/OpenAI-style inline
#          HINTS about the manuscript — the DATA layer of the dynamic-paper
#          experience ("a research agent that reacts to your work").
#
#          The compile pipeline already COMPUTES some of these signals (undefined
#          \ref cross-references in the LaTeX log). This turns them into ONE
#          machine-readable feed a UI (or an agent) can SUBSCRIBE to and surface
#          inline + quietly, instead of only fail-loud stderr / build gates.
#
#          NEUTRAL, MULTI-PRODUCER: writer owns the SCHEMA + the UI; each PRODUCER
#          (this writer/latex-structure producer, scitex-clew for provenance +
#          citations, a third party) writes hints into the feed under its own
#          `source`. Writer does not import clew. (Retiring the interim \cite +
#          claim readers here once clew ships its export_manuscript_hints
#          producer — see the card; \ref stays writer's, it is latex structure,
#          not provenance.)
#
#          IMMUTABLE ORIGINAL: never edits the manuscript or the PDF; reads
#          compile artifacts, writes a sidecar. ADVISORY: always exits 0 — a
#          hints feed must never break a compile.
#
#          Feed schema (manuscript-hints/1) -- one flat list, additive:
#            {
#              "schema": "manuscript-hints/1",
#              "summary": {"total": N, "by_severity": {...}, "by_kind": {...}},
#              "hints": [
#                {
#                  "id": "<stable per-hint id>",
#                  "kind": "citation|reference|figure|claim|stat|...",
#                  "severity": "info|advice|warning|error",
#                  "message": "<human-readable>",
#                  "location": {"file": str|null, "line": int|null, "page": int|null},
#                  "claim_id": str|null,   # join key into the clew provenance graph
#                  "source": "latex-log|scitex-clew|...",
#                }, ...
#              ]
#            }
#
# Usage:
#   python manuscript_hints.py [project_dir]

import json
import re
import sys
from pathlib import Path

SCHEMA = "manuscript-hints/1"
OUTPUT_JSON = ".scitex/writer/hints.json"
CLAIMS_JSON = ".scitex/clew/runtime/claims.json"

# The `source` labels THIS writer producer authoritatively owns in the shared
# feed. Merge-by-source (write_feed) replaces only these on each writer run and
# preserves every other producer's entries (clew, figrecipe, ...) untouched, so
# the feed is multi-producer without any producer importing another. "latex-log"
# = writer's own \ref/\cite log producer; "scitex-clew" is INTERIM (writer reads
# the clew ledger until scitex-clew ships export_manuscript_hints, at which point
# this tuple drops to ("latex-log",) and clew owns "scitex-clew").
WRITER_SOURCES = ("latex-log", "scitex-clew")
# The LaTeX engine log the compile writes; hints read it for unresolved refs.
_LOG_CANDIDATES = (
    "logs/manuscript.log",
    "01_manuscript/logs/manuscript.log",
    "manuscript.log",
)

# Severity order (low -> high) for summary sorting / UI grouping.
_SEVERITY_ORDER = ("info", "advice", "warning", "error")

# LaTeX log patterns for unresolved cross-references / citations.
_UNDEF_REF_RE = re.compile(r"Reference [`']([^'\n]+)' [^\n]*?undefined")
_UNDEF_CITE_RE = re.compile(r"Citation [`']([^'\n]+)' [^\n]*?undefined")

# clew claim status -> severity. verified is intentionally SILENT (a verified
# claim needs no hint -- "silent collect, notify what matters"). unsourced folds
# onto suspect (operator decision; see render_clew).
_CLAIM_STATUS_SEVERITY = {
    "verified": None,
    "suspect": "advice",
    "unsourced": "advice",
    "partial": "advice",
    "unverified": "warning",
    "failed": "warning",
    "exception": "warning",
}


def _hint(kind, severity, message, source, location=None, claim_id=None, hid=None):
    """Build one hint dict. ``hid`` is a stable id used for dedup + UI keying;
    when omitted it is derived from (kind, claim_id/message)."""
    key = hid or f"{kind}:{claim_id or message}"
    return {
        "id": key,
        "kind": kind,
        "severity": severity,
        "message": message,
        "location": location or {"file": None, "line": None, "page": None},
        "claim_id": claim_id,
        "source": source,
    }


def hints_from_log(log_text):
    """Unresolved cross-references / citations from a LaTeX engine log.

    Deduplicated by key: LaTeX repeats the warning on every pass, and a key can
    recur across pages -- the UI wants ONE hint per unresolved token. (The
    \\cite branch is INTERIM -- scitex-clew's verify-citations will own citation
    hints via its producer; \\ref stays here as latex structure.)"""
    out = []
    seen = set()
    for key in _UNDEF_REF_RE.findall(log_text or ""):
        if ("reference", key) in seen:
            continue
        seen.add(("reference", key))
        out.append(_hint(
            "reference", "warning",
            f"Reference '{key}' is undefined -- add a \\label or fix the \\ref.",
            "latex-log", claim_id=None, hid=f"reference:{key}"))
    for key in _UNDEF_CITE_RE.findall(log_text or ""):
        if ("citation", key) in seen:
            continue
        seen.add(("citation", key))
        out.append(_hint(
            "citation", "warning",
            f"Citation '{key}' is undefined -- add it to the bibliography.",
            "latex-log", claim_id=key, hid=f"citation:{key}"))
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


def hints_from_claims(data):
    """One hint per NON-verified clew claim. INTERIM: scitex-clew will own claim
    hints via its export_manuscript_hints producer; until then writer reads the
    ledger so the UI has content. A claim not verified to a source is exactly the
    "this value doesn't reach its data" signal -- carried with its claim_id so
    the UI can light up the provenance chain."""
    out = []
    for claim in _iter_claims(data):
        status = str(claim.get("status", "") or "").strip().lower()
        if status == "registered" and not claim.get("verified_at"):
            status = "unverified"
        severity = _CLAIM_STATUS_SEVERITY.get(status, "advice" if status else None)
        if severity is None:
            continue  # verified / unknown-empty -> stay quiet
        cid = str(claim.get("claim_id", claim.get("id", "")) or "")
        value = _claim_value(claim)
        shown = (value[:60] + "...") if len(value) > 63 else value
        detail = f" ('{shown}')" if shown else ""
        out.append(_hint(
            _claim_kind(claim), severity,
            f"Claim{detail} is not verified to a source ({status}).",
            "scitex-clew",
            location={
                "file": claim.get("file_path"),
                "line": claim.get("line_number"),
                "page": None,
            },
            claim_id=cid or None,
            hid=f"claim:{cid or shown}"))
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


def collect_hints(project_dir="."):
    """Gather hints from every available producer. Missing artifacts are simply
    skipped -- an absent clew ledger or log yields fewer hints, never an error
    (this is an advisory feed)."""
    project_path = Path(project_dir).resolve()
    hints = []
    hints.extend(hints_from_log(_read_log(project_path)))
    claims = _read_claims(project_path)
    if claims is not None:
        hints.extend(hints_from_claims(claims))
    return hints


def summarize(hints):
    by_sev = {}
    by_kind = {}
    for h in hints:
        by_sev[h["severity"]] = by_sev.get(h["severity"], 0) + 1
        by_kind[h["kind"]] = by_kind.get(h["kind"], 0) + 1
    return {"total": len(hints), "by_severity": by_sev, "by_kind": by_kind}


def build_feed(hints):
    """The full feed object, hints sorted most-severe first for the UI."""
    order = {s: i for i, s in enumerate(reversed(_SEVERITY_ORDER))}
    ordered = sorted(hints, key=lambda h: order.get(h["severity"], 99))
    return {"schema": SCHEMA, "summary": summarize(ordered), "hints": ordered}


def _read_existing_hints(project_path):
    """Existing feed's hints list, or [] when the sidecar is absent/malformed.

    An unreadable or non-conforming file is treated as empty rather than an
    error -- this is an advisory feed, and a merge must never crash a compile."""
    p = project_path / OUTPUT_JSON
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    hints = data.get("hints") if isinstance(data, dict) else None
    return [h for h in hints if isinstance(h, dict)] if isinstance(hints, list) else []


def merge_by_source(existing_hints, new_hints, owned_sources):
    """Multi-producer merge: replace ONLY the producer's own sources.

    Each producer (writer, clew, figrecipe, ...) writes into the shared feed but
    owns only its own ``source`` labels. Existing hints whose source is in
    ``owned_sources`` are dropped (the producer re-emits its current set --
    possibly empty, which is how STALE entries clear); every other source's hints
    are preserved verbatim. The producer never needs to know about, or import,
    the others. Returns the merged hint list (preserved-others + new)."""
    owned = {owned_sources} if isinstance(owned_sources, str) else set(owned_sources)
    preserved = [h for h in existing_hints if h.get("source") not in owned]
    return preserved + list(new_hints)


def write_feed(project_dir, feed, owned_sources=None):
    """Atomic write of the feed to <project>/.scitex/writer/hints.json.

    When ``owned_sources`` is given, merge-by-source: read the existing sidecar,
    preserve every other producer's hints, replace only this producer's own
    sources with ``feed``'s hints, and rebuild the summary/ordering over the
    union. When ``owned_sources`` is None the feed is written as-is (single
    producer / full-overwrite -- backward compatible)."""
    project_path = Path(project_dir).resolve()
    out = project_path / OUTPUT_JSON
    if owned_sources is not None:
        merged = merge_by_source(
            _read_existing_hints(project_path),
            feed.get("hints", []),
            owned_sources,
        )
        feed = build_feed(merged)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(feed, indent=2, ensure_ascii=False), encoding="utf-8")
    tmp.replace(out)
    return out


def main(argv):
    project_dir = argv[1] if len(argv) > 1 else "."
    feed = build_feed(collect_hints(project_dir))
    # Merge-by-source: writer owns WRITER_SOURCES, preserves other producers'.
    out = write_feed(project_dir, feed, owned_sources=WRITER_SOURCES)
    print(f"INFO:     Wrote manuscript hints feed ({feed['summary']['total']}) -> {out}")
    return 0  # advisory feed: never gate the compile


if __name__ == "__main__":
    sys.exit(main(sys.argv))

# EOF
