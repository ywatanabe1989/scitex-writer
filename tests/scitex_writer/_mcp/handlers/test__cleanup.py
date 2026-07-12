#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_mcp/handlers/test__cleanup.py

"""Tests for the cleanup handler (pure-Python cleanup engine)."""

from scitex_writer._mcp.handlers import _cleanup

_CONFIG = (
    "paths:\n"
    '  doc_root_dir: "./01_manuscript"\n'
    '  doc_log_dir: "./01_manuscript/logs"\n'
)


def _seed_project(tmp_path):
    """Seed a minimal manuscript project tree and return (project, doc_root)."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "config_manuscript.yaml").write_text(_CONFIG, encoding="utf-8")
    doc_root = tmp_path / "01_manuscript"
    (doc_root / "sub").mkdir(parents=True)
    return tmp_path, doc_root


class TestCleanupErrors:
    def test_invalid_doc_type_returns_actionable_error(self):
        # Arrange
        bad_doc_type = "poster"
        # Act
        result = _cleanup.clean(".", bad_doc_type)
        # Assert
        assert result["success"] is False and "poster" in result["error"]

    def test_missing_project_dir_returns_error_with_hint(self, tmp_path):
        # Arrange
        absent = tmp_path / "nope"
        # Act
        result = _cleanup.clean(str(absent), "manuscript")
        # Assert
        assert result["success"] is False and "not found" in result["error"]

    def test_missing_config_returns_error_with_hint(self, tmp_path):
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        # Act
        result = _cleanup.clean(str(tmp_path), "manuscript")
        # Assert
        assert result["success"] is False and "Config not found" in result["error"]


class TestCleanupSweeps:
    def test_removes_bak_files_recursively(self, tmp_path):
        # Arrange
        project, doc_root = _seed_project(tmp_path)
        target = doc_root / "sub" / "old.bak"
        target.write_text("x")
        # Act
        result = _cleanup.clean(str(project), "manuscript")
        # Assert
        assert result["bak_removed"] == 1 and not target.exists()

    def test_removes_emacs_temp_files_recursively(self, tmp_path):
        # Arrange
        project, doc_root = _seed_project(tmp_path)
        target = doc_root / "sub" / "#draft.tex#"
        target.write_text("x")
        # Act
        result = _cleanup.clean(str(project), "manuscript")
        # Assert
        assert result["emacs_removed"] == 1 and not target.exists()

    def test_moves_toplevel_aux_files_to_log_dir(self, tmp_path):
        # Arrange
        project, doc_root = _seed_project(tmp_path)
        (doc_root / "manuscript.aux").write_text("x")
        # Act
        result = _cleanup.clean(str(project), "manuscript")
        # Assert
        assert (doc_root / "logs" / "manuscript.aux").exists() and result["aux_moved"] == 1

    def test_removes_progress_log_files_recursively(self, tmp_path):
        # Arrange
        project, doc_root = _seed_project(tmp_path)
        target = doc_root / "sub" / "progress.log"
        target.write_text("x")
        # Act
        result = _cleanup.clean(str(project), "manuscript")
        # Assert
        assert result["progress_removed"] == 1 and not target.exists()

    def test_removes_versioned_files_in_project_root(self, tmp_path):
        # Arrange
        project, _ = _seed_project(tmp_path)
        pdf = project / "manuscript_v1.pdf"
        pdf.write_text("x")
        (project / "draft_v2.tex").write_text("x")
        # Act
        result = _cleanup.clean(str(project), "manuscript")
        # Assert
        assert result["versioned_removed"] == 2 and not pdf.exists()


class TestCleanupDryRun:
    def test_dry_run_previews_without_deleting(self, tmp_path):
        # Arrange
        project, doc_root = _seed_project(tmp_path)
        target = doc_root / "sub" / "old.bak"
        target.write_text("x")
        # Act
        result = _cleanup.clean(str(project), "manuscript", dry_run=True)
        # Assert
        assert result["bak_removed"] == 1 and target.exists()


class TestCleanupRootGuard:
    def test_refuses_when_doc_root_escapes_project_root(self, tmp_path):
        # Arrange
        project = tmp_path / "proj"
        project.mkdir()
        cfg = project / "config"
        cfg.mkdir()
        (cfg / "config_manuscript.yaml").write_text(
            'paths:\n  doc_root_dir: "../outside"\n  doc_log_dir: "./01_manuscript/logs"\n',
            encoding="utf-8",
        )
        outside_bak = tmp_path / "outside" / "keep.bak"
        outside_bak.parent.mkdir()
        outside_bak.write_text("x")
        # Act
        result = _cleanup.clean(str(project), "manuscript")
        # Assert
        assert result["success"] is False and outside_bak.exists()


if __name__ == "__main__":
    import sys

    import pytest

    sys.exit(pytest.main([__file__, "-v"]))

# EOF
