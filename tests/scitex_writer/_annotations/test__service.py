#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_writer._annotations._service (POST orchestration).

Real SQLite in ``tmp_path``; the scitex-todo rail is optional so the
notified-True path ``pytest.importorskip("scitex_todo")``. No mocks
(STX-NM002); one assert per test (STX-TQ007); no monkeypatch (PA-306).
"""

from __future__ import annotations

import pytest

from scitex_writer._annotations._record import Annotation
from scitex_writer._annotations._service import add_annotation, resolve_source_ref


def _body(text: str = "please clarify") -> dict:
    return {"page": 2, "doc_type": "manuscript", "payload": {"text": text}}


@pytest.fixture
def todo_store(tmp_path):
    """A real tmp scitex-todo store seeded with the owning card."""
    pytest.importorskip("scitex_todo")
    from scitex_todo import add_task

    store = tmp_path / "tasks.yaml"
    add_task(
        store,
        id="writer-annotations-proj",
        title="annotations for proj",
        assignee="scitex-writer",
        created_by="scitex-writer",
    )
    return store


def test_resolve_source_ref_is_page_only():
    # Arrange
    ann = Annotation.from_post(_body())
    # Act
    ref = resolve_source_ref(ann)
    # Assert
    assert ref == {"page": 2}


def test_add_annotation_returns_ok(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    empty_store = tmp_path / "empty.yaml"
    # Act
    result = add_annotation(_body(), project="proj", db_path=db, store=empty_store)
    # Assert
    assert result["ok"] is True


def test_add_annotation_assigns_annotation_id(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    empty_store = tmp_path / "empty.yaml"
    # Act
    result = add_annotation(_body(), project="proj", db_path=db, store=empty_store)
    # Assert
    assert result["annotation_id"]


def test_add_annotation_source_ref_is_page_only(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    empty_store = tmp_path / "empty.yaml"
    # Act
    result = add_annotation(_body(), project="proj", db_path=db, store=empty_store)
    # Assert
    assert result["source_ref"] == {"page": 2}


def test_add_annotation_persists_the_row(tmp_path):
    # Arrange
    from scitex_writer._annotations._db import list_annotations

    db = tmp_path / "writer.db"
    empty_store = tmp_path / "empty.yaml"
    add_annotation(_body(), project="proj", db_path=db, store=empty_store)
    # Act
    rows = list_annotations(db_path=db)
    # Assert
    assert len(rows) == 1


def test_add_annotation_notifies_owning_card(tmp_path, todo_store):
    # Arrange
    db = tmp_path / "writer.db"
    # Act
    result = add_annotation(_body(), project="proj", db_path=db, store=todo_store)
    # Assert
    assert result["notified"] is True
