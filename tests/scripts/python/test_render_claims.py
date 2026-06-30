"""render_claims.py pre-compile step regenerates claims_rendered.tex from claims.json."""

import json
import subprocess
import sys
from pathlib import Path

_SCRIPT = (
    Path(__file__).resolve().parents[3] / "scripts/python/render_claims.py"
)


def _make_project(tmp_path, claims=None):
    shared = tmp_path / "00_shared"
    shared.mkdir(parents=True)
    if claims is not None:
        (shared / "claims.json").write_text(
            json.dumps({"version": "1.0", "claims": claims}), encoding="utf-8"
        )
    return tmp_path


def _run(project_dir):
    return subprocess.run(
        [sys.executable, str(_SCRIPT), str(project_dir)],
        capture_output=True,
        text=True,
    )


def test_noop_when_no_claims_json(tmp_path):
    # Arrange
    project = _make_project(tmp_path, claims=None)
    # Act
    result = _run(project)
    # Assert
    assert result.returncode == 0 and not (project / "00_shared/claims_rendered.tex").exists()


def test_renders_when_claims_json_present(tmp_path):
    # Arrange
    project = _make_project(tmp_path, claims={"foo": {"type": "value", "value": {"value": 42, "unit": "ms"}}})
    # Act
    _run(project)
    # Assert
    assert "\\vclaim" in (project / "00_shared/claims_rendered.tex").read_text(encoding="utf-8")


def test_regenerates_stale_file(tmp_path):
    # Arrange
    project = _make_project(tmp_path, claims={"foo": {"type": "value", "value": {"value": 1}}})
    stale = project / "00_shared/claims_rendered.tex"
    stale.write_text("%% STALE CLEW PROTOTYPE BLOCK\n", encoding="utf-8")
    # Act
    _run(project)
    # Assert
    assert "STALE CLEW PROTOTYPE" not in stale.read_text(encoding="utf-8")
