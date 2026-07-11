#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: src/scitex_writer/_core/_engines.py

from scitex_writer._core._engines import (
    DEFAULT_AUTO_ORDER,
    auto_detect_engine,
    get_engine_info,
    get_engine_version,
    list_available_engines,
    verify_engine,
)

_KNOWN_ENGINES = ("tectonic", "latexmk", "3pass")


def test_verify_engine_rejects_unknown_engine():
    # Arrange
    # Act
    # Assert
    assert verify_engine("not-a-real-engine") is False


def test_verify_engine_returns_bool_for_known_engines():
    # Arrange
    # Act
    results = [verify_engine(e) for e in _KNOWN_ENGINES]
    # Assert
    assert all(isinstance(r, bool) for r in results)


def test_get_engine_info_known_engine_is_nonempty():
    # Arrange
    # Act
    info = get_engine_info("tectonic")
    # Assert
    assert info


def test_get_engine_info_unknown_engine_is_empty():
    # Arrange
    # Act
    info = get_engine_info("not-a-real-engine")
    # Assert
    assert info == ""


def test_get_engine_version_unknown_engine_is_none():
    # Arrange
    # Act
    version = get_engine_version("not-a-real-engine")
    # Assert
    assert version is None


def test_auto_detect_engine_returns_a_known_engine():
    # Arrange
    # Act
    engine = auto_detect_engine()
    # Assert
    assert engine in _KNOWN_ENGINES


def test_auto_detect_engine_falls_back_to_3pass_when_nothing_verifies():
    # Arrange
    order = ("not-a-real-engine",)
    # Act
    engine = auto_detect_engine(order)
    # Assert
    assert engine == "3pass"


def test_default_auto_order_matches_priority_doc():
    # Arrange
    # Act
    # Assert: latexmk (fastest dev) -> tectonic (fallback) -> 3pass
    # (guaranteed), matching the shell source's SCITEX_WRITER_AUTO_ORDER default.
    assert DEFAULT_AUTO_ORDER == ("latexmk", "tectonic", "3pass")


def test_list_available_engines_returns_all_three():
    # Arrange
    # Act
    engines = list_available_engines()
    # Assert
    assert [e["engine"] for e in engines] == list(_KNOWN_ENGINES)


def test_list_available_engines_rows_have_expected_keys():
    # Arrange
    # Act
    rows = list_available_engines()
    # Assert
    assert all({"engine", "available", "version", "info"} <= row.keys() for row in rows)
