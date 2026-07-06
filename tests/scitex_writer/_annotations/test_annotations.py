#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spike-0 tests for scitex_writer._annotations.

Real SQLite in ``tmp_path`` and a real tmp scitex-todo ``tasks.yaml`` — no
mocks (STX-NM002), no monkeypatch (PA-306), one assert per test (STX-TQ007).
The emit rail is pointed at a tmp store so the real shared
``~/.scitex/todo/tasks.yaml`` is never written.
"""

from __future__ import annotations

import pytest

from scitex_writer._annotations import (
    Annotation,
    add_annotation,
    list_annotations,
    persist,
    resolve_source_ref,
)


def _text_comment_body(text: str = "fix this claim") -> dict:
    return {"page": 3, "doc_type": "manuscript", "payload": {"text": text}}


# --- persist round-trip -----------------------------------------------------


def test_persist_then_list_returns_one_row(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    ann = Annotation.from_post(_text_comment_body())
    # Act
    persist(ann, db_path=db)
    rows = list_annotations(db_path=db)
    # Assert
    assert len(rows) == 1


def test_persist_round_trips_text_payload(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    ann = Annotation.from_post(_text_comment_body("check figure 2"))
    persist(ann, db_path=db)
    # Act
    rows = list_annotations(db_path=db)
    # Assert
    assert rows[0]["payload"] == {"text": "check figure 2"}


def test_list_annotations_filters_by_status(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    persist(Annotation.from_post(_text_comment_body()), db_path=db)
    # Act
    rows = list_annotations(db_path=db, status="resolved")
    # Assert
    assert rows == []


def test_resolve_source_ref_is_page_only(tmp_path):
    # Arrange
    ann = Annotation.from_post(_text_comment_body())
    # Act
    ref = resolve_source_ref(ann)
    # Assert
    assert ref == {"page": 3}


def test_from_post_rejects_non_text_comment_kind():
    # Arrange
    body = {"page": 1, "kind": "stroke", "payload": {"text": "x"}}
    # Act
    raises = pytest.raises(ValueError)
    # Assert
    with raises:
        Annotation.from_post(body)


def test_from_post_rejects_empty_text():
    # Arrange
    body = {"page": 1, "payload": {"text": "   "}}
    # Act
    raises = pytest.raises(ValueError)
    # Assert
    with raises:
        Annotation.from_post(body)


# --- emit seam (hermetic: tmp scitex-todo store) ----------------------------


@pytest.fixture
def todo_store(tmp_path):
    """A real tmp scitex-todo store seeded with the owning card."""
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


def test_add_annotation_reports_notified(tmp_path, todo_store):
    # Arrange
    db = tmp_path / "writer.db"
    # Act
    result = add_annotation(
        _text_comment_body(),
        project="proj",
        db_path=db,
        store=todo_store,
    )
    # Assert
    assert result["notified"] is True


def test_add_annotation_posts_comment_to_owning_card(tmp_path, todo_store):
    # Arrange
    from scitex_todo import get_task

    db = tmp_path / "writer.db"
    add_annotation(
        _text_comment_body("rewrite the abstract"),
        project="proj",
        db_path=db,
        store=todo_store,
    )
    # Act
    card = get_task(todo_store, "writer-annotations-proj")
    comment_texts = " ".join(c.get("text", "") for c in card.get("comments", []))
    # Assert
    assert "rewrite the abstract" in comment_texts


def test_add_annotation_persists_even_when_notify_fails(tmp_path):
    # Arrange — no card in the store → notify fails soft, persist still happens
    db = tmp_path / "writer.db"
    empty_store = tmp_path / "empty.yaml"
    add_annotation(
        _text_comment_body(),
        project="missing",
        db_path=db,
        store=empty_store,
    )
    # Act
    rows = list_annotations(db_path=db)
    # Assert
    assert len(rows) == 1
