#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: check_version_freshness.py
#
# The installed version is injected via --installed so tests don't depend on
# whatever scitex_writer is importable in the runner. The vendor stamp is a
# real file in tmp_path. No monkeypatch.

import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from check_version_freshness import (  # noqa: E402
    read_vendor_stamp,
    version_tuple,
)

_SCRIPT = ROOT_DIR / "scripts" / "python" / "check_version_freshness.py"
_STAMP = "00_shared/.scitex-writer-vendored-version"


def _write_stamp(tmp_path, version):
    p = tmp_path / _STAMP
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f"{version}\n# vendored-from stamp\n", encoding="utf-8")
    return p


def _run(tmp_path, *extra):
    env = dict(os.environ)
    env.pop("SCITEX_WRITER_VERSION_FRESHNESS", None)
    env["HOME"] = str(tmp_path / "_home")
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(tmp_path), *extra],
        capture_output=True, text=True, env=env,
    )


# ============================================================================
# unit
# ============================================================================


def test_version_tuple_parses_dotted():
    # Arrange
    s = "2.24.0"
    # Act
    t = version_tuple(s)
    # Assert
    assert t == (2, 24, 0)


def test_version_tuple_handles_suffix():
    # Arrange
    s = "2.24.0rc1"
    # Act
    t = version_tuple(s)
    # Assert
    assert t == (2, 24, 0)


def test_version_tuple_ordering_stale_lt_current():
    # Arrange
    old, new = version_tuple("2.13.4"), version_tuple("2.24.0")
    # Act
    is_stale = old < new
    # Assert
    assert is_stale is True


def test_read_vendor_stamp_reads_first_noncomment_line(tmp_path):
    # Arrange
    _write_stamp(tmp_path, "2.24.0")
    # Act
    v = read_vendor_stamp(tmp_path)
    # Assert
    assert v == "2.24.0"


def test_read_vendor_stamp_none_when_absent(tmp_path):
    # Arrange
    project = tmp_path
    # Act
    v = read_vendor_stamp(project)
    # Assert
    assert v is None


# ============================================================================
# end-to-end gate behaviour
# ============================================================================


def test_stale_vendor_fails(tmp_path):
    """vendored 2.13.4 < installed 2.24.0 -> FAIL (exit 1)."""
    # Arrange
    _write_stamp(tmp_path, "2.13.4")
    # Act
    proc = _run(tmp_path, "--installed", "2.24.0")
    # Assert
    assert proc.returncode == 1


def test_current_vendor_passes(tmp_path):
    """vendored == installed -> pass."""
    # Arrange
    _write_stamp(tmp_path, "2.24.0")
    # Act
    proc = _run(tmp_path, "--installed", "2.24.0")
    # Assert
    assert proc.returncode == 0


def test_vendor_ahead_passes(tmp_path):
    """vendored newer than installed -> pass (not stale)."""
    # Arrange
    _write_stamp(tmp_path, "2.25.0")
    # Act
    proc = _run(tmp_path, "--installed", "2.24.0")
    # Assert
    assert proc.returncode == 0


def test_absent_stamp_warns_not_fails(tmp_path):
    """No vendor stamp -> loud WARN, never blocks (exit 0)."""
    # Arrange
    project = tmp_path
    # Act
    proc = _run(project, "--installed", "2.24.0")
    # Assert
    assert proc.returncode == 0


def test_absent_stamp_message_urges_revendor(tmp_path):
    """The absent-stamp warning points at update-project."""
    # Arrange
    project = tmp_path
    # Act
    proc = _run(project, "--installed", "2.24.0")
    # Assert
    assert "update-project" in proc.stdout


def test_off_level_skips_stale_failure(tmp_path):
    """--level off disables the gate even when stale."""
    # Arrange
    _write_stamp(tmp_path, "2.13.4")
    # Act
    proc = _run(tmp_path, "--installed", "2.24.0", "--level", "off")
    # Assert
    assert proc.returncode == 0


def test_warn_level_does_not_block_stale(tmp_path):
    """--level warn reports staleness but exits 0."""
    # Arrange
    _write_stamp(tmp_path, "2.13.4")
    # Act
    proc = _run(tmp_path, "--installed", "2.24.0", "--level", "warn")
    # Assert
    assert proc.returncode == 0
