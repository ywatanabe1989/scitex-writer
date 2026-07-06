#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spike-0 tests for the /api/annotations Django handler.

Real Django RequestFactory + real SQLite under a tmp project dir + real
tmp scitex-todo store (pointed via SCITEX_TODO_TASKS_YAML_SHARED so the
real shared store is never written). No mocks (STX-NM002), no monkeypatch
(PA-306), one assert per test (STX-TQ007).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from django.test import RequestFactory

from scitex_writer._django import views


@pytest.fixture
def project_dir(tmp_path):
    p = tmp_path / "myproj"
    (p / "01_manuscript" / "contents").mkdir(parents=True)
    (p / "01_manuscript" / "contents" / "01_intro.tex").write_text(r"\section{Intro}")
    (p / "00_shared" / "bib_files").mkdir(parents=True)
    (p / "00_shared" / "bib_files" / "bibliography.bib").write_text(
        "@article{foo2024, title={Foo}}\n"
    )
    return str(p)


@pytest.fixture
def isolated_todo_store(tmp_path):
    """Point scitex-todo's shared store at a tmp file seeded with the card.

    Env-based isolation (NOT the monkeypatch fixture): the manuscript
    project's owning card is ``writer-annotations-myproj``.
    """
    from scitex_todo import add_task

    store = tmp_path / "todo.yaml"
    add_task(
        store,
        id="writer-annotations-myproj",
        title="annotations for myproj",
        assignee="scitex-writer",
        created_by="scitex-writer",
    )
    prev = os.environ.get("SCITEX_TODO_TASKS_YAML_SHARED")
    os.environ["SCITEX_TODO_TASKS_YAML_SHARED"] = str(store)
    try:
        yield store
    finally:
        if prev is None:
            os.environ.pop("SCITEX_TODO_TASKS_YAML_SHARED", None)
        else:
            os.environ["SCITEX_TODO_TASKS_YAML_SHARED"] = prev


def _post(project: str, body: dict):
    rf = RequestFactory()
    request = rf.post(
        f"/api/annotations?working_dir={project}",
        data=json.dumps(body),
        content_type="application/json",
    )
    return views.api_dispatch(request, "api/annotations")


def _text_body(text: str = "please clarify") -> dict:
    return {"page": 2, "doc_type": "manuscript", "payload": {"text": text}}


def test_post_returns_200(project_dir, isolated_todo_store):
    # Arrange
    body = _text_body()
    # Act
    resp = _post(project_dir, body)
    # Assert
    assert resp.status_code == 200


def test_post_response_is_ok(project_dir, isolated_todo_store):
    # Arrange
    body = _text_body()
    # Act
    data = json.loads(_post(project_dir, body).content)
    # Assert
    assert data["ok"] is True


def test_post_assigns_annotation_id(project_dir, isolated_todo_store):
    # Arrange
    body = _text_body()
    # Act
    data = json.loads(_post(project_dir, body).content)
    # Assert
    assert data["annotation_id"]


def test_post_source_ref_is_page_only(project_dir, isolated_todo_store):
    # Arrange
    body = _text_body()
    # Act
    data = json.loads(_post(project_dir, body).content)
    # Assert
    assert data["source_ref"] == {"page": 2}


def test_post_emit_seam_notifies_owning_card(project_dir, isolated_todo_store):
    # Arrange
    body = _text_body()
    # Act
    data = json.loads(_post(project_dir, body).content)
    # Assert
    assert data["notified"] is True


def test_post_comment_lands_on_the_card(project_dir, isolated_todo_store):
    # Arrange
    from scitex_todo import get_task

    _post(project_dir, _text_body("expand the discussion"))
    # Act
    card = get_task(isolated_todo_store, "writer-annotations-myproj")
    texts = " ".join(c.get("text", "") for c in card.get("comments", []))
    # Assert
    assert "expand the discussion" in texts


def test_get_lists_the_persisted_annotation(project_dir, isolated_todo_store):
    # Arrange
    _post(project_dir, _text_body("first note"))
    rf = RequestFactory()
    request = rf.get(f"/api/annotations?working_dir={project_dir}")
    # Act
    data = json.loads(views.api_dispatch(request, "api/annotations").content)
    # Assert
    assert data["count"] == 1


def test_post_invalid_kind_returns_400(project_dir, isolated_todo_store):
    # Arrange
    body = {"page": 1, "kind": "stroke", "payload": {"text": "x"}}
    # Act
    resp = _post(project_dir, body)
    # Assert
    assert resp.status_code == 400


def test_persisted_db_lives_under_project_runtime(project_dir, isolated_todo_store):
    # Arrange
    _post(project_dir, _text_body())
    # Act
    db = Path(project_dir) / ".scitex" / "writer" / "runtime" / "writer.db"
    # Assert
    assert db.is_file()
