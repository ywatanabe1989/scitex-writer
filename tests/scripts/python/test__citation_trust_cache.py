#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: scripts/python/_citation_trust_cache.py
#
# The verdict cache for the citation-trustworthiness check. Real files under
# tmp_path only -- no mocks, no monkeypatch.

import json
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from _citation_trust_cache import (  # noqa: E402
    CACHE_SCHEMA,
    CACHE_TTL_DAYS,
    cache_lookup,
    cache_path,
    cache_store,
    entry_fingerprint,
    load_cache,
    save_cache,
)

KNOWN = {"verified", "unverified", "stub", "unlinked", "hallucinated"}


def _verdict(key="Smith2020", status="verified"):
    return {"key": key, "status": status, "detail": "crossref", "confidence": 0.99}


def test_cache_path_lives_under_project_runtime_dir():
    # Arrange
    project = Path("/tmp/proj")
    # Act
    path = cache_path(project)
    # Assert
    assert path == project / ".scitex/writer/runtime/citation_trust.json"


def test_entry_fingerprint_changes_when_a_field_is_edited():
    # Arrange
    before = entry_fingerprint({"title": "A study", "doi": "10.1/x"})
    # Act
    after = entry_fingerprint({"title": "A different study", "doi": "10.1/x"})
    # Assert
    assert before != after


def test_entry_fingerprint_is_stable_across_field_order():
    # Arrange
    first = entry_fingerprint({"title": "A study", "doi": "10.1/x"})
    # Act
    second = entry_fingerprint({"doi": "10.1/x", "title": "A study"})
    # Assert
    assert first == second


def test_saved_verdict_is_returned_on_cache_hit(tmp_path):
    # Arrange
    path = cache_path(tmp_path)
    save_cache(path, cache_store({}, [_verdict()], {"Smith2020": "fp"}, KNOWN))
    # Act
    hit = cache_lookup(load_cache(path), "Smith2020", "fp", KNOWN)
    # Assert
    assert hit["status"] == "verified"


def test_cache_hit_is_flagged_as_cached(tmp_path):
    # Arrange
    cached = cache_store({}, [_verdict()], {"Smith2020": "fp"}, KNOWN)
    # Act
    hit = cache_lookup(cached, "Smith2020", "fp", KNOWN)
    # Assert
    assert hit["cached"] is True


def test_changed_fingerprint_is_a_cache_miss():
    # Arrange
    cached = cache_store({}, [_verdict()], {"Smith2020": "old-fp"}, KNOWN)
    # Act
    hit = cache_lookup(cached, "Smith2020", "new-fp", KNOWN)
    # Assert
    assert hit is None


def test_unknown_cite_key_is_a_cache_miss():
    # Arrange
    cached = cache_store({}, [_verdict()], {"Smith2020": "fp"}, KNOWN)
    # Act
    hit = cache_lookup(cached, "NeverSeen2021", "fp", KNOWN)
    # Assert
    assert hit is None


def test_expired_verdict_is_a_cache_miss():
    # Arrange
    stale = time.time() - (CACHE_TTL_DAYS + 1) * 86400
    cached = cache_store({}, [_verdict()], {"Smith2020": "fp"}, KNOWN, now=stale)
    # Act
    hit = cache_lookup(cached, "Smith2020", "fp", KNOWN)
    # Assert
    assert hit is None


def test_unknown_status_is_never_stored_in_cache():
    # Arrange
    verdicts = [_verdict(status="totally-new-status")]
    # Act
    cached = cache_store({}, verdicts, {"Smith2020": "fp"}, KNOWN)
    # Assert
    assert cached == {}


def test_unknown_status_in_cache_file_is_a_miss():
    # Arrange
    cached = {
        "Smith2020": {
            "fingerprint": "fp",
            "status": "totally-new-status",
            "verified_at": time.time(),
        }
    }
    # Act
    hit = cache_lookup(cached, "Smith2020", "fp", KNOWN)
    # Assert
    assert hit is None


def test_corrupt_cache_file_reads_as_empty(tmp_path):
    # Arrange
    path = tmp_path / "citation_trust.json"
    path.write_text("{not json", encoding="utf-8")
    # Act
    cached = load_cache(path)
    # Assert
    assert cached == {}


def test_foreign_schema_cache_file_reads_as_empty(tmp_path):
    # Arrange
    path = tmp_path / "citation_trust.json"
    path.write_text(json.dumps({"schema": "other/v9", "verdicts": {"a": {}}}), "utf-8")
    # Act
    cached = load_cache(path)
    # Assert
    assert cached == {}


def test_missing_cache_file_reads_as_empty(tmp_path):
    # Arrange
    path = cache_path(tmp_path)
    # Act
    cached = load_cache(path)
    # Assert
    assert cached == {}


def test_saved_cache_file_carries_the_schema_marker(tmp_path):
    # Arrange
    path = cache_path(tmp_path)
    # Act
    save_cache(path, cache_store({}, [_verdict()], {"Smith2020": "fp"}, KNOWN))
    # Assert
    assert json.loads(path.read_text(encoding="utf-8"))["schema"] == CACHE_SCHEMA


# EOF
