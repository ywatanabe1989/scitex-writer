#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: tests/scripts/shell/test_clew_overlay_flag.py

"""``--clew-overlay`` flag threading + render_clew.sh loud-but-graceful degrade.

Two behaviors are covered:

1. render_clew.sh (REAL script, executed in a sandbox whose sub-tools are tiny
   no-op recorder scripts — genuine external programs the module shells out to,
   NOT mocks of internal code, mirroring test_compile_dispatch.py): with the
   clew presentation master switch on but NO clew feed present, it must WARN on
   stderr and still exit 0 (a decorative layer never aborts a compile).

2. The flag→env contract in the three compile_*.sh scripts: ``--clew-overlay``
   exports ``SCITEX_WRITER_CLEW_PRESENTATION=on`` (the master switch the
   presentation layer already consumes).
"""

import subprocess
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[3]
_RENDER_CLEW = _REPO_ROOT / "scripts/shell/modules/render_clew.sh"

_STUB = "#!/usr/bin/env python3\nimport sys\nsys.exit(0)\n"


def _sandbox_render_clew(tmp_path: Path) -> Path:
    """A sandbox holding the REAL render_clew.sh + no-op stub sub-tools."""
    modules = tmp_path / "scripts" / "shell" / "modules"
    modules.mkdir(parents=True)
    (modules / "render_clew.sh").write_bytes(_RENDER_CLEW.read_bytes())
    pydir = tmp_path / "scripts" / "python"
    pydir.mkdir(parents=True)
    for name in ("render_clew_toggles.py", "render_clew.py"):
        (pydir / name).write_text(_STUB)
    return tmp_path


def _run_render_clew(root: Path) -> subprocess.CompletedProcess:
    env = {
        "PATH": "/usr/bin:/bin",
        "PROJECT_ROOT": str(root),
        "SCITEX_WRITER_PYTHON": sys.executable,
        "SCITEX_WRITER_CLEW_PRESENTATION": "on",
        # Point the clew CLI at a name that does not exist so the export step is
        # skipped and only the missing-feed degrade path is exercised.
        "SCITEX_WRITER_CLEW_BIN": "__no_such_clew_bin__",
    }
    return subprocess.run(
        ["bash", str(root / "scripts/shell/modules/render_clew.sh")],
        capture_output=True,
        text=True,
        env=env,
    )


def test_missing_feed_overlay_exits_zero(tmp_path):
    # Arrange: overlay requested (master switch on) but no clew feed on disk.
    root = _sandbox_render_clew(tmp_path)
    # Act
    result = _run_render_clew(root)
    # Assert
    assert result.returncode == 0


def test_missing_feed_overlay_warns_on_stderr(tmp_path):
    # Arrange
    root = _sandbox_render_clew(tmp_path)
    # Act
    result = _run_render_clew(root)
    # Assert
    assert "no clew feed found" in result.stderr


def test_present_feed_overlay_does_not_warn(tmp_path):
    # Arrange: a non-empty clew feed exists, so no missing-feed warning fires.
    root = _sandbox_render_clew(tmp_path)
    feed = root / ".scitex/clew/runtime/claims.json"
    feed.parent.mkdir(parents=True)
    feed.write_text('{"claims": []}\n')
    # Act
    result = _run_render_clew(root)
    # Assert
    assert "no clew feed found" not in result.stderr


@pytest.mark.parametrize(
    "script",
    ["compile_manuscript.sh", "compile_revision.sh", "compile_supplementary.sh"],
)
def test_flag_exports_master_switch(script):
    # Arrange
    text = (_REPO_ROOT / "scripts/shell" / script).read_text(encoding="utf-8")
    # Act
    wired = (
        "--clew-overlay) clew_overlay=true" in text
        and "export SCITEX_WRITER_CLEW_PRESENTATION=on" in text
    )
    # Assert
    assert wired


# EOF
