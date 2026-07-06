#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: _update/_handler.py — read-only perms on vendored engine files

from scitex_writer._mcp.handlers._update._handler import (
    _apply_updates,
    _set_engine_readonly,
)


def test_set_engine_readonly_clears_write_bit(tmp_path):
    # Arrange
    target = tmp_path / "scripts" / "python" / "csv_to_latex.py"
    target.parent.mkdir(parents=True)
    target.write_text("print('hi')\n")
    target.chmod(0o644)
    # Act
    _set_engine_readonly(tmp_path, ["scripts/python/csv_to_latex.py"])
    # Assert
    assert not (target.stat().st_mode & 0o222)


def test_set_engine_readonly_keeps_execute_bit(tmp_path):
    # Arrange
    target = tmp_path / "scripts" / "shell" / "compile_core.sh"
    target.parent.mkdir(parents=True)
    target.write_text("echo hi\n")
    target.chmod(0o755)
    # Act
    _set_engine_readonly(tmp_path, ["scripts/shell/compile_core.sh"])
    # Assert
    assert target.stat().st_mode & 0o111


def test_apply_updates_leaves_written_engine_file_read_only(tmp_path):
    # Arrange
    project = tmp_path / "project"
    project.mkdir()
    src = tmp_path / "template" / "Makefile"
    src.parent.mkdir(parents=True)
    src.write_text("all:\n")
    # Act
    _apply_updates(project, {"Makefile": src}, modified=[], added=["Makefile"])
    # Assert
    assert not ((project / "Makefile").stat().st_mode & 0o222)


def test_apply_updates_is_idempotent_over_read_only_target(tmp_path):
    # A second vendor must not fail on the now-read-only file it wrote before.
    # Arrange
    project = tmp_path / "project"
    project.mkdir()
    src = tmp_path / "template" / "Makefile"
    src.parent.mkdir(parents=True)
    src.write_text("all:\n")
    _apply_updates(project, {"Makefile": src}, modified=[], added=["Makefile"])
    src.write_text("all:\n\techo v2\n")
    # Act
    _apply_updates(project, {"Makefile": src}, modified=["Makefile"], added=[])
    # Assert
    assert (project / "Makefile").read_text() == "all:\n\techo v2\n"
