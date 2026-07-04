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
from render_clew_toggles import (  # noqa: E402
    CONFIG_YAML,
    _resolve_config_yaml,
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


class TestResolveConfigYaml:
    def test_nested_writer_resolves_git_root_config(self, tmp_path):
        # Arrange: writer vendored under an outer git repo; config at the outer
        # git root's .scitex/writer/, NOT doubly-nested under the writer subdir.
        (tmp_path / ".git").mkdir()
        writer = tmp_path / ".scitex" / "writer"
        writer.mkdir(parents=True)
        (writer / "config.yaml").write_text("clew_presentation: on\n")
        # Act
        resolved = _resolve_config_yaml(writer)
        # Assert
        assert resolved == tmp_path / CONFIG_YAML

    def test_flat_project_resolves_its_own_config(self, tmp_path):
        # Arrange
        (tmp_path / ".git").mkdir()
        (tmp_path / ".scitex" / "writer").mkdir(parents=True)
        (tmp_path / CONFIG_YAML).write_text("clew_presentation: on\n")
        # Act
        resolved = _resolve_config_yaml(tmp_path)
        # Assert
        assert resolved == tmp_path / CONFIG_YAML

    def test_no_git_root_falls_back_to_project_path(self, tmp_path):
        # Arrange
        project = tmp_path / "proj"
        project.mkdir()
        # Act
        resolved = _resolve_config_yaml(project)
        # Assert
        assert resolved == project / CONFIG_YAML


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
