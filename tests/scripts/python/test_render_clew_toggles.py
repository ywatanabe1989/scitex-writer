#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: render_clew_toggles.py (writer clew-presentation opt-in)

import subprocess
import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from render_clew_toggles import (  # noqa: E402
    render_toggles_tex,
    resolve_toggles,
)

_SCRIPT = ROOT_DIR / "scripts" / "python" / "render_clew_toggles.py"
_OUT = "00_shared/clew_presentation_toggles.tex"


class TestResolveToggles:
    def test_scalar_on_enables_the_full_master_set(self):
        # Arrange / Act
        toggles = resolve_toggles("on", None)
        # Assert: master set on, attest off.
        assert (
            toggles["markers"] and toggles["badge"] and toggles["legend"]
            and toggles["explainer"] and toggles["signature"]
            and not toggles["attest"]
        )

    def test_scalar_off_disables_everything(self):
        # Arrange / Act
        toggles = resolve_toggles("off", None)
        # Assert
        assert not any(toggles.values())

    def test_absent_config_defaults_all_off(self):
        # Arrange / Act
        toggles = resolve_toggles(None, None)
        # Assert
        assert not any(toggles.values())

    def test_mapping_is_explicit_per_key(self):
        # Arrange / Act
        toggles = resolve_toggles({"markers": True, "badge": False}, None)
        # Assert
        assert toggles["markers"] and not toggles["badge"] and not toggles["legend"]

    def test_env_master_on_overrides_config_off(self):
        # Arrange / Act
        toggles = resolve_toggles("off", "on")
        # Assert
        assert toggles["markers"] and toggles["badge"]

    def test_unknown_mapping_key_is_ignored(self):
        # Arrange: a future toggle whose \newif is not defined yet.
        # Act
        toggles = resolve_toggles({"legend_first": True, "markers": True}, None)
        # Assert
        assert ("legend_first" not in toggles) and toggles["markers"]

    def test_malformed_scalar_raises(self):
        # Arrange
        raises = pytest.raises(ValueError)
        # Act / Assert
        with raises:
            resolve_toggles("maybe", None)


class TestRenderTogglesTex:
    def test_emits_true_line_only_for_enabled_toggles(self):
        # Arrange
        toggles = {"markers": True, "badge": False, "legend": True,
                   "explainer": False, "signature": False, "attest": False}
        # Act
        tex = render_toggles_tex(toggles)
        # Assert
        assert ("\\clewpresmarkerstrue" in tex) and ("\\clewpresbadgetrue" not in tex)


class TestCli:
    def _run(self, project_dir):
        return subprocess.run(
            [sys.executable, str(_SCRIPT), str(project_dir)],
            capture_output=True, text=True,
            env={"PATH": __import__("os").environ["PATH"]},
        )

    def test_config_on_writes_the_toggles_file(self, tmp_path):
        # Arrange
        cfg = tmp_path / ".scitex" / "writer"
        cfg.mkdir(parents=True)
        (cfg / "config.yaml").write_text("clew_presentation: on\n")
        # Act
        self._run(tmp_path)
        # Assert
        assert (tmp_path / _OUT).is_file()

    def test_config_off_removes_a_stale_file(self, tmp_path):
        # Arrange: pre-existing stale toggles file + config off.
        out = tmp_path / _OUT
        out.parent.mkdir(parents=True)
        out.write_text("\\clewpresmarkerstrue\n")
        cfg = tmp_path / ".scitex" / "writer"
        cfg.mkdir(parents=True)
        (cfg / "config.yaml").write_text("clew_presentation: off\n")
        # Act
        self._run(tmp_path)
        # Assert
        assert not out.exists()

    def test_malformed_config_exits_nonzero(self, tmp_path):
        # Arrange
        cfg = tmp_path / ".scitex" / "writer"
        cfg.mkdir(parents=True)
        (cfg / "config.yaml").write_text("clew_presentation: maybe\n")
        # Act
        proc = self._run(tmp_path)
        # Assert
        assert proc.returncode == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
