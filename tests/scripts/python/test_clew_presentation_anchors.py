#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scripts/python/test_clew_presentation_anchors.py

"""Contract tests for the live-paper PDF anchors in clew_presentation.tex.

The scitex-live-paper overlay locates a claim in the compiled PDF via the
named destination ``clew-<raw claim id>`` (2026-07-04 contract). These tests
pin the macro-source contract textually: the anchor helper exists, both
location-marking macros (\\clewval and \\clewmark) emit it, the destination
carries the RAW id under the ``clew-`` namespace, and re-anchoring is
one-shot per claim. The compile behaviour itself is exercised by the
existing pdflatex overlay smokes.
"""

from pathlib import Path

import pytest

_STYLES_TEX = (
    Path(__file__).parents[3] / "00_shared" / "latex_styles" / "clew_presentation.tex"
)


@pytest.fixture
def presentation_source():
    return _STYLES_TEX.read_text()


def test_anchor_helper_is_defined(presentation_source):
    # Arrange
    helper = r"\cs_new_protected:Npn \__clew_anchor:nn"
    # Act
    present = helper in presentation_source
    # Assert
    assert present


def test_clewval_and_clewmark_both_emit_anchor(presentation_source):
    # Arrange
    call = r"\__clew_anchor:nn { \l__clew_key_tl } {#1}"
    # Act
    call_count = presentation_source.count(call)
    # Assert
    assert call_count == 2


def test_destination_uses_clew_namespace_with_raw_id(presentation_source):
    # Arrange
    destination = r"\hypertarget { clew- \tl_to_str:n {#2} } {}"
    # Act
    present = destination in presentation_source
    # Assert
    assert present


def test_anchor_is_one_shot_per_claim_id(presentation_source):
    # Arrange
    flag = "clew@anchored@"
    # Act
    present = flag in presentation_source
    # Assert
    assert present


def test_anchor_degrades_without_hyperref(presentation_source):
    # Arrange
    guard = r"\cs_if_exist:NT \hypertarget"
    # Act
    present = guard in presentation_source
    # Assert
    assert present
