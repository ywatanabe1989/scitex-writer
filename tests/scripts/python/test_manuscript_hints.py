#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: manuscript_hints.py (the dynamic-paper hints feed)

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from manuscript_hints import (  # noqa: E402
    build_feed,
    collect_hints,
    hints_from_claims,
    hints_from_log,
    summarize,
    write_feed,
)


class TestHintsFromLog:
    def test_undefined_reference_becomes_reference_hint(self):
        # Arrange
        log = "LaTeX Warning: Reference `fig:1' on page 2 undefined on input line 9."
        # Act
        found = hints_from_log(log)
        # Assert
        assert found[0]["kind"] == "reference" and found[0]["severity"] == "warning"

    def test_undefined_citation_carries_key_as_claim_id(self):
        # Arrange
        log = "LaTeX Warning: Citation `Smith2020' on page 1 undefined on input line 3."
        # Act
        found = hints_from_log(log)
        # Assert
        assert found[0]["kind"] == "citation" and found[0]["claim_id"] == "Smith2020"

    def test_repeated_undefined_key_is_deduplicated(self):
        # Arrange
        log = ("Reference `fig:1' on page 1 undefined.\n"
               "Reference `fig:1' on page 2 undefined.\n")
        # Act
        found = hints_from_log(log)
        # Assert
        assert len(found) == 1

    def test_clean_log_yields_no_hints(self):
        # Arrange
        log = "This is a normal compile log with nothing undefined.\n"
        # Act
        found = hints_from_log(log)
        # Assert
        assert found == []


class TestHintsFromClaims:
    def test_verified_claim_stays_silent(self):
        # Arrange
        data = {"claims": [{"claim_id": "a", "status": "verified"}]}
        # Act
        found = hints_from_claims(data)
        # Assert
        assert found == []

    def test_unverified_claim_becomes_warning(self):
        # Arrange
        data = {"claims": [{"claim_id": "a", "status": "unverified", "claim_value": "p=0.003"}]}
        # Act
        found = hints_from_claims(data)
        # Assert
        assert found[0]["severity"] == "warning"

    def test_registered_without_verified_at_reads_unverified(self):
        # Arrange
        data = {"claims": [{"claim_id": "a", "status": "registered", "verified_at": None}]}
        # Act
        found = hints_from_claims(data)
        # Assert
        assert found[0]["severity"] == "warning"

    def test_suspect_claim_becomes_advice(self):
        # Arrange
        data = {"claims": [{"claim_id": "a", "status": "suspect"}]}
        # Act
        found = hints_from_claims(data)
        # Assert
        assert found[0]["severity"] == "advice"

    def test_unsourced_claim_folds_to_advice(self):
        # Arrange
        data = {"claims": [{"claim_id": "a", "status": "unsourced"}]}
        # Act
        found = hints_from_claims(data)
        # Assert
        assert found[0]["severity"] == "advice"

    def test_hint_carries_claim_id_and_location(self):
        # Arrange
        data = {"claims": [{"claim_id": "x", "status": "unverified",
                            "file_path": "results.tex", "line_number": 42}]}
        # Act
        found = hints_from_claims(data)
        # Assert
        assert found[0]["claim_id"] == "x" and found[0]["location"]["line"] == 42

    def test_value_claim_maps_to_stat_kind(self):
        # Arrange
        data = {"claims": [{"claim_id": "a", "status": "unverified", "claim_type": "value"}]}
        # Act
        found = hints_from_claims(data)
        # Assert
        assert found[0]["kind"] == "stat"

    def test_claims_as_dict_keyed_by_id_supported(self):
        # Arrange
        data = {"claims": {"myclaim": {"status": "unverified"}}}
        # Act
        found = hints_from_claims(data)
        # Assert
        assert found[0]["claim_id"] == "myclaim"


class TestBuildFeed:
    _HINTS = [
        {"id": "a", "kind": "claim", "severity": "advice", "message": "m",
         "location": {}, "claim_id": None, "source": "scitex-clew"},
        {"id": "b", "kind": "reference", "severity": "warning", "message": "m",
         "location": {}, "claim_id": None, "source": "latex-log"},
    ]

    def test_feed_declares_schema_version(self):
        # Arrange
        hints = list(self._HINTS)
        # Act
        feed = build_feed(hints)
        # Assert
        assert feed["schema"] == "manuscript-hints/1"

    def test_hints_sorted_most_severe_first(self):
        # Arrange
        hints = list(self._HINTS)
        # Act
        feed = build_feed(hints)
        # Assert
        assert feed["hints"][0]["severity"] == "warning"

    def test_summary_counts_by_severity(self):
        # Arrange
        hints = list(self._HINTS)
        # Act
        summary = summarize(hints)
        # Assert
        assert summary["by_severity"] == {"advice": 1, "warning": 1}


class TestCollectAndWrite:
    def test_collect_reads_log_and_claims_from_project(self, tmp_path):
        # Arrange
        (tmp_path / "logs").mkdir()
        (tmp_path / "logs" / "manuscript.log").write_text("Citation `Ref1' undefined.\n")
        (tmp_path / ".scitex" / "clew" / "runtime").mkdir(parents=True)
        (tmp_path / ".scitex" / "clew" / "runtime" / "claims.json").write_text(
            json.dumps({"claims": [{"claim_id": "a", "status": "unverified"}]}))
        # Act
        found = collect_hints(str(tmp_path))
        # Assert
        assert len(found) == 2

    def test_write_feed_creates_json_file(self, tmp_path):
        # Arrange
        feed = build_feed([])
        # Act
        out = write_feed(str(tmp_path), feed)
        # Assert
        assert json.loads(Path(out).read_text())["schema"] == "manuscript-hints/1"

    def test_absent_artifacts_yield_empty_feed_not_error(self, tmp_path):
        # Arrange
        empty_project = tmp_path
        # Act
        found = collect_hints(str(empty_project))
        # Assert
        assert found == []


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
