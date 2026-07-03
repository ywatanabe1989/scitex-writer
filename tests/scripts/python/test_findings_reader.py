#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_writer._mcp.handlers._findings.get_findings (feed reader)."""

import json

from scitex_writer._mcp.handlers._findings import get_findings


class TestGetFindings:
    def test_absent_sidecar_returns_empty_feed(self, tmp_path):
        # Arrange
        project = tmp_path
        # Act
        feed = get_findings(str(project))
        # Assert
        assert feed["summary"]["total"] == 0

    def test_reads_present_sidecar_feed(self, tmp_path):
        # Arrange
        writer_dir = tmp_path / ".scitex" / "writer"
        writer_dir.mkdir(parents=True)
        (writer_dir / "findings.json").write_text(json.dumps({
            "schema": "manuscript-findings/1",
            "summary": {"total": 1},
            "findings": [{"id": "x", "kind": "claim", "severity": "warning"}],
        }))
        # Act
        feed = get_findings(str(tmp_path))
        # Assert
        assert feed["findings"][0]["id"] == "x"

    def test_malformed_sidecar_returns_empty_feed(self, tmp_path):
        # Arrange
        writer_dir = tmp_path / ".scitex" / "writer"
        writer_dir.mkdir(parents=True)
        (writer_dir / "findings.json").write_text("{ not valid json")
        # Act
        feed = get_findings(str(tmp_path))
        # Assert
        assert feed["findings"] == []

    def test_returned_empty_feed_is_an_independent_copy(self, tmp_path):
        # Arrange
        first = get_findings(str(tmp_path))
        first["findings"].append("mutated")
        # Act
        second = get_findings(str(tmp_path))
        # Assert
        assert second["findings"] == []


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
