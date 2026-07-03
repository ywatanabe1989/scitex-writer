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


class TestClew0219Schema:
    """clew 0.2.19: claim_value field, no color/palette/attestation, status
    'registered' + verified_at (null = not chain-verified)."""

    _CLAIM = {
        "claim_id": "results_perpatient_auc",
        "claim_value": "0.651",
        "claim_type": "value",
        "status": "registered",
        "verified_at": None,
    }

    def test_reads_the_claim_value_field(self):
        # Arrange
        data = {"claims": [self._CLAIM]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\@namedef{clew@val@resultsperpatientauc}{0.651}" in tex

    def test_registered_unverified_renders_red(self):
        # Arrange: no verified_at -> unverified verdict -> red palette hex.
        data = {"claims": [self._CLAIM]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert ("\\@namedef{clew@status@resultsperpatientauc}{unverified}" in tex) and (
            "\\@namedef{clew@hex@resultsperpatientauc}{C62828}" in tex
        )

    def test_registered_with_verified_at_renders_verified(self):
        # Arrange
        claim = dict(self._CLAIM, verified_at="2026-07-01T00:00:00Z")
        data = {"claims": [claim]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\@namedef{clew@status@resultsperpatientauc}{verified}" in tex

    def test_aggregate_computed_without_attestation_block(self):
        # Arrange: 2 registered (unverified) + 1 verified, no attestation.
        data = {"claims": [
            dict(self._CLAIM, claim_id="a"),
            dict(self._CLAIM, claim_id="b"),
            dict(self._CLAIM, claim_id="c", verified_at="2026-07-01T00:00:00Z"),
        ]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert ("\\def\\clew@total{3}" in tex) and ("\\def\\clew@verified{1}" in tex)

    def test_math_value_emitted_verbatim(self):
        # Arrange: real 0.2.19 value strings carry LaTeX math.
        data = {"claims": [dict(self._CLAIM, claim_id="x", claim_value="$80\\times$")]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\@namedef{clew@val@x}{$80\\times$}" in tex


class TestCitationAndFigureClaims:
    """render_clew is claim_type-agnostic: citation (keyed by bibkey) and figure
    (keyed by save-path) claims get the same clew@hex/status@<id> macros the
    \\clewcite / \\clewfig macros read."""

    def test_verified_citation_emits_green_hex_by_bibkey(self):
        # Arrange
        data = {"claims": [{
            "claim_id": "Kuhlmann2018", "claim_type": "citation",
            "status": "verified", "verified_at": "2026-07-01T00:00:00Z",
        }]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\@namedef{clew@hex@Kuhlmann2018}{2E7D32}" in tex

    def test_unverified_citation_emits_red_hex_by_bibkey(self):
        # Arrange
        data = {"claims": [{
            "claim_id": "Freestone2015", "claim_type": "citation",
            "status": "registered", "verified_at": None,
        }]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\@namedef{clew@hex@Freestone2015}{C62828}" in tex

    def test_figure_claim_keyed_by_sanitized_save_path(self):
        # Arrange
        data = {"claims": [{
            "claim_id": "figures/01_main.jpg", "claim_type": "figure",
            "status": "registered", "verified_at": None,
        }]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\@namedef{clew@hex@figures01mainjpg}{C62828}" in tex

    def test_v15_failed_status_maps_to_red_bucket(self):
        # Arrange: unified schema 1.5 renamed the red state unverified->failed.
        data = {"claims": [{
            "claim_id": "Stub2023", "claim_type": "citation",
            "status": "failed", "claim_value": "",
        }]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert ("\\@namedef{clew@status@Stub2023}{unverified}" in tex) and (
            "\\@namedef{clew@hex@Stub2023}{C62828}" in tex
        )

    def test_v15_palette_failed_key_lands_on_red_color(self):
        # Arrange: 1.5 palette keys the red state "failed" (cf222e).
        data = {
            "palette": {"verified": "2da44e", "suspect": "d29922",
                        "failed": "cf222e", "exception": "8250df"},
            "claims": [{"claim_id": "c", "claim_type": "value",
                        "status": "failed", "claim_value": "x"}],
        }
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\definecolor{clewUnverified}{HTML}{CF222E}" in tex

    def test_v15_nested_attestation_counts_shape(self):
        # Arrange: 1.5 attestation nests counts {total, verified, ...}.
        data = {
            "attestation": {"badge_state": "partial",
                            "counts": {"total": 5, "verified": 2}},
            "claims": [],
        }
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert ("\\def\\clew@total{5}" in tex) and ("\\def\\clew@verified{2}" in tex)

    def test_display_color_field_is_honored_over_palette(self):
        # Arrange: clew 0.4.0 emits per-entry `display_color` (frozen name).
        data = {"claims": [{
            "claim_id": "c", "claim_type": "value", "status": "verified",
            "claim_value": "x", "display_color": "#123ABC",
        }]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\@namedef{clew@hex@c}{123ABC}" in tex

    def test_v16_unsourced_status_folds_to_amber_suspect(self):
        # Arrange: clew 1.6 adds an `unsourced` state; writer folds it to suspect.
        data = {"claims": [{"claim_id": "u", "claim_type": "value",
                            "status": "unsourced", "claim_value": "x"}]}
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\@namedef{clew@status@u}{suspect}" in tex

    def test_v16_unsourced_palette_key_preserves_suspect_color(self):
        # Arrange: clew 1.6 palette carries BOTH suspect and unsourced hexes.
        data = {
            "palette": {"verified": "2da44e", "suspect": "d29922",
                        "unsourced": "b26a00", "failed": "cf222e",
                        "exception": "8250df"},
            "claims": [],
        }
        # Act
        tex = render_clew_tex(data)
        # Assert
        assert "\\definecolor{clewSuspect}{HTML}{D29922}" in tex


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
