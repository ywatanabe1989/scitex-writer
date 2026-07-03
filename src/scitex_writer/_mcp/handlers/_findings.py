#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Read the manuscript-findings feed sidecar (.scitex/writer/findings.json).

The feed is PRODUCED at compile time by ``scripts/python/manuscript_findings.py``
(the "Manuscript Findings" compile stage) — the data layer of the dynamic-paper
UI. This reader just SERVES it to the editor's Details pane. Framework-agnostic
(the Django / MCP / Flask surfaces are all thin wrappers around this).
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

FINDINGS_JSON = ".scitex/writer/findings.json"

_EMPTY_FEED = {
    "schema": "manuscript-findings/1",
    "summary": {"total": 0, "by_severity": {}, "by_kind": {}},
    "findings": [],
}


def get_findings(project_dir: str) -> dict:
    """The manuscript-findings feed for ``project_dir``.

    Returns an EMPTY feed (never raises) when the sidecar is absent, unreadable,
    or malformed — the UI treats "no feed yet" (paper not compiled since the
    feature landed) the same as "no findings". A copy is returned so callers
    cannot mutate the module-level default.
    """
    path = Path(project_dir) / FINDINGS_JSON
    if not path.exists():
        return copy.deepcopy(_EMPTY_FEED)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return copy.deepcopy(_EMPTY_FEED)
    if not isinstance(data, dict) or not isinstance(data.get("findings"), list):
        return copy.deepcopy(_EMPTY_FEED)
    return data


__all__ = ["get_findings", "FINDINGS_JSON"]
