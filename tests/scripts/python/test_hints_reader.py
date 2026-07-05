#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scitex_writer._mcp.handlers._hints.get_hints (feed reader)."""

import json

from scitex_writer._mcp.handlers._hints import get_hints


class TestGetHints:
    def test_absent_sidecar_returns_empty_feed(self, tmp_path):
        # Arrange
        project = tmp_path
        # Act
        feed = get_hints(str(project))
        # Assert
        assert feed["summary"]["total"] == 0

    def test_reads_present_sidecar_feed(self, tmp_path):
        # Arrange
        writer_dir = tmp_path / ".scitex" / "writer"
        writer_dir.mkdir(parents=True)
        (writer_dir / "hints.json").write_text(json.dumps({
            "schema": "manuscript-hints/1",
            "summary": {"total": 1},
            "hints": [{"id": "x", "kind": "claim", "severity": "warning"}],
        }))
        # Act
        feed = get_hints(str(tmp_path))
        # Assert
        assert feed["hints"][0]["id"] == "x"

    def test_malformed_sidecar_returns_empty_feed(self, tmp_path):
        # Arrange
        writer_dir = tmp_path / ".scitex" / "writer"
        writer_dir.mkdir(parents=True)
        (writer_dir / "hints.json").write_text("{ not valid json")
        # Act
        feed = get_hints(str(tmp_path))
        # Assert
        assert feed["hints"] == []

    def test_returned_empty_feed_is_an_independent_copy(self, tmp_path):
        # Arrange
        first = get_hints(str(tmp_path))
        first["hints"].append("mutated")
        # Act
        second = get_hints(str(tmp_path))
        # Assert
        assert second["hints"] == []


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
