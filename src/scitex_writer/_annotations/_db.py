#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SQLite persistence for annotations (§2.3).

One ``annotations`` table; JSON columns for ``region`` / ``payload`` /
``source_ref``. No ORM, no Django models — writer's Django app is
model-less by design. The default DB path is resolved through the fleet
local-state convention (``scitex_config`` runtime path), NOT hard-coded;
tests pass an explicit ``db_path`` so the real store is never touched.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ._record import Annotation

# JSON-encoded columns (§2.3 schema).
_JSON_COLUMNS = ("region", "payload", "source_ref")
_COLUMNS = (
    "annotation_id",
    "doc_type",
    "build_id",
    "page",
    "region",
    "kind",
    "payload",
    "source_ref",
    "author",
    "created_at",
    "status",
)

PathLike = Union[str, Path]


def default_db_path() -> Path:
    """Resolve the runtime DB path via the fleet local-state convention.

    ``scitex_config._ecosystem.local_state.runtime_path("writer", "writer.db")``
    → ``<scope>/.scitex/writer/runtime/writer.db``. Resolved lazily (not at
    import) so tests never trigger the seed-dir creation.

    NOTE (spike 0): ``runtime_path`` resolves scope from the *current
    working directory's* git root, not the manuscript project dir. That is
    the documented convention (writer already writes ``builds/builds.json``
    there). A per-manuscript DB is a later concern (§6); for the spike the
    handler may pass an explicit path if it wants project-scoped storage.
    """
    from scitex_config._ecosystem import local_state

    return Path(local_state.runtime_path("writer", "writer.db"))


def _connect(db_path: Optional[PathLike]) -> sqlite3.Connection:
    path = Path(db_path) if db_path is not None else default_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    _ensure_schema(conn)
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS annotations (
            annotation_id TEXT PRIMARY KEY,
            doc_type      TEXT NOT NULL,
            build_id      TEXT,
            page          INTEGER NOT NULL,
            region        TEXT,
            kind          TEXT NOT NULL,
            payload       TEXT,
            source_ref    TEXT,
            author        TEXT,
            created_at    TEXT NOT NULL,
            status        TEXT NOT NULL DEFAULT 'open'
        )
        """
    )
    conn.execute(
        "CREATE INDEX IF NOT EXISTS ix_annotations_doc_status "
        "ON annotations (doc_type, status)"
    )
    conn.commit()


def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for col in _COLUMNS:
        val = row[col]
        if col in _JSON_COLUMNS and val is not None:
            val = json.loads(val)
        out[col] = val
    return out


def persist(
    annotation: Annotation, *, db_path: Optional[PathLike] = None
) -> Dict[str, Any]:
    """Insert one annotation row; return the stored record as a dict.

    Atomic single-row insert (no whole-file rewrite) — safe under the
    Django server's concurrent POSTs.
    """
    record = annotation.to_dict()
    values = []
    for col in _COLUMNS:
        val = record.get(col)
        if col in _JSON_COLUMNS and val is not None:
            val = json.dumps(val)
        values.append(val)
    placeholders = ", ".join("?" for _ in _COLUMNS)
    conn = _connect(db_path)
    try:
        conn.execute(
            f"INSERT INTO annotations ({', '.join(_COLUMNS)}) VALUES ({placeholders})",
            values,
        )
        conn.commit()
    finally:
        conn.close()
    return record


def list_annotations(
    *,
    db_path: Optional[PathLike] = None,
    doc_type: Optional[str] = None,
    status: Optional[str] = None,
    build_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return annotations matching the given predicate, newest first."""
    clauses = []
    params: List[Any] = []
    if doc_type:
        clauses.append("doc_type = ?")
        params.append(doc_type)
    if status:
        clauses.append("status = ?")
        params.append(status)
    if build_id:
        clauses.append("build_id = ?")
        params.append(build_id)
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    conn = _connect(db_path)
    try:
        rows = conn.execute(
            f"SELECT * FROM annotations{where} ORDER BY created_at DESC", params
        ).fetchall()
    finally:
        conn.close()
    return [_row_to_dict(r) for r in rows]
