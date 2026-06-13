#!/usr/bin/env python3
"""Tests for the scholar bridge."""

from __future__ import annotations

import json
from pathlib import Path

from scitex_writer._ports import scholar


def _write_metadata(root: Path, paper_id: str, **ids) -> None:
    entry = root / "MASTER" / paper_id
    entry.mkdir(parents=True)
    md = {
        "metadata": {
            "id": {
                "doi": ids.get("doi"),
                "arxiv_id": ids.get("arxiv_id"),
                "pmid": ids.get("pmid"),
            },
            "basic": {
                "title": ids.get("title", "t"),
                "year": ids.get("year", 2024),
                "authors": ids.get("authors", ["A. Author"]),
            },
            "publication": {"journal": "J"},
        }
    }
    (entry / "metadata.json").write_text(json.dumps(md))


def test_library_root_returns_none_when_no_symlink_present(tmp_path: Path):
    """Verify scholar_library_root returns None when there's no symlink at all."""
    # Arrange
    # tmp_path has no symlink
    # Act
    result = scholar.scholar_library_root(tmp_path)
    # Assert
    assert result is None


def test_library_root_resolves_valid_symlink_target(tmp_path: Path):
    """Verify scholar_library_root resolves a valid library symlink."""
    # Arrange
    home_lib = tmp_path / "home"
    home_lib.mkdir()
    (home_lib / "MASTER").mkdir()
    link_parent = tmp_path / "proj" / "00_shared" / "scholar"
    link_parent.mkdir(parents=True)
    (link_parent / "library").symlink_to(home_lib)
    # Act
    resolved = scholar.scholar_library_root(tmp_path / "proj")
    # Assert
    assert resolved == home_lib.resolve()


def test_library_root_returns_none_for_dangling_symlink(tmp_path: Path):
    """Verify a dangling library symlink yields None."""
    # Arrange
    link_parent = tmp_path / "proj" / "00_shared" / "scholar"
    link_parent.mkdir(parents=True)
    (link_parent / "library").symlink_to(tmp_path / "does-not-exist")
    # Act
    result = scholar.scholar_library_root(tmp_path / "proj")
    # Assert
    assert result is None


def test_metadata_for_doi_returns_match_via_master_scan(tmp_path: Path):
    """Verify metadata_for_doi locates an entry via MASTER scan (non-None)."""
    # Arrange
    _write_metadata(tmp_path, "AAA", doi="10.1/aaa")
    _write_metadata(tmp_path, "BBB", doi="10.2/bbb")
    # Act
    md = scholar.metadata_for_doi(tmp_path, "10.1/AAA")
    # Assert
    assert md is not None


def test_metadata_for_doi_paper_id_matches_master_scan(tmp_path: Path):
    """Verify metadata_for_doi returns the correct paper id (case-insensitive)."""
    # Arrange
    _write_metadata(tmp_path, "AAA", doi="10.1/aaa")
    _write_metadata(tmp_path, "BBB", doi="10.2/bbb")
    # Act
    md = scholar.metadata_for_doi(tmp_path, "10.1/AAA")
    # Assert
    assert md["_paper_id"] == "AAA"


def test_metadata_for_doi_returns_none_when_missing(tmp_path: Path):
    """Verify metadata_for_doi returns None when DOI is not present."""
    # Arrange
    _write_metadata(tmp_path, "AAA", doi="10.1/aaa")
    # Act
    result = scholar.metadata_for_doi(tmp_path, "10.99/nope")
    # Assert
    assert result is None


def test_iter_library_cards_returned_order_sorted_by_year_desc(tmp_path: Path):
    """Verify iter_library_cards yields cards sorted by year descending."""
    # Arrange
    _write_metadata(tmp_path, "OLD", doi="10.1/o", year=2010, title="old")
    _write_metadata(tmp_path, "NEW", doi="10.1/n", year=2025, title="new")
    # Act
    cards = scholar.iter_library_cards(tmp_path)
    # Assert
    assert [c["paper_id"] for c in cards] == ["NEW", "OLD"]


def test_prefers_index_db_when_present_for_iter_library_cards(tmp_path: Path):
    """If index.db exists, iter_library_cards reads it directly."""
    # Arrange
    import sqlite3

    _write_metadata(tmp_path, "AAA", doi="10.1/a", year=2024, title="alpha")
    conn = sqlite3.connect(tmp_path / "index.db")
    conn.executescript(
        "CREATE TABLE papers (paper_id TEXT PRIMARY KEY, doi TEXT, "
        "arxiv_id TEXT, pmid TEXT, title TEXT, year INTEGER, venue TEXT, "
        "is_oa INTEGER, updated_at REAL);"
    )
    conn.execute(
        "INSERT INTO papers(paper_id, doi, title, year, venue) VALUES "
        "('ZZZ','10.9/z','from_db',2099,'DB')"
    )
    conn.commit()
    conn.close()
    # Act
    cards = scholar.iter_library_cards(tmp_path)
    # Assert
    assert any(c["paper_id"] == "ZZZ" for c in cards)


def test_scholar_available_flag_is_bool_type():
    """Verify the SCHOLAR_AVAILABLE module flag is a bool."""
    # Arrange
    # constant defined at module level
    # Act
    flag = scholar.SCHOLAR_AVAILABLE
    # Assert
    assert isinstance(flag, bool)
