#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scripts/shell/test_compile_dispatch.py

"""Dispatch/ordering tests for the top-level ``compile.sh`` wrapper.

These exercise the REAL ``compile.sh`` (the code under test) inside a
throw-away sandbox project. The heavy per-document compile scripts it
delegates to (``compile_manuscript.sh`` / ``compile_supplementary.sh`` /
``compile_revision.sh``) are replaced with tiny recorder scripts that only
append their name to an order file. These recorders are genuine executables
standing in for external programs the wrapper shells out to — NOT mocks of
any internal code path — so the dispatch/ordering logic is observed exactly
as it runs in production, without needing a real (unavailable in-container)
LaTeX toolchain.

The combined ``all`` target must compile the supplement FIRST (so its
``.aux`` exists) and the manuscript SECOND, so that main->supplement
xr-hyper cross-references resolve in a single invocation. Single targets
(``-m`` / ``-s`` / ``-r``) must be unchanged: exactly one delegate runs.
"""

import subprocess
from pathlib import Path

import pytest

RECORDER = '#!/bin/bash\necho {name} >> "$PROJECT_ROOT/order.log"\nexit 0\n'


def _find_repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in [p, *p.parents]:
        if (parent / "pyproject.toml").is_file() and (parent / "compile.sh").is_file():
            return parent
    raise RuntimeError(f"Could not find repo root from {__file__}")


@pytest.fixture
def sandbox(tmp_path):
    """A minimal project whose delegate scripts only record their name."""
    root = _find_repo_root()
    # Real wrapper under test.
    (tmp_path / "compile.sh").write_bytes((root / "compile.sh").read_bytes())
    (tmp_path / "compile.sh").chmod(0o755)
    # Recorder stand-ins for the heavy per-document compile scripts.
    shell_dir = tmp_path / "scripts" / "shell"
    shell_dir.mkdir(parents=True)
    for name in ("manuscript", "supplementary", "revision"):
        script = shell_dir / f"compile_{name}.sh"
        script.write_text(RECORDER.format(name=name))
        script.chmod(0o755)
    return tmp_path


def _run(sandbox: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(sandbox / "compile.sh"), *args],
        cwd=str(sandbox),
        capture_output=True,
        text=True,
    )


def _order(sandbox: Path) -> list[str]:
    log = sandbox / "order.log"
    if not log.is_file():
        return []
    return [ln for ln in log.read_text().splitlines() if ln]


def test_all_runs_supplement_before_manuscript(sandbox):
    # Arrange
    target = "all"
    # Act
    _run(sandbox, target)
    # Assert
    assert _order(sandbox) == ["supplementary", "manuscript"]


def test_all_short_flag_runs_supplement_before_manuscript(sandbox):
    # Arrange
    target = "-a"
    # Act
    _run(sandbox, target)
    # Assert
    assert _order(sandbox) == ["supplementary", "manuscript"]


def test_all_does_not_run_revision(sandbox):
    # Arrange
    target = "all"
    # Act
    _run(sandbox, target)
    # Assert
    assert "revision" not in _order(sandbox)


def test_manuscript_single_target_runs_only_manuscript(sandbox):
    # Arrange
    target = "-m"
    # Act
    _run(sandbox, target)
    # Assert
    assert _order(sandbox) == ["manuscript"]


def test_supplementary_single_target_runs_only_supplementary(sandbox):
    # Arrange
    target = "-s"
    # Act
    _run(sandbox, target)
    # Assert
    assert _order(sandbox) == ["supplementary"]


def test_revision_single_target_runs_only_revision(sandbox):
    # Arrange
    target = "-r"
    # Act
    _run(sandbox, target)
    # Assert
    assert _order(sandbox) == ["revision"]


def test_default_no_args_runs_only_manuscript(sandbox):
    # Arrange
    no_args = ()
    # Act
    _run(sandbox, *no_args)
    # Assert
    assert _order(sandbox) == ["manuscript"]


def test_all_help_lists_combined_target(sandbox):
    # Arrange
    flag = "--help"
    # Act
    result = _run(sandbox, flag)
    # Assert
    assert "all, -a" in result.stdout


# EOF
