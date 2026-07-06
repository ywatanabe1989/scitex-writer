#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_writer._annotations._record (Annotation dataclass).

One assert per test (STX-TQ007); no mocks (STX-NM002); no monkeypatch
(PA-306).
"""

from __future__ import annotations

import pytest

from scitex_writer._annotations._record import Annotation


def _body(text: str = "fix this claim") -> dict:
    return {"page": 3, "doc_type": "manuscript", "payload": {"text": text}}


def test_from_post_assigns_annotation_id():
    # Arrange
    body = _body()
    # Act
    ann = Annotation.from_post(body)
    # Assert
    assert ann.annotation_id


def test_from_post_assigns_created_at():
    # Arrange
    body = _body()
    # Act
    ann = Annotation.from_post(body)
    # Assert
    assert ann.created_at


def test_from_post_defaults_status_open():
    # Arrange
    body = _body()
    # Act
    ann = Annotation.from_post(body)
    # Assert
    assert ann.status == "open"


def test_from_post_keeps_text_payload():
    # Arrange
    body = _body("check figure 2")
    # Act
    ann = Annotation.from_post(body)
    # Assert
    assert ann.payload == {"text": "check figure 2"}


def test_to_dict_round_trips_page():
    # Arrange
    ann = Annotation.from_post(_body())
    # Act
    d = ann.to_dict()
    # Assert
    assert d["page"] == 3


def test_from_post_requires_page():
    # Arrange
    body = {"payload": {"text": "x"}}
    # Act
    raises = pytest.raises(ValueError)
    # Assert
    with raises:
        Annotation.from_post(body)


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
