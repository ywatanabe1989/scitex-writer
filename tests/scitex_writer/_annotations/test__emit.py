#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_writer._annotations._emit (the emit seam).

The scitex-todo rail is OPTIONAL — tests that assert a comment was posted
``pytest.importorskip("scitex_todo")`` so they skip where the dep is
absent (e.g. CI) and run where present. NO mock of scitex_todo
(STX-NM002). Real tmp store isolates the shared ``tasks.yaml``. One assert
per test (STX-TQ007); no monkeypatch (PA-306).
"""

from __future__ import annotations

import pytest

from scitex_writer._annotations._emit import emit, render_summary
from scitex_writer._annotations._record import Annotation


def _annotation(text: str = "fix this claim") -> Annotation:
    return Annotation.from_post(
        {"page": 3, "doc_type": "manuscript", "payload": {"text": text}}
    )


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


def test_render_summary_includes_text():
    # Arrange
    record = _annotation("rewrite abstract").to_dict()
    # Act
    summary = render_summary(record)
    # Assert
    assert "rewrite abstract" in summary


def test_emit_persists_even_when_notify_fails(tmp_path):
    # Arrange — no card / no rail → notify fails soft, persist still happens
    from scitex_writer._annotations._db import list_annotations

    db = tmp_path / "writer.db"
    empty_store = tmp_path / "empty.yaml"
    # Act
    emit(_annotation(), project="missing", db_path=db, store=empty_store)
    # Assert
    assert len(list_annotations(db_path=db)) == 1


def test_emit_reports_persisted_true(tmp_path):
    # Arrange
    db = tmp_path / "writer.db"
    empty_store = tmp_path / "empty.yaml"
    # Act
    result = emit(_annotation(), project="missing", db_path=db, store=empty_store)
    # Assert
    assert result["persisted"] is True


def test_emit_surfaces_notify_error_when_rail_unavailable(tmp_path):
    # Arrange — missing card (or absent rail) is surfaced, never silent
    db = tmp_path / "writer.db"
    empty_store = tmp_path / "empty.yaml"
    # Act
    result = emit(_annotation(), project="missing", db_path=db, store=empty_store)
    # Assert
    assert result["notify_error"] is not None


def test_emit_reports_notified_true_with_seeded_card(tmp_path, todo_store):
    # Arrange
    db = tmp_path / "writer.db"
    # Act
    result = emit(_annotation(), project="proj", db_path=db, store=todo_store)
    # Assert
    assert result["notified"] is True


def test_emit_posts_comment_to_owning_card(tmp_path, todo_store):
    # Arrange
    from scitex_todo import get_task

    db = tmp_path / "writer.db"
    emit(
        _annotation("rewrite the abstract"),
        project="proj",
        db_path=db,
        store=todo_store,
    )
    # Act
    card = get_task(todo_store, "writer-annotations-proj")
    texts = " ".join(c.get("text", "") for c in card.get("comments", []))
    # Assert
    assert "rewrite the abstract" in texts
