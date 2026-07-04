#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: render_clew.py git-root .scitex/clew resolution (nested-writer).

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from render_clew import (  # noqa: E402
    CLAIMS_JSON,
    _resolve_claims_json,
)


class TestResolveClaimsJson:
    def test_nested_writer_resolves_git_root_feed(self, tmp_path):
        # Arrange: writer vendored under an outer git repo whose .scitex/clew is
        # the real feed; a STRAY empty .scitex/clew sits under the writer subdir.
        (tmp_path / ".git").mkdir()
        (tmp_path / ".scitex" / "clew" / "runtime").mkdir(parents=True)
        writer = tmp_path / ".scitex" / "writer"
        (writer / ".scitex" / "clew" / "runtime").mkdir(parents=True)
        # Act
        resolved = _resolve_claims_json(writer)
        # Assert
        assert resolved == tmp_path / ".scitex" / "clew" / "runtime" / "claims.json"

    def test_flat_project_resolves_its_own_clew(self, tmp_path):
        # Arrange: project IS its own git root with .scitex/clew (common case).
        (tmp_path / ".git").mkdir()
        (tmp_path / ".scitex" / "clew" / "runtime").mkdir(parents=True)
        # Act
        resolved = _resolve_claims_json(tmp_path)
        # Assert
        assert resolved == tmp_path / ".scitex" / "clew" / "runtime" / "claims.json"

    def test_no_git_root_falls_back_to_project_path(self, tmp_path):
        # Arrange: no .git anywhere above the project.
        project = tmp_path / "proj"
        project.mkdir()
        # Act
        resolved = _resolve_claims_json(project)
        # Assert
        assert resolved == project / CLAIMS_JSON

    def test_git_root_without_clew_falls_back_to_project_path(self, tmp_path):
        # Arrange: a git root exists but never ran clew (no .scitex/clew there).
        (tmp_path / ".git").mkdir()
        project = tmp_path / "sub"
        project.mkdir()
        # Act
        resolved = _resolve_claims_json(project)
        # Assert
        assert resolved == project / CLAIMS_JSON


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
