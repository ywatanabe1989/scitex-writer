#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scripts/shell/modules/test_run_python_pipeline.py

"""Tests for scripts/shell/modules/run_python_pipeline.sh.

The launcher every compile_*.sh uses to reach the INSTALLED scitex-writer
Python engine for the four heavy stages (figures / tables / diff / archive).

Real subprocesses against a real fixture project on disk -- the point of the
module is precisely that a REAL shell invocation reaches the REAL Python
pipeline, which a stubbed call could never prove.
"""

import os
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[4]
LAUNCHER = REPO_ROOT / "scripts" / "shell" / "modules" / "run_python_pipeline.sh"

# A cell the old shell table module mangled: a percent sign plus inline math.
MATH_CELL = "5% ($p<0.05$)"


def _make_project(root: Path) -> Path:
    """Build the minimum project the table pipeline needs: config + one CSV."""
    project = root / "paper"
    tables = project / "01_manuscript" / "contents" / "tables" / "caption_and_media"
    tables.mkdir(parents=True)
    (tables / "01_demo.csv").write_text(
        f"Group,Change\nTreated,{MATH_CELL}\n", encoding="utf-8"
    )
    (project / "config").mkdir()
    (project / "config" / "config_manuscript.yaml").write_text(
        "tables:\n"
        "  dir: ./01_manuscript/contents/tables\n"
        "  caption_media_dir: ./01_manuscript/contents/tables/caption_and_media\n"
        "  compiled_dir: ./01_manuscript/contents/tables/compiled\n"
        "  compiled_file: ./01_manuscript/contents/tables/compiled/FINAL.tex\n",
        encoding="utf-8",
    )
    return project


def _run(project: Path, *args: str, python: str = "") -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PROJECT_ROOT"] = str(project)
    env["SCITEX_WRITER_DOC_TYPE"] = "manuscript"
    if python:
        env["SCITEX_WRITER_PYTHON"] = python
    return subprocess.run(
        ["bash", str(LAUNCHER), *args],
        cwd=str(project),
        env=env,
        capture_output=True,
        text=True,
        timeout=180,
    )


class TestTableStageReachesPythonEngine:
    """`run_python_pipeline.sh tables` really runs the Python table pipeline."""

    @pytest.fixture
    def rendered(self, tmp_path):
        project = _make_project(tmp_path)
        result = _run(project, "tables")
        # FINAL.tex only \input's the per-table files; the rendered rows live
        # in compiled/<name>.tex.
        compiled = (
            project
            / "01_manuscript"
            / "contents"
            / "tables"
            / "compiled"
            / "01_demo.tex"
        )
        return result, compiled

    def test_table_stage_exits_zero(self, rendered):
        # Arrange
        result, _ = rendered
        # Act
        code = result.returncode
        # Assert
        assert code == 0, result.stdout + result.stderr

    def test_table_stage_invokes_the_python_module(self, rendered):
        # Arrange
        result, _ = rendered
        # Act
        printed = result.stdout
        # Assert
        assert "-m scitex_writer tables render" in printed

    def test_table_stage_preserves_the_inline_math_cell(self, rendered):
        # Arrange
        _, compiled = rendered
        # Act
        text = compiled.read_text(encoding="utf-8")
        # Assert
        assert r"5\% ($p<0.05$)" in text

    def test_table_stage_skips_when_no_tables_requested(self, tmp_path):
        # Arrange
        project = _make_project(tmp_path)
        # Act
        result = _run(project, "tables", "true")
        # Assert
        assert "--no-tables" in result.stdout


class TestMissingPythonEngineFailsLoud:
    """A missing scitex-writer package must ABORT, never fall back to the shell."""

    @pytest.fixture
    def fake_python(self, tmp_path):
        """A real interpreter-shaped executable that cannot import the package."""
        fake = tmp_path / "python-without-scitex-writer"
        fake.write_text(
            '#!/bin/bash\nif [ "$1" = "-c" ]; then exit 1; fi\nexit 1\n',
            encoding="utf-8",
        )
        fake.chmod(0o755)
        return fake

    def test_missing_package_exits_nonzero(self, tmp_path, fake_python):
        # Arrange
        project = _make_project(tmp_path)
        # Act
        result = _run(project, "tables", python=str(fake_python))
        # Assert
        assert result.returncode == 1

    def test_missing_package_prints_install_hint(self, tmp_path, fake_python):
        # Arrange
        project = _make_project(tmp_path)
        # Act
        result = _run(project, "tables", python=str(fake_python))
        # Assert
        assert "pip install -U scitex-writer" in result.stdout

    def test_missing_package_does_not_render_tables(self, tmp_path, fake_python):
        # Arrange
        project = _make_project(tmp_path)
        # Act
        _run(project, "tables", python=str(fake_python))
        # Assert
        assert not (
            project / "01_manuscript" / "contents" / "tables" / "compiled"
        ).exists()


class TestUnknownStageIsRejected:
    """An unknown stage name is a usage error, not a silent no-op."""

    def test_unknown_stage_exits_with_usage_code(self, tmp_path):
        # Arrange
        project = _make_project(tmp_path)
        # Act
        result = _run(project, "nonsense")
        # Assert
        assert result.returncode == 2


if __name__ == "__main__":
    pytest.main([os.path.abspath(__file__)])

# EOF
