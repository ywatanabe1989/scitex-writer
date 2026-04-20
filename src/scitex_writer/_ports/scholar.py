"""scitex-scholar bridge (optional; no hard dependency).

Resolves bibliography citation keys / DOIs to enriched scholar library
records by reading the user's scholar library via a filesystem symlink
at ``<project_dir>/.scitex/writer/00_shared/scholar/library`` (or the
writer's in-tree ``00_shared/scholar/library``).

Resolution paths, in order:

1. ``<library_root>/index.db`` — when scitex-scholar PR-C has shipped,
   use a single SQLite SELECT. This is preferred whenever the DB exists.
2. Linear scan of ``<library_root>/MASTER/*/metadata.json``, cached
   in-process with an mtime key. Works today, no DB needed.
3. Return ``None`` — caller falls back to bare bib card.

Every function degrades on missing/dangling symlink, unreadable JSON,
or unknown schema fields.
"""

from __future__ import annotations

import json
import sqlite3
from functools import lru_cache
from pathlib import Path
from typing import Optional

try:  # Presence check only. Not used for functional imports.
    import scitex_scholar  # noqa: F401

    SCHOLAR_AVAILABLE = True
except ImportError:
    SCHOLAR_AVAILABLE = False


_INDEX_DB_NAME = "index.db"


def scholar_library_root(project_dir: Path) -> Optional[Path]:
    """Resolve the project's scholar-library symlink. Returns None on dangle."""
    p = Path(project_dir) / "00_shared" / "scholar" / "library"
    try:
        resolved = p.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if not resolved.is_dir():
        return None
    return resolved


def _index_db_path(root: Path) -> Optional[Path]:
    """Return the index.db path if present and readable."""
    p = root / _INDEX_DB_NAME
    return p if p.is_file() else None


def metadata_for_doi(root: Path, doi: str) -> Optional[dict]:
    """Look up a paper by DOI. Prefers index.db, falls back to MASTER scan."""
    db = _index_db_path(root)
    if db is not None:
        try:
            with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
                conn.row_factory = sqlite3.Row
                row = conn.execute(
                    "SELECT * FROM papers WHERE doi = ? COLLATE NOCASE", (doi,)
                ).fetchone()
                if row:
                    return _hydrate_full_metadata(root, dict(row)["paper_id"]) or dict(
                        row
                    )
        except sqlite3.Error:
            pass

    doi_lc = doi.lower()
    for md in _iter_all_metadata(root):
        entry_doi = (md.get("metadata", {}).get("id", {}) or {}).get("doi")
        if entry_doi and entry_doi.lower() == doi_lc:
            return md
    return None


def metadata_for_paper_id(root: Path, paper_id: str) -> Optional[dict]:
    return _hydrate_full_metadata(root, paper_id)


def iter_library_cards(root: Path) -> list[dict]:
    """Return a list of compact library records for a browse view.

    Prefers index.db (one query) over full-MASTER scan. Each record has
    ``paper_id``, ``doi``, ``title``, ``year``, ``venue`` at minimum;
    consumers should ``.get()`` anything beyond that.
    """
    db = _index_db_path(root)
    if db is not None:
        try:
            with sqlite3.connect(f"file:{db}?mode=ro", uri=True) as conn:
                conn.row_factory = sqlite3.Row
                rows = conn.execute(
                    "SELECT paper_id, doi, arxiv_id, pmid, title, year, venue, is_oa "
                    "FROM papers ORDER BY year DESC, title"
                ).fetchall()
                return [dict(r) for r in rows]
        except sqlite3.Error:
            pass

    out = []
    for md in _iter_all_metadata(root):
        m = md.get("metadata", {}) or {}
        id_ = m.get("id", {}) or {}
        basic = m.get("basic", {}) or {}
        pub = m.get("publication", {}) or {}
        out.append(
            {
                "paper_id": md.get("_paper_id"),
                "doi": id_.get("doi"),
                "arxiv_id": id_.get("arxiv_id"),
                "pmid": id_.get("pmid"),
                "title": basic.get("title"),
                "year": basic.get("year"),
                "venue": pub.get("short_journal") or pub.get("journal"),
            }
        )
    out.sort(key=lambda r: (-(r.get("year") or 0), (r.get("title") or "")))
    return out


def _hydrate_full_metadata(root: Path, paper_id: str) -> Optional[dict]:
    """Read MASTER/<paper_id>/metadata.json in full. None if missing."""
    f = root / "MASTER" / paper_id / "metadata.json"
    if not f.is_file():
        return None
    try:
        md = json.loads(f.read_text())
        md["_paper_id"] = paper_id
        return md
    except (OSError, json.JSONDecodeError):
        return None


def _iter_all_metadata(root: Path) -> tuple[dict, ...]:
    """Cached MASTER scan, invalidated when the MASTER dir mtime changes."""
    master = root / "MASTER"
    mtime = master.stat().st_mtime if master.is_dir() else 0.0
    return _cached_master_scan(str(root), mtime)


@lru_cache(maxsize=8)
def _cached_master_scan(root_str: str, mtime_key: float) -> tuple[dict, ...]:
    root = Path(root_str)
    master = root / "MASTER"
    if not master.is_dir():
        return ()
    entries = []
    for f in master.glob("*/metadata.json"):
        try:
            md = json.loads(f.read_text())
            md["_paper_id"] = f.parent.name
            entries.append(md)
        except (OSError, json.JSONDecodeError):
            continue
    return tuple(entries)
