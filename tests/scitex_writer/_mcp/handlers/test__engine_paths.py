#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_mcp/handlers/test__engine_paths.py

"""Tests for the shared config loading + boundary-checked path resolution.

Real YAML files under ``tmp_path``. The boundary check is the load-bearing part:
a ``..`` in the config must never let a pipeline write outside the project.
"""

from scitex_writer._mcp.handlers import _engine_paths

_KEYS = {"compiled_tex": ("paths", "compiled_tex")}


def _write_config(tmp_path, body):
    cfg = tmp_path / "config"
    cfg.mkdir(exist_ok=True)
    (cfg / "config_manuscript.yaml").write_text(body, encoding="utf-8")
    return tmp_path


class TestLoadDocConfig:
    def test_valid_config_is_parsed_into_a_dict(self, tmp_path):
        # Arrange
        project = _write_config(tmp_path, 'paths:\n  compiled_tex: "./a/b.tex"\n')
        # Act
        cfg, error = _engine_paths.load_doc_config(project, "manuscript")
        # Assert
        assert cfg["paths"]["compiled_tex"] == "./a/b.tex"

    def test_absent_config_returns_actionable_error(self, tmp_path):
        # Arrange
        project = tmp_path
        # Act
        _, error = _engine_paths.load_doc_config(project, "manuscript")
        # Assert
        assert "Config not found" in error

    def test_malformed_yaml_returns_actionable_error(self, tmp_path):
        # Arrange
        project = _write_config(tmp_path, "paths: [unclosed\n")
        # Act
        _, error = _engine_paths.load_doc_config(project, "manuscript")
        # Assert
        assert "not valid YAML" in error


class TestResolvePaths:
    def test_relative_path_resolves_under_the_project(self, tmp_path):
        # Arrange
        cfg = {"paths": {"compiled_tex": "./01_manuscript/m.tex"}}
        # Act
        paths, _ = _engine_paths.resolve_paths(tmp_path, cfg, _KEYS, "paths")
        # Assert
        assert paths["compiled_tex"] == tmp_path.resolve() / "01_manuscript/m.tex"

    def test_missing_key_returns_actionable_error(self, tmp_path):
        # Arrange
        cfg = {"paths": {}}
        # Act
        _, error = _engine_paths.resolve_paths(tmp_path, cfg, _KEYS, "paths")
        # Assert
        assert "paths.compiled_tex is missing" in error

    def test_escaping_path_is_refused(self, tmp_path):
        # Arrange
        cfg = {"paths": {"compiled_tex": "../outside/m.tex"}}
        # Act
        _, error = _engine_paths.resolve_paths(tmp_path, cfg, _KEYS, "paths")
        # Assert
        assert "OUTSIDE the project root" in error


class TestCfgGet:
    def test_nested_key_is_read_back(self):
        # Arrange
        cfg = {"a": {"b": "c"}}
        # Act
        value = _engine_paths.cfg_get(cfg, ("a", "b"))
        # Assert
        assert value == "c"

    def test_absent_level_falls_back_to_default(self):
        # Arrange
        cfg = {"a": {}}
        # Act
        value = _engine_paths.cfg_get(cfg, ("a", "b"), default="fallback")
        # Assert
        assert value == "fallback"
