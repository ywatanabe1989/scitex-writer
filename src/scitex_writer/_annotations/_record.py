#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The annotation record — one posted PDF annotation is one record.

Framework-agnostic (no Django). Wire shape == stored shape == this
dataclass's ``to_dict()``. See
``docs/04_DESIGN_PDF_ANNOTATION_FEEDBACK_LOOP.md`` §2.1.

Spike 0 scope: ``kind`` is limited to ``text_comment`` and ``source_ref``
is page-only (no SyncTeX / claim-hotspot resolution yet — §6 spike 1).
"""

from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

# Spike 0 supports only text comments; broadened in later spikes (§6).
TEXT_COMMENT = "text_comment"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class Annotation:
    """One posted annotation over the compiled manuscript PDF (§2.1)."""

    page: int
    doc_type: str = "manuscript"
    kind: str = TEXT_COMMENT
    payload: Dict[str, Any] = field(default_factory=dict)
    region: Optional[Dict[str, float]] = None
    build_id: Optional[str] = None
    source_ref: Optional[Dict[str, Any]] = None
    author: str = "operator"
    status: str = "open"
    annotation_id: str = field(default_factory=_new_id)
    created_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_post(cls, body: Dict[str, Any]) -> "Annotation":
        """Build a record from a POST body (§2.1 minus server fields).

        Server-owned fields (``annotation_id``, ``created_at``) are always
        assigned here, never trusted from the client. ``source_ref`` is
        resolved by the caller when omitted (spike 0: page-only).
        """
        if "page" not in body:
            raise ValueError("page is required")
        page = int(body["page"])
        kind = body.get("kind", TEXT_COMMENT)
        if kind != TEXT_COMMENT:
            raise ValueError(
                f"spike 0 supports kind={TEXT_COMMENT!r} only, got {kind!r}"
            )
        payload = body.get("payload") or {}
        if not (payload.get("text") or "").strip():
            raise ValueError("text_comment payload requires a non-empty 'text'")
        return cls(
            page=page,
            doc_type=body.get("doc_type", "manuscript"),
            kind=kind,
            payload=payload,
            region=body.get("region"),
            build_id=body.get("build_id"),
            source_ref=body.get("source_ref"),
            author=body.get("author", "operator"),
        )
