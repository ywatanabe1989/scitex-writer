#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: render_clew.py (clew_rendered.tex emit from claims.json v1.3)

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from render_clew import (  # noqa: E402
    render_clew_tex,
    sanitize_id,
)


class TestSanitizeId:
    def test_strips_non_alphanumeric_characters(self):
        # Arrange
        raw = "results_seizure-auc.01"
        # Act
        out = sanitize_id(raw)
        # Assert
        assert out == "resultsseizureauc01"

    def test_matches_presentation_layer_transform(self):
        # Arrange: the same [^a-zA-Z0-9] removal clew_presentation.tex applies.
        raw = "abstract_strongest_patients"
        # Act
        out = sanitize_id(raw)
        # Assert
        assert out == "abstractstrongestpatients"


class TestRenderClewTex:
    _DATA = {
        "palette": {
            "verified": "2E7D32",
            "suspect": "F9A825",
            "unverified": "C62828",
            "exception": "6A1B9A",
        },
        "attestation": {"verified_count": 2, "unverified_count": 1},
        "claims": [
            {"claim_id": "results_repro", "status": "verified",
             "color": "#2E7D32", "value": "13/15 reproduce; p=0.0037"},
            {"claim_id": "table1_events", "status": "unverified",
             "color": "C62828", "value": "Table 1 events"},
        ],
    }

    def test_emits_makeatletter_wrapper(self):
        # Arrange
        # Act
        tex = render_clew_tex(self._DATA)
        # Assert
        assert tex.startswith("\\makeatletter") and tex.rstrip().endswith("\\makeatother")

    def test_defines_the_four_palette_colors(self):
        # Arrange
        # Act
        tex = render_clew_tex(self._DATA)
        # Assert
        assert all(
            f"\\definecolor{{{n}}}{{HTML}}" in tex
            for n in ("clewVerified", "clewSuspect", "clewUnverified", "clewException")
        )

    def test_emits_sanitized_per_claim_value_macro(self):
        # Arrange
        # Act
        tex = render_clew_tex(self._DATA)
        # Assert
        assert "\\@namedef{clew@val@resultsrepro}{13/15 reproduce; p=0.0037}" in tex

    def test_emits_per_claim_hex_and_status(self):
        # Arrange
        # Act
        tex = render_clew_tex(self._DATA)
        # Assert
        assert ("\\@namedef{clew@hex@table1events}{C62828}" in tex) and (
            "\\@namedef{clew@status@table1events}{unverified}" in tex
        )

    def test_aggregate_counts_from_attestation(self):
        # Arrange
        # Act
        tex = render_clew_tex(self._DATA)
        # Assert
        assert ("\\def\\clew@total{3}" in tex) and ("\\def\\clew@verified{2}" in tex)

    def test_allverified_zero_when_some_unverified(self):
        # Arrange
        # Act
        tex = render_clew_tex(self._DATA)
        # Assert
        assert "\\def\\clew@allverified{0}" in tex

    def test_allverified_one_when_all_verified(self):
        # Arrange
        data = {
            "attestation": {"verified_count": 2, "unverified_count": 0},
            "claims": [
                {"claim_id": "a", "status": "verified", "value": "x"},
                {"claim_id": "b", "status": "verified", "value": "y"},
            ],
        }
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\def\\clew@allverified{1}" in tex

    def test_accepts_claims_as_dict_keyed_by_id(self):
        # Arrange
        data = {"claims": {"myclaim": {"status": "verified", "value": "v"}}}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\@namedef{clew@val@myclaim}{v}" in tex

    def test_value_emitted_verbatim_without_reescaping(self):
        # Arrange: clew provides display-ready LaTeX; must not be double-escaped.
        data = {"claims": [
            {"claim_id": "c", "status": "verified", "value": "AUC $\\times$ 0.58, clinical\\_only"}
        ]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "AUC $\\times$ 0.58, clinical\\_only" in tex


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
