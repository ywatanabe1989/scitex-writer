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

    def test_add_statistic(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        result = sc.add(
            project_dir=project_dir,
            claim_id="group_comparison",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
            context="Group A vs B",
        )
        assert result["success"]
        assert result["claim_id"] == "group_comparison"

    def test_add_value(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        result = sc.add(
            project_dir=project_dir,
            claim_id="rt_mean",
            claim_type="value",
            value={"value": 42.3, "unit": "ms"},
        )
        assert result["success"]

    def test_add_citation(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        result = sc.add(
            project_dir=project_dir,
            claim_id="key_finding",
            claim_type="citation",
            value={"text": "as previously reported"},
        )
        assert result["success"]

    def test_add_creates_claims_json(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="c1",
            claim_type="citation",
            value={"text": "test"},
        )
        claims_file = Path(project_dir) / "00_shared" / "claims.json"
        assert claims_file.exists()
        data = json.loads(claims_file.read_text())
        assert "c1" in data["claims"]

    def test_add_preserves_existing(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="c1",
            claim_type="citation",
            value={"text": "first"},
        )
        sc.add(
            project_dir=project_dir,
            claim_id="c2",
            claim_type="citation",
            value={"text": "second"},
        )
        result = sc.list(project_dir=project_dir)
        assert result["count"] == 2


class TestClaimList:
    """Test listing claims."""

    def test_list_empty(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        result = sc.list(project_dir=project_dir)
        assert result["success"]
        assert result["count"] == 0
        assert result["claims"] == []

    def test_list_after_add(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="stat1",
            claim_type="statistic",
            value={"t": 2.1, "df": 20, "p": 0.05, "d": 0.4},
        )
        result = sc.list(project_dir=project_dir)
        assert result["success"]
        assert result["count"] == 1
        assert result["claims"][0]["claim_id"] == "stat1"
        assert result["claims"][0]["type"] == "statistic"

    def test_list_includes_preview(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 3.5, "df": 10, "p": 0.006, "d": 0.9},
        )
        result = sc.list(project_dir=project_dir)
        claim = result["claims"][0]
        assert "preview_nature" in claim


class TestClaimGet:
    """Test getting individual claims."""

    def test_get_existing(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="my_claim",
            claim_type="citation",
            value={"text": "test text"},
        )
        result = sc.get(project_dir=project_dir, claim_id="my_claim")
        assert result["success"]
        assert result["claim"]["type"] == "citation"

    def test_get_missing(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        result = sc.get(project_dir=project_dir, claim_id="nonexistent")
        assert not result["success"]


class TestClaimRemove:
    """Test removing claims."""

    def test_remove_existing(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="to_delete",
            claim_type="citation",
            value={"text": "delete me"},
        )
        result = sc.remove(project_dir=project_dir, claim_id="to_delete")
        assert result["success"]
        assert sc.list(project_dir=project_dir)["count"] == 0

    def test_remove_missing(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        result = sc.remove(project_dir=project_dir, claim_id="ghost")
        assert not result["success"]


class TestClaimFormat:
    """Test formatting claims into rendered strings."""

    def test_format_statistic_nature(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        result = sc.format(project_dir=project_dir, claim_id="s1", style="nature")
        assert result["success"]
        assert "t" in result["rendered"]
        assert "4.23" in result["rendered"]

    def test_format_statistic_apa(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        result = sc.format(project_dir=project_dir, claim_id="s1", style="apa")
        assert result["success"]
        assert "Cohen" in result["rendered"]

    def test_format_statistic_plain(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        result = sc.format(project_dir=project_dir, claim_id="s1", style="plain")
        assert result["success"]
        assert "$" not in result["rendered"]

    def test_format_p_small(self, tmp_path):
        """p < 0.001 should render as < 0.001, not 0.000."""
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 5.0, "df": 100, "p": 0.0005, "d": 1.0},
        )
        result = sc.format(project_dir=project_dir, claim_id="s1", style="nature")
        assert result["success"]
        assert "0.001" in result["rendered"]  # < 0.001

    def test_format_citation(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="c1",
            claim_type="citation",
            value={"text": "as shown previously"},
        )
        result = sc.format(project_dir=project_dir, claim_id="c1", style="nature")
        assert result["success"]
        assert "as shown previously" in result["rendered"]

    def test_format_value(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="v1",
            claim_type="value",
            value={"value": 42.3, "unit": "ms"},
        )
        result = sc.format(project_dir=project_dir, claim_id="v1", style="nature")
        assert result["success"]
        assert "42.3" in result["rendered"]
        assert "ms" in result["rendered"]


class TestClaimRender:
    """Test rendering all claims to claims_rendered.tex."""

    def test_render_creates_tex(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="grp",
            claim_type="statistic",
            value={"t": 4.23, "df": 34, "p": 0.00032, "d": 0.87},
        )
        result = sc.render(project_dir=project_dir)
        assert result["success"]
        tex_path = Path(project_dir) / "00_shared" / "claims_rendered.tex"
        assert tex_path.exists()

    def test_render_tex_has_macro(self, tmp_path):
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="my_stat",
            claim_type="statistic",
            value={"t": 2.0, "df": 10, "p": 0.03, "d": 0.5},
        )
        sc.render(project_dir=project_dir)
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "\\stxclaim" in tex
        assert "mystat" in tex  # sanitized ID (underscores removed)

    def test_render_all_styles(self, tmp_path):
        """Rendered .tex defines nature, apa, and plain macros for each claim."""
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        sc.add(
            project_dir=project_dir,
            claim_id="s1",
            claim_type="statistic",
            value={"t": 3.0, "df": 20, "p": 0.005, "d": 0.7},
        )
        sc.render(project_dir=project_dir)
        tex = (Path(project_dir) / "00_shared" / "claims_rendered.tex").read_text()
        assert "@nature" in tex
        assert "@apa" in tex
        assert "@plain" in tex

    def test_render_empty(self, tmp_path):
        """Rendering with no claims still creates a valid .tex file."""
        import scitex_writer.claim as sc

        project_dir = _make_project(tmp_path)
        result = sc.render(project_dir=project_dir)
        assert result["success"]
        assert result["claims_count"] == 0
        tex_path = Path(project_dir) / "00_shared" / "claims_rendered.tex"
        assert tex_path.exists()


class TestClaimPublicApi:
    """Test that scitex_writer.claim exposes the correct public interface."""

    def test_public_functions_exist(self):
        import scitex_writer.claim as sc

        for name in ["add", "list", "get", "remove", "format", "render"]:
            assert hasattr(sc, name), f"Missing: claim.{name}"
            assert callable(getattr(sc, name))

    def test_claim_not_in_top_level_all(self):
        """Internal dataclasses should not appear in scitex_writer.__all__."""
        import scitex_writer as sw

        for name in [
            "CompilationResult",
            "ManuscriptTree",
            "RevisionTree",
            "SupplementaryTree",
        ]:
            assert name not in sw.__all__, f"{name} should be hidden from __all__"

    def test_claim_in_top_level_all(self):
        """claim module should be in scitex_writer.__all__."""
        import scitex_writer as sw

        assert "claim" in sw.__all__
