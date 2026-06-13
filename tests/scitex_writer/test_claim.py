#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-19
# File: tests/python/test_claim.py

"""Tests for scitex_writer claim feature.

Tests CRUD operations and LaTeX rendering via public API (scitex_writer.claim).
All file I/O uses tmp_path to avoid touching actual project files.
"""

import json
from pathlib import Path


def _make_project(tmp_path: Path) -> Path:
    """Create minimal project structure for claim tests."""
    shared = tmp_path / "00_shared"
    shared.mkdir(parents=True)
    return str(tmp_path)


class TestClaimAdd:
    """Test adding claims."""

    def test_add_statistic_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        result = sc.add(
            project_dir=project_dir,
            claim_id="group_comparison",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
            context="Group A vs B",
        )
        # Assert
        assert result["success"]

    def test_add_statistic_returns_matching_claim_id(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        result = sc.add(
            project_dir=project_dir,
            claim_id="group_comparison",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
            context="Group A vs B",
        )
        # Assert
        assert result["claim_id"] == "group_comparison"

    def test_add_value_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        result = sc.add(
            project_dir=project_dir,
            claim_id="rt_mean",
            claim_type="value",
            value={"value": 42.3, "unit": "ms"},
        )
        # Assert
        assert result["success"]

    def test_add_citation_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        result = sc.add(
            project_dir=project_dir,
            claim_id="key_finding",
            claim_type="citation",
            value={"text": "as previously reported"},
        )
        # Assert
        assert result["success"]

    def test_add_creates_claims_json_file(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        sc.add(
            project_dir=project_dir,
            claim_id="c1",
            claim_type="citation",
            value={"text": "test"},
        )
        # Assert
        claims_file = Path(project_dir) / "00_shared" / "claims.json"
        assert claims_file.exists()

    def test_add_records_claim_id_in_claims_json(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        sc.add(
            project_dir=project_dir,
            claim_id="c1",
            claim_type="citation",
            value={"text": "test"},
        )
        # Assert
        claims_file = Path(project_dir) / "00_shared" / "claims.json"
        data = json.loads(claims_file.read_text())
        assert "c1" in data["claims"]

    def test_add_preserves_existing_claims_in_list(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="c1",
            claim_type="citation",
            value={"text": "first"},
        )
        # Act
        sc.add(
            project_dir=project_dir,
            claim_id="c2",
            claim_type="citation",
            value={"text": "second"},
        )
        # Assert
        result = sc.list(project_dir=project_dir)
        assert result["count"] == 2


class TestClaimList:
    """Test listing claims."""

    def test_list_empty_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        result = sc.list(project_dir=project_dir)
        # Assert
        assert result["success"]

    def test_list_empty_returns_zero_count(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        result = sc.list(project_dir=project_dir)
        # Assert
        assert result["count"] == 0

    def test_list_empty_returns_empty_claims_list(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        result = sc.list(project_dir=project_dir)
        # Assert
        assert result["claims"] == []

    def test_list_after_add_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="stat1",
            claim_type="statistic",
            value={"t": 2.1, "df": 20, "p": 0.05, "d": 0.4},
        )
        # Act
        result = sc.list(project_dir=project_dir)
        # Assert
        assert result["success"]

    def test_list_after_add_returns_count_one(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="stat1",
            claim_type="statistic",
            value={"t": 2.1, "df": 20, "p": 0.05, "d": 0.4},
        )
        # Act
        result = sc.list(project_dir=project_dir)
        # Assert
        assert result["count"] == 1

    def test_list_after_add_returns_matching_claim_id(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="stat1",
            claim_type="statistic",
            value={"t": 2.1, "df": 20, "p": 0.05, "d": 0.4},
        )
        # Act
        result = sc.list(project_dir=project_dir)
        # Assert
        assert result["claims"][0]["claim_id"] == "stat1"

    def test_list_after_add_returns_matching_claim_type(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="stat1",
            claim_type="statistic",
            value={"t": 2.1, "df": 20, "p": 0.05, "d": 0.4},
        )
        # Act
        result = sc.list(project_dir=project_dir)
        # Assert
        assert result["claims"][0]["type"] == "statistic"

    def test_list_includes_preview_nature_field(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 3.5, "df": 10, "p": 0.006, "d": 0.9},
        )
        # Act
        result = sc.list(project_dir=project_dir)
        # Assert
        claim = result["claims"][0]
        assert "preview_nature" in claim


class TestClaimGet:
    """Test getting individual claims."""

    def test_get_existing_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="my_claim",
            claim_type="citation",
            value={"text": "test text"},
        )
        # Act
        result = sc.get(project_dir=project_dir, claim_id="my_claim")
        # Assert
        assert result["success"]

    def test_get_existing_returns_matching_claim_type(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="my_claim",
            claim_type="citation",
            value={"text": "test text"},
        )
        # Act
        result = sc.get(project_dir=project_dir, claim_id="my_claim")
        # Assert
        assert result["claim"]["type"] == "citation"

    def test_get_missing_returns_success_false(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        result = sc.get(project_dir=project_dir, claim_id="nonexistent")
        # Assert
        assert not result["success"]


class TestClaimRemove:
    """Test removing claims."""

    def test_remove_existing_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="to_delete",
            claim_type="citation",
            value={"text": "delete me"},
        )
        # Act
        result = sc.remove(project_dir=project_dir, claim_id="to_delete")
        # Assert
        assert result["success"]

    def test_remove_existing_leaves_zero_claims(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="to_delete",
            claim_type="citation",
            value={"text": "delete me"},
        )
        # Act
        sc.remove(project_dir=project_dir, claim_id="to_delete")
        # Assert
        assert sc.list(project_dir=project_dir)["count"] == 0

    def test_remove_missing_returns_success_false(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        result = sc.remove(project_dir=project_dir, claim_id="ghost")
        # Assert
        assert not result["success"]


class TestClaimFormat:
    """Test formatting claims into rendered strings."""

    def test_format_statistic_nature_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="s1", style="nature")
        # Assert
        assert result["success"]

    def test_format_statistic_nature_rendered_contains_t(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="s1", style="nature")
        # Assert
        assert "t" in result["rendered"]

    def test_format_statistic_nature_rendered_contains_t_value(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="s1", style="nature")
        # Assert
        assert "4.23" in result["rendered"]

    def test_format_statistic_apa_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="s1", style="apa")
        # Assert
        assert result["success"]

    def test_format_statistic_apa_rendered_contains_cohen(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="s1", style="apa")
        # Assert
        assert "Cohen" in result["rendered"]

    def test_format_statistic_plain_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="s1", style="plain")
        # Assert
        assert result["success"]

    def test_format_statistic_plain_rendered_has_no_math_delim(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="s1", style="plain")
        # Assert
        assert "$" not in result["rendered"]

    def test_format_small_p_returns_success_true(self, tmp_path):
        """p < 0.001 should render as < 0.001, not 0.000."""
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 5.0, "df": 100, "p": 0.0005, "d": 1.0},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="s1", style="nature")
        # Assert
        assert result["success"]

    def test_format_small_p_rendered_shows_threshold(self, tmp_path):
        """p < 0.001 should render as < 0.001, not 0.000."""
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 5.0, "df": 100, "p": 0.0005, "d": 1.0},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="s1", style="nature")
        # Assert
        assert "0.001" in result["rendered"]

    def test_format_citation_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="c1",
            claim_type="citation",
            value={"text": "as shown previously"},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="c1", style="nature")
        # Assert
        assert result["success"]

    def test_format_citation_rendered_contains_text(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="c1",
            claim_type="citation",
            value={"text": "as shown previously"},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="c1", style="nature")
        # Assert
        assert "as shown previously" in result["rendered"]

    def test_format_value_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="v1",
            claim_type="value",
            value={"value": 42.3, "unit": "ms"},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="v1", style="nature")
        # Assert
        assert result["success"]

    def test_format_value_rendered_contains_number(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="v1",
            claim_type="value",
            value={"value": 42.3, "unit": "ms"},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="v1", style="nature")
        # Assert
        assert "42.3" in result["rendered"]

    def test_format_value_rendered_contains_unit(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="v1",
            claim_type="value",
            value={"value": 42.3, "unit": "ms"},
        )
        # Act
        result = sc.format(project_dir=project_dir, claim_id="v1", style="nature")
        # Assert
        assert "ms" in result["rendered"]


class TestClaimRender:
    """Test rendering all claims to claims_rendered.tex."""

    def test_render_returns_success_true(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="grp",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        result = sc.render(project_dir=project_dir)
        # Assert
        assert result["success"]

    def test_render_creates_tex_file(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="grp",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex_path = Path(project_dir) / "00_shared" / "claims_rendered.tex"
        assert tex_path.exists()

    def test_render_tex_contains_vclaim_macro(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="my_stat",
            claim_type="statistic",
            value={"t": 2.0, "df": 10, "p": 0.03, "d": 0.5},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "\\vclaim" in tex

    def test_render_tex_sanitizes_id_without_underscores(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="my_stat",
            claim_type="statistic",
            value={"t": 2.0, "df": 10, "p": 0.03, "d": 0.5},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "mystat" in tex

    def test_render_tex_defines_nature_macro(self, tmp_path):
        """Rendered .tex defines nature, apa, and plain macros for each claim."""
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 3.0, "df": 20, "p": 0.005, "d": 0.7},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "@nature" in tex

    def test_render_tex_defines_apa_macro(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 3.0, "df": 20, "p": 0.005, "d": 0.7},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "@apa" in tex

    def test_render_tex_defines_plain_macro(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 3.0, "df": 20, "p": 0.005, "d": 0.7},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "@plain" in tex

    def test_render_empty_returns_success_true(self, tmp_path):
        """Rendering with no claims still creates a valid .tex file."""
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        result = sc.render(project_dir=project_dir)
        # Assert
        assert result["success"]

    def test_render_empty_reports_zero_claims_count(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        result = sc.render(project_dir=project_dir)
        # Assert
        assert result["claims_count"] == 0

    def test_render_empty_still_creates_tex_file(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex_path = Path(project_dir) / "00_shared" / "claims_rendered.tex"
        assert tex_path.exists()

    def test_render_emits_hypertarget_for_claim(self, tmp_path):
        """Each claim's rendered output wraps in \\hypertarget{vclaim-<id>}{...}
        so PDF.js can locate claim text for Living Paper hover popups (#133)."""
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="group_comparison",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "\\hypertarget{vclaim-groupcomparison}" in tex

    def test_render_emits_anchored_flag_for_claim(self, tmp_path):
        """The target is emitted once per claim via a one-shot flag so repeat
        \\vclaim{id} calls don't warn about duplicate destinations."""
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="group_comparison",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "v@claim@groupcomparison@anchored" in tex

    def test_render_emits_nature_style_macro_for_claim(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="group_comparison",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "v@claim@groupcomparison@nature" in tex

    def test_render_emits_apa_style_macro_for_claim(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="group_comparison",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "v@claim@groupcomparison@apa" in tex

    def test_render_emits_plain_style_macro_for_claim(self, tmp_path):
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="group_comparison",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "v@claim@groupcomparison@plain" in tex

    def test_render_uses_expandafter_ifx_guard(self, tmp_path):
        """The one-shot flag pattern should let multiple \\vclaim{id} calls
        expand without re-emitting the same named destination."""
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="x",
            claim_type="value",
            value={"number": 42, "unit": "Hz"},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "\\expandafter\\ifx\\csname v@claim@x@anchored\\endcsname\\relax" in tex

    def test_render_uses_global_namedef_flag_setter(self, tmp_path):
        """Global flag-setter so second call sees \relax absent."""
        # Arrange
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="x",
            claim_type="value",
            value={"number": 42, "unit": "Hz"},
        )
        # Act
        sc.render(project_dir=project_dir)
        # Assert
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "\\global\\@namedef{v@claim@x@anchored}" in tex


class TestClaimPublicApi:
    """Test that scitex_writer.claim exposes the correct public interface."""

    def test_public_function_add_exists(self):
        # Arrange
        import scitex_writer.claim as sc

        # Act
        result = hasattr(sc, "add") and callable(getattr(sc, "add"))
        # Assert
        assert result

    def test_public_function_list_exists(self):
        # Arrange
        import scitex_writer.claim as sc

        # Act
        result = hasattr(sc, "list") and callable(getattr(sc, "list"))
        # Assert
        assert result

    def test_public_function_get_exists(self):
        # Arrange
        import scitex_writer.claim as sc

        # Act
        result = hasattr(sc, "get") and callable(getattr(sc, "get"))
        # Assert
        assert result

    def test_public_function_remove_exists(self):
        # Arrange
        import scitex_writer.claim as sc

        # Act
        result = hasattr(sc, "remove") and callable(getattr(sc, "remove"))
        # Assert
        assert result

    def test_public_function_format_exists(self):
        # Arrange
        import scitex_writer.claim as sc

        # Act
        result = hasattr(sc, "format") and callable(getattr(sc, "format"))
        # Assert
        assert result

    def test_public_function_render_exists(self):
        # Arrange
        import scitex_writer.claim as sc

        # Act
        result = hasattr(sc, "render") and callable(getattr(sc, "render"))
        # Assert
        assert result

    def test_compilation_result_hidden_from_top_level_all(self):
        """Internal dataclasses should not appear in scitex_writer.__all__."""
        # Arrange
        import scitex_writer as sw

        # Act
        present = "CompilationResult" in sw.__all__
        # Assert
        assert not present

    def test_manuscript_tree_hidden_from_top_level_all(self):
        # Arrange
        import scitex_writer as sw

        # Act
        present = "ManuscriptTree" in sw.__all__
        # Assert
        assert not present

    def test_revision_tree_hidden_from_top_level_all(self):
        # Arrange
        import scitex_writer as sw

        # Act
        present = "RevisionTree" in sw.__all__
        # Assert
        assert not present

    def test_supplementary_tree_hidden_from_top_level_all(self):
        # Arrange
        import scitex_writer as sw

        # Act
        present = "SupplementaryTree" in sw.__all__
        # Assert
        assert not present

    def test_claim_module_in_top_level_all_namespace(self):
        """claim module should be in scitex_writer.__all__."""
        # Arrange
        import scitex_writer as sw

        # Act
        present = "claim" in sw.__all__
        # Assert
        assert present
