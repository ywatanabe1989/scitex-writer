#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The emit seam (§4) — annotation → channel notification.

PROVISIONAL RAIL. The design doc (§4) recommends scitex-todo card events
as the durable notification rail, but the exact contract (card model,
body schema, resolve/close semantics) is pending **scitex-agentic-journal
ratification** (§5.4). This module keeps the whole mechanism behind a
single ``emit()`` function so the rail is a swappable impl detail, not an
API change. Do NOT hard-couple callers to scitex-todo.

Spike 0 behaviour: ``emit()`` PERSISTS the record (SQLite, ``_db``) and
POSTS a one-line ``comment_task`` to the manuscript's owning card. Both
steps are fail-soft on the notify side — a failed post never fails the
persist (§3, POST sequence step 4).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Union

from ._db import persist as _persist
from ._record import Annotation

PathLike = Union[str, Path]

# Provisional default card-id template (§4). One card per manuscript
# project; swappable once agentic-journal ratifies the card model.
_CARD_ID_TEMPLATE = "writer-annotations-{project}"
_EMIT_AUTHOR = "scitex-writer"


def default_card_id(project: str) -> str:
    """The provisional owning-card id for a manuscript project (§4)."""
    return _CARD_ID_TEMPLATE.format(project=project)


def render_summary(record: Dict[str, Any]) -> str:
    """One-line human-readable render of an annotation (§4)."""
    text = ((record.get("payload") or {}).get("text") or "").strip()
    if len(text) > 120:
        text = text[:117] + "..."
    return (
        f"[annotation] p{record.get('page')} {record.get('kind')} "
        f'@ {record.get("source_ref")} — "{text}" '
        f"(id={record.get('annotation_id')})"
    )


def _notify(
    record: Dict[str, Any],
    *,
    card_id: str,
    store: Optional[PathLike] = None,
) -> bool:
    """PROVISIONAL: post the annotation summary to a scitex-todo card.

    Returns True on success, False on any failure (fail-soft). ``store``
    lets tests point at a tmp ``tasks.yaml`` so the real shared store is
    never written.
    """
    try:
        from scitex_todo import comment_task

        comment_task(
            store,
            task_id=card_id,
            text=render_summary(record),
            by=_EMIT_AUTHOR,
        )
        return True
    except Exception:
        # Fail-soft: a broken/absent card must not fail the persist.
        return False


def emit(
    annotation: Annotation,
    *,
    project: str,
    card_id: Optional[str] = None,
    db_path: Optional[PathLike] = None,
    store: Optional[PathLike] = None,
) -> Dict[str, Any]:
    """Persist the annotation, then emit the provisional notification.

    Returns ``{annotation_id, source_ref, persisted, notified}``. The
    ``notified`` flag is fail-soft (§3 step 4): a failed notify still
    returns a persisted record.
    """
    record = _persist(annotation, db_path=db_path)
    target_card = card_id or default_card_id(project)
    notified = _notify(record, card_id=target_card, store=store)
    return {
        "annotation_id": record["annotation_id"],
        "source_ref": record["source_ref"],
        "persisted": True,
        "notified": notified,
    }
