#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Annotation orchestration — the POST flow (§3) and source resolution (§2.2).

Framework-agnostic. The Django handler
(``_django/handlers/annotation.py``) is a thin wrapper over
``add_annotation`` here, so the same logic is reusable from CLI/MCP later.

Spike 0 (§6.1): ``source_ref`` is page-only; SyncTeX / claim-hotspot /
float resolution land in spike 1 (§6.2).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from ._emit import emit
from ._record import Annotation

PathLike = Union[str, Path]


def resolve_source_ref(annotation: Annotation) -> Dict[str, Any]:
    """Best-effort coords→source mapping (§2.2).

    Spike 0: page-only (level 4). SyncTeX / claim-hotspot / float
    resolution land in spike 1 (§6.2). Never fatal — always resolves at
    least to ``{page}``.
    """
    return {"page": annotation.page}


def add_annotation(
    body: Dict[str, Any],
    *,
    project: str,
    card_id: Optional[str] = None,
    db_path: Optional[PathLike] = None,
    store: Optional[PathLike] = None,
) -> Dict[str, Any]:
    """POST orchestration (§3): validate → resolve source_ref → persist → emit.

    ``project`` names the manuscript (used to derive the owning card id).
    ``db_path`` / ``store`` are injectable so tests stay hermetic. Returns
    ``{ok, annotation_id, source_ref, notified}``.
    """
    annotation = Annotation.from_post(body)
    if annotation.source_ref is None:
        annotation.source_ref = resolve_source_ref(annotation)
    result = emit(
        annotation,
        project=project,
        card_id=card_id,
        db_path=db_path,
        store=store,
    )
    return {
        "ok": True,
        "annotation_id": result["annotation_id"],
        "source_ref": result["source_ref"],
        "notified": result["notified"],
        "notify_error": result["notify_error"],
    }
