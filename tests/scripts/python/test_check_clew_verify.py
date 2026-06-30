#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_clew_verify.py
#
# The check shells out to the `clew` CLI. To keep tests hermetic (no real
# scitex-clew install, no real claim store), we point SCITEX_WRITER_CLEW_BIN at
# a FAKE clew executable whose exit code is driven by $FAKE_CLEW_EXIT. That
# lets us exercise every exit-code branch (0 / 10-13 / 20 / missing) without a
# LaTeX toolchain or a real clew.

import os
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_clew_verify import (  # noqa: E402
    _is_research_project,
    resolve_level,
    resolve_strict,
)

_SCRIPT = ROOT_DIR / "scripts" / "python" / "check_clew_verify.py"

_FAKE_CLEW = """#!/usr/bin/env python3
import os, sys
sys.stdout.write("fake clew args: %s\\n" % " ".join(sys.argv[1:]))
sys.exit(int(os.environ.get("FAKE_CLEW_EXIT", "0")))
"""

_ENV_KEYS = (
    "SCITEX_WRITER_CLEW_VERIFY",
    "SCITEX_WRITER_CLEW_BIN",
    "FAKE_CLEW_EXIT",
    "HOME",
)


def _write(tmp_path, rel, content):
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def _mark_research(tmp_path):
    _write(tmp_path, ".scitex/dev/config.yaml", "project-type: research\n")


def _make_fake_clew(tmp_path):
    p = tmp_path / "fake_clew"
    p.write_text(_FAKE_CLEW, encoding="utf-8")
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
    return p


def _run(project, *extra, clew_bin=None, clew_exit=None, env_level=None):
    env = dict(os.environ)
    for k in _ENV_KEYS:
        env.pop(k, None)
    env["HOME"] = str(Path(project) / "_home")
    if clew_bin is not None:
        env["SCITEX_WRITER_CLEW_BIN"] = str(clew_bin)
    if clew_exit is not None:
        env["FAKE_CLEW_EXIT"] = str(clew_exit)
    if env_level is not None:
        env["SCITEX_WRITER_CLEW_VERIFY"] = env_level
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(project), *extra],
        capture_output=True,
        text=True,
        env=env,
    )


@pytest.fixture
def clean_env():
    saved = {k: os.environ.get(k) for k in _ENV_KEYS}
    for k in _ENV_KEYS:
        if k != "HOME":
            os.environ.pop(k, None)
    with tempfile.TemporaryDirectory() as home:
        os.environ["HOME"] = home
        yield home
    for key, val in saved.items():
        if val is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = val


# ============================================================================
# project-type detection -> default level
# ============================================================================


def test_research_marker_detected(tmp_path):
    """A .scitex/dev/config.yaml project-type: research is recognised."""
    # Arrange
    _mark_research(tmp_path)
    # Act / Assert
    assert _is_research_project(tmp_path) is True


def test_non_research_when_marker_absent(tmp_path):
    """No marker file => not a research project."""
    # Arrange / Act / Assert
    assert _is_research_project(tmp_path) is False


def test_default_off_for_non_research(tmp_path, clean_env):
    """Non-research projects default to off (gate disabled)."""
    # Arrange / Act
    level = resolve_level(
        "clew_verify", None, tmp_path,
        default="off", env_var="SCITEX_WRITER_CLEW_VERIFY",
    )
    # Assert
    assert level == "off"


# ============================================================================
# end-to-end gate behaviour
# ============================================================================


def test_non_research_passes_without_clew(tmp_path, clean_env):
    """A non-research project compiles fine with no clew and no claims."""
    # Arrange (no marker, no clew bin)
    # Act
    proc = _run(tmp_path, clew_bin=tmp_path / "does_not_exist")
    # Assert
    assert proc.returncode == 0


def test_research_missing_clew_warns_not_blocks(tmp_path, clean_env):
    """Research project + clew CLI absent => WARN, never block (exit 0)."""
    # Arrange
    _mark_research(tmp_path)
    # Act
    proc = _run(tmp_path, clew_bin=tmp_path / "no_such_clew")
    # Assert
    assert proc.returncode == 0
    assert "not found" in proc.stdout


def test_research_clew_ok_passes(tmp_path, clean_env):
    """Research project + clew verify OK (0) => pass, exit 0."""
    # Arrange
    _mark_research(tmp_path)
    clew = _make_fake_clew(tmp_path)
    # Act
    proc = _run(tmp_path, clew_bin=clew, clew_exit=0)
    # Assert
    assert proc.returncode == 0


@pytest.mark.parametrize("code", [10, 11, 12, 13])
def test_research_verify_failure_blocks(tmp_path, clean_env, code):
    """Research project + a real verify failure (10-13) => exit 1 (gate blocks)."""
    # Arrange
    _mark_research(tmp_path)
    clew = _make_fake_clew(tmp_path)
    # Act
    proc = _run(tmp_path, clew_bin=clew, clew_exit=code)
    # Assert
    assert proc.returncode == 1


def test_research_no_claims_warns_not_blocks(tmp_path, clean_env):
    """NO_CLAIMS (20) is a warning, not a hard block, even for research."""
    # Arrange
    _mark_research(tmp_path)
    clew = _make_fake_clew(tmp_path)
    # Act
    proc = _run(tmp_path, clew_bin=clew, clew_exit=20)
    # Assert
    assert proc.returncode == 0


def test_off_level_skips_failing_clew(tmp_path, clean_env):
    """--level off disables the gate even when clew verify fails."""
    # Arrange
    _mark_research(tmp_path)
    clew = _make_fake_clew(tmp_path)
    # Act
    proc = _run(tmp_path, "--level", "off", clew_bin=clew, clew_exit=12)
    # Assert
    assert proc.returncode == 0


def test_warn_level_does_not_block(tmp_path, clean_env):
    """--level warn reports a verify failure but exits 0 (does not block)."""
    # Arrange
    _mark_research(tmp_path)
    clew = _make_fake_clew(tmp_path)
    # Act
    proc = _run(tmp_path, "--level", "warn", clew_bin=clew, clew_exit=12)
    # Assert
    assert proc.returncode == 0


def test_cli_error_overrides_non_research_default(tmp_path, clean_env):
    """--level error forces the gate ON for a non-research project."""
    # Arrange (no research marker)
    clew = _make_fake_clew(tmp_path)
    # Act
    proc = _run(tmp_path, "--level", "error", clew_bin=clew, clew_exit=12)
    # Assert
    assert proc.returncode == 1


def test_env_level_enables_gate(tmp_path, clean_env):
    """SCITEX_WRITER_CLEW_VERIFY=error enables the gate via env."""
    # Arrange
    clew = _make_fake_clew(tmp_path)
    # Act
    proc = _run(tmp_path, clew_bin=clew, clew_exit=11, env_level="error")
    # Assert
    assert proc.returncode == 1


def test_strict_flag_passed_through_to_clew(tmp_path, clean_env):
    """--strict is forwarded to the clew invocation."""
    # Arrange
    _mark_research(tmp_path)
    clew = _make_fake_clew(tmp_path)
    # Act
    proc = _run(tmp_path, "--strict", clew_bin=clew, clew_exit=0)
    # Assert
    assert "--strict" in proc.stdout


def test_resolve_strict_cli_tightens(tmp_path):
    """The --strict CLI flag wins regardless of config."""
    # Arrange / Act / Assert
    assert resolve_strict(True, tmp_path) is True
    assert resolve_strict(False, tmp_path) is False
