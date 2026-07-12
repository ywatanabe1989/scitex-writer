#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scitex_writer/_mcp/handlers/test__diff_pipeline.py

r"""Tests for the pure-Python diff pipeline (port of process_diff.sh).

Real inputs throughout: a real git repository under ``tmp_path`` carrying two real
commits of a real compiled ``.tex``, the same config keys the shell read, real
``latexdiff`` and a real ``latexmk`` compile of the result. A diff PDF that does
not compile is not a diff PDF, so the end-to-end case really compiles one.

The "no previous version" case is the regression guard for the shell's worst
silent degradation: it diffed the file against ITSELF and shipped an unmarked PDF,
which a reviewer cannot tell apart from "nothing changed".
"""

import shutil
import subprocess

import pytest

from scitex_writer._mcp.handlers import _diff_pipeline

_CONFIG = (
    "paths:\n"
    '  doc_log_dir: "./01_manuscript/logs"\n'
    '  compiled_tex: "./01_manuscript/manuscript.tex"\n'
    '  compiled_pdf: "./01_manuscript/manuscript.pdf"\n'
    '  diff_tex: "./01_manuscript/manuscript_diff.tex"\n'
    '  diff_pdf: "./01_manuscript/manuscript_diff.pdf"\n'
    '  archive_dir: "./01_manuscript/archive"\n'
)

_V1 = "\\documentclass{article}\n\\begin{document}\nThe first draft.\n\\end{document}\n"
_V2 = (
    "\\documentclass{article}\n\\begin{document}\n"
    "The second, thoroughly revised draft.\n\\end{document}\n"
)

needs_tools = pytest.mark.skipif(
    shutil.which("latexdiff") is None or shutil.which("latexmk") is None,
    reason="latexdiff and latexmk are both required",
)


def _git_cmd(repo, *args):
    subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    )


def _commit(repo, message):
    _git_cmd(repo, "add", "-A")
    _git_cmd(repo, "commit", "-q", "-m", message)


def _seed_project(tmp_path, revisions=(_V1, _V2)):
    """A real git project whose compiled .tex has one commit per revision."""
    cfg = tmp_path / "config"
    cfg.mkdir()
    (cfg / "config_manuscript.yaml").write_text(_CONFIG, encoding="utf-8")
    (tmp_path / "01_manuscript").mkdir()
    _git_cmd(tmp_path, "init", "-q")
    _git_cmd(tmp_path, "config", "user.email", "tester@example.com")
    _git_cmd(tmp_path, "config", "user.name", "Tester")
    for index, text in enumerate(revisions):
        (tmp_path / "01_manuscript" / "manuscript.tex").write_text(
            text, encoding="utf-8"
        )
        _commit(tmp_path, f"revision {index}")
    return tmp_path


class TestPipelineErrors:
    def test_invalid_doc_type_returns_actionable_error(self):
        # Arrange
        bad_doc_type = "poster"
        # Act
        result = _diff_pipeline.process(".", bad_doc_type)
        # Assert
        assert result["success"] is False and "poster" in result["error"]

    def test_missing_project_dir_returns_error_hint(self, tmp_path):
        # Arrange
        absent = tmp_path / "nope"
        # Act
        result = _diff_pipeline.process(str(absent), "manuscript")
        # Assert
        assert result["success"] is False and "not found" in result["error"]

    def test_missing_config_returns_error_hint(self, tmp_path):
        # Arrange
        (tmp_path / "01_manuscript").mkdir()
        # Act
        result = _diff_pipeline.process(str(tmp_path), "manuscript")
        # Assert
        assert result["success"] is False and "Config not found" in result["error"]

    def test_missing_compiled_tex_returns_compile_hint(self, tmp_path):
        # Arrange
        cfg = tmp_path / "config"
        cfg.mkdir()
        (cfg / "config_manuscript.yaml").write_text(_CONFIG, encoding="utf-8")
        (tmp_path / "01_manuscript").mkdir()
        # Act
        result = _diff_pipeline.process(str(tmp_path), "manuscript")
        # Assert
        assert "Compiled TeX not found" in result["error"]

    def test_no_diff_flag_skips_pipeline(self, tmp_path):
        # Arrange
        project = _seed_project(tmp_path)
        # Act
        result = _diff_pipeline.process(str(project), "manuscript", no_diff=True)
        # Assert
        assert result["skipped"] is True

    def test_escaping_config_path_is_refused(self, tmp_path):
        # Arrange
        project = tmp_path / "proj"
        (project / "config").mkdir(parents=True)
        (project / "config" / "config_manuscript.yaml").write_text(
            _CONFIG.replace('diff_pdf: "./01', 'diff_pdf: "../01'), encoding="utf-8"
        )
        (project / "01_manuscript").mkdir()
        # Act
        result = _diff_pipeline.process(str(project), "manuscript")
        # Assert
        assert "OUTSIDE the project root" in result["error"]


class TestResolveVersions:
    def test_single_commit_refuses_to_diff_against_itself(self, tmp_path):
        # Arrange
        project = _seed_project(tmp_path, revisions=(_V1,))
        # Act
        result = _diff_pipeline.process(str(project), "manuscript")
        # Assert
        assert "No PREVIOUS version" in result["error"]

    def test_unknown_diff_from_commit_is_an_error(self, tmp_path):
        # Arrange
        project = _seed_project(tmp_path)
        # Act
        result = _diff_pipeline.process(
            str(project), "manuscript", diff_from="no-such-commit"
        )
        # Assert
        assert "does not resolve to a commit" in result["error"]

    def test_non_git_project_is_an_error(self, tmp_path):
        # Arrange
        cfg = tmp_path / "config"
        cfg.mkdir()
        (cfg / "config_manuscript.yaml").write_text(_CONFIG, encoding="utf-8")
        (tmp_path / "01_manuscript").mkdir()
        (tmp_path / "01_manuscript" / "manuscript.tex").write_text(
            _V1, encoding="utf-8"
        )
        # Act
        result = _diff_pipeline.process(str(tmp_path), "manuscript")
        # Assert
        assert "not a git repository" in result["error"]

    def test_dirty_tree_marks_the_new_version_with_plus(self, tmp_path):
        # Arrange -- an edit to a TRACKED file; git (and so the shell) does not
        # count an untracked file as a change against HEAD.
        project = _seed_project(tmp_path)
        compiled = project / "01_manuscript" / "manuscript.tex"
        compiled.write_text(_V2 + "% uncommitted\n", encoding="utf-8")
        # Act
        _, _, new_label = _diff_pipeline.resolve_versions(project, compiled, None)
        # Assert
        assert new_label.endswith("+")

    def test_clean_tree_marks_the_new_version_without_plus(self, tmp_path):
        # Arrange
        project = _seed_project(tmp_path)
        compiled = project / "01_manuscript" / "manuscript.tex"
        # Act
        _, _, new_label = _diff_pipeline.resolve_versions(project, compiled, None)
        # Assert
        assert not new_label.endswith("+")


@needs_tools
class TestEndToEnd:
    @pytest.fixture
    def rendered(self, tmp_path):
        project = _seed_project(tmp_path)
        return project, _diff_pipeline.process(str(project), "manuscript")

    def test_two_committed_revisions_render_successfully(self, rendered):
        # Arrange
        _, result = rendered
        # Act
        success = result["success"]
        # Assert
        assert success is True, result.get("error")

    def test_diff_pdf_really_exists_on_disk(self, rendered):
        # Arrange
        project, result = rendered
        # Act
        pdf = project / "01_manuscript" / "manuscript_diff.pdf"
        # Assert
        assert pdf.is_file()

    def test_diff_pdf_is_non_empty(self, rendered):
        # Arrange
        _, result = rendered
        # Act
        size = result["pdf_bytes"]
        # Assert
        assert size > 0

    def test_diff_tex_carries_latexdiff_markup(self, rendered):
        # Arrange
        project, _ = rendered
        text = (project / "01_manuscript" / "manuscript_diff.tex").read_text(
            encoding="utf-8"
        )
        # Act
        marked = "\\DIFadd" in text and "\\DIFdel" in text
        # Assert
        assert marked is True

    def test_diff_tex_carries_the_signature_block(self, rendered):
        # Arrange
        project, _ = rendered
        text = (project / "01_manuscript" / "manuscript_diff.tex").read_text(
            encoding="utf-8"
        )
        # Act
        signed = "Diff Document Metadata" in text
        # Assert
        assert signed is True

    def test_result_names_both_compared_versions(self, rendered):
        # Arrange
        _, result = rendered
        # Act
        named = bool(result["from_hash"]) and bool(result["to_hash"])
        # Assert
        assert named is True

    def test_explicit_diff_from_head_is_accepted(self, tmp_path):
        # Arrange
        project = _seed_project(tmp_path)
        # Act
        result = _diff_pipeline.process(str(project), "manuscript", diff_from="HEAD~1")
        # Assert
        assert result["success"] is True, result.get("error")
