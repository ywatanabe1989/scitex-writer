#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_claim_citations.py
#
# THE BUG THIS PINS. An undefined \vclaim{id} silently renders as a
# [claim:id] placeholder in the PDF — the same failure class as an undefined
# \cite, in the one citation type that binds prose to computed evidence. There
# was no compile-stage check for it. Found by paper-scitex-clew: 4 abstract
# headline numbers shipped as [claim:...] placeholders through human review.
#
# The sanitize trap is the subtle part: the defined macro is named from
# _sanitize_id(id) (letters+digits only), so \vclaim{a_b_c} must match a claim
# defined as "a_b_c" via its sanitized form "abc" — a raw string compare
# silently misses, which is exactly why the real placeholders (underscored ids)
# evaded everything.
#
# No mocks: the whole point is to exercise the real script against real files.

import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

_SCRIPT = ROOT_DIR / "scripts" / "python" / "check_claim_citations.py"

from check_claim_citations import extract_vclaims  # noqa: E402

# ============================================================================
# extract_vclaims — the scanner
# ============================================================================


class TestExtractVclaims:
    def test_extracts_a_plain_vclaim(self, tmp_path):
        # Arrange
        tex = tmp_path / "m.tex"
        tex.write_text("The value is \\vclaim{group_effect}.\n")

        # Act
        used = extract_vclaims([tex])

        # Assert
        assert "group_effect" in used

    def test_extracts_id_ignoring_the_optional_style_arg(self, tmp_path):
        # Arrange: \vclaim[apa]{id} — the [..] is render style, the {..} is the id.
        tex = tmp_path / "m.tex"
        tex.write_text("\\vclaim[apa]{group_effect}\n")

        # Act
        used = extract_vclaims([tex])

        # Assert
        assert "group_effect" in used

    def test_skips_a_commented_out_vclaim(self, tmp_path):
        # Arrange
        tex = tmp_path / "m.tex"
        tex.write_text("real \\vclaim{a}\n% \\vclaim{commented}\n")

        # Act
        used = extract_vclaims([tex])

        # Assert
        assert "commented" not in used

    def test_skips_the_macro_definition_argument(self, tmp_path):
        # Arrange: \vclaim's own definition uses ##2 — never a real citation.
        tex = tmp_path / "m.tex"
        tex.write_text("\\providecommand{\\vclaim}[2]{\\vclaim{#2}}\n")

        # Act
        used = extract_vclaims([tex])

        # Assert
        assert not any(k.startswith("#") for k in used)


# ============================================================================
# End-to-end — what the compile stage actually runs
# ============================================================================


def _project(tmp_path, tex_body, claims_json=None):
    """A minimal project tree the script can scan."""
    contents = tmp_path / "01_manuscript" / "contents"
    contents.mkdir(parents=True)
    (contents / "section.tex").write_text(tex_body)
    if claims_json is not None:
        shared = tmp_path / "00_shared"
        shared.mkdir(parents=True)
        (shared / "claims.json").write_text(claims_json)
    return tmp_path


def _run(project_dir):
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(project_dir)],
        capture_output=True,
        text=True,
    )


class TestEndToEnd:
    def test_undefined_vclaim_fails_the_gate(self, tmp_path):
        # Arrange: THE BUG — a \vclaim with no matching claim.
        proj = _project(
            tmp_path,
            "Headline: \\vclaim{cohorta_inter_ncaps}.\n",
            claims_json='{"claims": {"registered_one": {"type": "value"}}}',
        )

        # Act
        result = _run(proj)

        # Assert
        assert result.returncode == 1

    def test_the_failure_names_the_undefined_id(self, tmp_path):
        # Arrange
        proj = _project(
            tmp_path,
            "Headline: \\vclaim{cohorta_inter_ncaps}.\n",
            claims_json='{"claims": {"registered_one": {"type": "value"}}}',
        )

        # Act
        result = _run(proj)

        # Assert
        assert "cohorta_inter_ncaps" in result.stdout

    def test_punctuation_variant_resolves_via_sanitize_not_raw_match(self, tmp_path):
        # Arrange: THE SANITIZE TRAP, exercised so it is NOT vacuous. The claim
        # is keyed "group-a-effect" (hyphens); the manuscript cites
        # \vclaim{group_a_effect} (underscores). BOTH sanitize to "groupaeffect",
        # so the macro \v@claim@groupaeffect is defined and LaTeX resolves it —
        # the check must agree (exit 0). A naive RAW string compare would see
        # "group_a_effect" != "group-a-effect" and cry wolf. (Mutating _sanitize
        # to identity flips this test to a failure, which is how I confirmed it
        # actually tests the sanitize rather than passing regardless.)
        proj = _project(
            tmp_path,
            "Value: \\vclaim{group_a_effect}.\n",
            claims_json='{"claims": {"group-a-effect": {"type": "value"}}}',
        )

        # Act
        result = _run(proj)

        # Assert
        assert result.returncode == 0

    def test_a_manuscript_with_no_vclaims_passes(self, tmp_path):
        # Arrange: nothing to validate is an honest pass, not a failure.
        proj = _project(tmp_path, "Plain prose, no claims.\n")

        # Act
        result = _run(proj)

        # Assert
        assert result.returncode == 0

    def test_vclaim_used_but_no_claims_json_fails(self, tmp_path):
        # Arrange: a manuscript citing computed values with no value store at
        # all — every \vclaim is a placeholder. This must fail, not pass by
        # vacuously finding "no defined claims to contradict".
        proj = _project(tmp_path, "Value: \\vclaim{anything}.\n")

        # Act
        result = _run(proj)

        # Assert
        assert result.returncode == 1

    def test_off_level_disables_the_gate(self, tmp_path):
        # Arrange: an undefined vclaim, but the check is turned off.
        proj = _project(
            tmp_path,
            "Headline: \\vclaim{undefined_one}.\n",
            claims_json='{"claims": {}}',
        )

        # Act
        result = subprocess.run(
            [sys.executable, str(_SCRIPT), str(proj), "--level", "off"],
            capture_output=True,
            text=True,
        )

        # Assert
        assert result.returncode == 0
