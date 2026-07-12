#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/python/_citation_trust_cache.py
# Purpose: Verdict cache for check_citation_trust.py.
#
#          CACHING IS MANDATORY here: scitex-scholar has NO persistent cache in
#          the verify_cites path (it builds fresh resolver engines per call), and
#          a manuscript carries 100+ cites recompiled many times a day -- so
#          every compile would otherwise re-hit CrossRef/OpenAlex/arXiv.
#
#          Verdicts live in the project runtime dir
#          (.scitex/writer/runtime/citation_trust.json -- the same
#          `.scitex/writer/runtime/` convention as the annotations DB and the GUI
#          runtime state), keyed by cite key + a CONTENT fingerprint of the bib
#          entry, so editing any field of an entry re-verifies it.
#
#          Invariants (fail-loud):
#            * a cache MISS is never reported as verified -- it forces a real
#              verification run;
#            * only KNOWN statuses are stored, so an unrecognised status can
#              never be resurrected from the cache;
#            * entries older than CACHE_TTL_DAYS are re-verified;
#            * a corrupt/foreign cache file reads as empty (= all misses).
#          The caller additionally never stores OFFLINE verdicts (an offline
#          "unverified" must not poison a later online run).
#
# Self-contained: stdlib only.

import hashlib
import json
import time
from pathlib import Path

# Runtime dir convention: <project>/.scitex/writer/runtime/<file>.
CACHE_REL = ".scitex/writer/runtime/citation_trust.json"
CACHE_SCHEMA = "scitex-writer/citation_trust/v1"
CACHE_TTL_DAYS = 30


def cache_path(project_dir):
    """Path of the verdict cache inside the project runtime dir."""
    return Path(project_dir) / CACHE_REL


def entry_fingerprint(fields):
    """Content fingerprint of one bib entry (sha256 over its normalized fields)."""
    payload = "\n".join(f"{name}={fields[name]}" for name in sorted(fields))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_cache(path):
    """Load the verdict cache, or ``{}`` on any problem (a bad cache = all misses)."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    if not isinstance(data, dict) or data.get("schema") != CACHE_SCHEMA:
        return {}
    verdicts = data.get("verdicts")
    return verdicts if isinstance(verdicts, dict) else {}


def save_cache(path, verdicts):
    """Write the verdict cache. Best-effort: a read-only tree must not crash."""
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {"schema": CACHE_SCHEMA, "verdicts": verdicts},
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
    except OSError:
        return False
    return True


def cache_lookup(cached, key, fingerprint, known_statuses, now=None):
    """Return the cached verdict dict for ``key``, or None on a MISS.

    A miss (unknown key, changed entry content, unknown status, expired verdict,
    malformed record) yields None -- and a miss is NEVER a pass; the caller
    re-verifies.
    """
    record = cached.get(key)
    if not isinstance(record, dict):
        return None
    if fingerprint is None or record.get("fingerprint") != fingerprint:
        return None
    status = record.get("status")
    if status not in known_statuses:
        return None
    stamp = record.get("verified_at")
    if not isinstance(stamp, (int, float)):
        return None
    now = time.time() if now is None else now
    if now - stamp > CACHE_TTL_DAYS * 86400:
        return None
    return {
        "key": key,
        "status": status,
        "detail": record.get("detail", ""),
        "confidence": record.get("confidence"),
        "cached": True,
    }


def cache_store(cached, verdicts, fingerprints, known_statuses, now=None):
    """Merge fresh verdicts into ``cached`` (returns it). Unknown status = skipped."""
    now = time.time() if now is None else now
    for verdict in verdicts:
        key = verdict.get("key")
        status = verdict.get("status")
        fingerprint = fingerprints.get(key)
        if not key or status not in known_statuses or fingerprint is None:
            continue
        cached[key] = {
            "fingerprint": fingerprint,
            "status": status,
            "detail": verdict.get("detail", ""),
            "confidence": verdict.get("confidence"),
            "verified_at": now,
        }
    return cached


__all__ = [
    "CACHE_REL",
    "CACHE_SCHEMA",
    "CACHE_TTL_DAYS",
    "cache_lookup",
    "cache_path",
    "cache_store",
    "entry_fingerprint",
    "load_cache",
    "save_cache",
]

# EOF
