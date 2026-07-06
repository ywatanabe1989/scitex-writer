#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_writer._annotations._db (SQLite persist / list).

Real SQLite in ``tmp_path`` (no mocks, STX-NM002); one assert per test
(STX-TQ007); no monkeypatch (PA-306).
"""

from __future__ import annotations

from scitex_writer._annotations._db import list_annotations, persist
from scitex_writer._annotations._record import Annotation


def _annotation(text: str = "fix this claim") -> Annotation:
    return Annotation.from_post(
        {"page": 3, "doc_type": "manuscript", "payload": {"text": text}}
    )


def test_persist_then_list_returns_one_row(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    persist(_annotation(), db_path=db)
    # Act
    rows = list_annotations(db_path=db)
    # Assert
    assert len(rows) == 1


def test_persist_round_trips_text_payload(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    persist(_annotation("check figure 2"), db_path=db)
    # Act
    rows = list_annotations(db_path=db)
    # Assert
    assert rows[0]["payload"] == {"text": "check figure 2"}


def test_persist_round_trips_source_ref(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    ann = _annotation()
    ann.source_ref = {"page": 3}
    persist(ann, db_path=db)
    # Act
    rows = list_annotations(db_path=db)
    # Assert
    assert rows[0]["source_ref"] == {"page": 3}


def test_list_annotations_filters_by_status(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    persist(_annotation(), db_path=db)
    # Act
    rows = list_annotations(db_path=db, status="resolved")
    # Assert
    assert rows == []


def test_list_annotations_filters_by_doc_type(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    persist(_annotation(), db_path=db)
    # Act
    rows = list_annotations(db_path=db, doc_type="manuscript")
    # Assert
    assert len(rows) == 1
