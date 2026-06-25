#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: _update/_diff.py — active-style drift detection + noise filter

from scitex_writer._mcp.handlers._update._diff import (
    collect_sync_files,
    should_skip,
)


def test_should_skip_excludes_vendored_node_modules():
    # Arrange
    rel = "src/scitex_writer/_django/frontend/node_modules/rollup/x.js"
    # Act
    result = should_skip(rel)
    # Assert
    assert result is True


def test_should_skip_keeps_normal_engine_paths():
    # Arrange
    rel = "scripts/shell/compile_core.sh"
    # Act
    result = should_skip(rel)
    # Assert
    assert result is False


def _fake_template(tmp_path):
    t = tmp_path / "template"
    (t / "00_shared" / "latex_styles").mkdir(parents=True)
    (t / "00_shared" / "latex_styles" / "formatting.tex").write_text("template")
    (t / "scripts" / "shell").mkdir(parents=True)
    (t / "scripts" / "shell" / "compile_core.sh").write_text("echo hi")
    nm = t / "src" / "scitex_writer" / "_django" / "frontend" / "node_modules"
    nm.mkdir(parents=True)
    (nm / "junk.js").write_text("junk")
    (t / "src" / "scitex_writer" / "checks.py").write_text("source")
    return t


def test_collect_excludes_package_src(tmp_path):
    # The pip-installed package must never be vendored into a consumer project.
    # Arrange
    template = _fake_template(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    # Act
    files = collect_sync_files(template, project)
    # Assert
    assert not any(key.startswith("src/scitex_writer") for key in files)


def test_collect_includes_engine_scripts(tmp_path):
    # Arrange
    template = _fake_template(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    # Act
    files = collect_sync_files(template, project)
    # Assert
    assert "scripts/shell/compile_core.sh" in files


def test_collect_keys_styles_by_active_compiled_path(tmp_path):
    # Arrange
    template = _fake_template(tmp_path)
    project = tmp_path / "project"
    (project / "01_manuscript" / "contents" / "latex_styles").mkdir(parents=True)
    # Act
    files = collect_sync_files(template, project)
    # Assert
    assert "01_manuscript/contents/latex_styles/formatting.tex" in files


def test_collect_excludes_node_modules_from_drift(tmp_path):
    # Arrange
    template = _fake_template(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    # Act
    files = collect_sync_files(template, project)
    # Assert
    assert not any("node_modules" in key for key in files)


def test_collect_skips_styles_for_doc_type_without_latex_styles(tmp_path):
    # Arrange
    template = _fake_template(tmp_path)
    project = tmp_path / "project"
    project.mkdir()
    # Act
    files = collect_sync_files(template, project)
    # Assert
    assert not any("contents/latex_styles" in key for key in files)
