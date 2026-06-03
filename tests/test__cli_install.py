"""Tests for ``scitex_writer/_cli/install.py`` — sub-tool SIF installer.

Per operator design 8566: scitex-writer owns its texlive.def + its
``install texlive-sif`` CLI verb that drops the built SIF at
``~/.scitex/writer/containers/texlive.sif``. The build is delegated
to ``scitex_container.apptainer.build`` — same engine sac uses for
``:base`` / ``:scitex`` — for uniform versioning.

Real on-disk via ``tmp_path``; no MagicMock. The build delegate is
swapped through a module-level reassignment (no monkeypatch deep
imports) — same hand-rolled-callable pattern sac's
``test_image_group.py`` uses for its build runner. AAA, ≥3-word
test names, one assert per test.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import pytest
from click.testing import CliRunner

from scitex_writer._cli import install as inst
from scitex_writer._cli.install import install_group

# ---------------------------------------------------------------------------
# Fixtures — tmp HOME so every command writes into tmp_path.
# ---------------------------------------------------------------------------


@pytest.fixture
def home_tmp(tmp_path: Path) -> Iterator[Path]:
    home = tmp_path / "home"
    home.mkdir()
    saved_home = os.environ.get("HOME")
    os.environ["HOME"] = str(home)
    try:
        yield tmp_path
    finally:
        if saved_home is None:
            os.environ.pop("HOME", None)
        else:
            os.environ["HOME"] = saved_home


@contextmanager
def _swap_sc_build(stub) -> Iterator[list[tuple]]:
    """Swap scitex-container's build engine for a recording fake.

    The install verb imports ``scitex_container.apptainer.build`` at
    call time inside ``_run_install``. We override the resolved
    callable via ``sys.modules`` patching — same swap-and-restore
    discipline as the sac side. The yielded list collects every call.
    """
    import sys
    import types

    calls: list[tuple] = []

    def _fake(*a, **kw):
        calls.append((a, kw))
        return stub(*a, **kw)

    sc = types.ModuleType("scitex_container")
    sc_apt = types.ModuleType("scitex_container.apptainer")
    sc_apt.build = _fake
    sc.apptainer = sc_apt

    saved_sc = sys.modules.get("scitex_container")
    saved_sc_apt = sys.modules.get("scitex_container.apptainer")
    sys.modules["scitex_container"] = sc
    sys.modules["scitex_container.apptainer"] = sc_apt
    try:
        yield calls
    finally:
        if saved_sc is None:
            sys.modules.pop("scitex_container", None)
        else:
            sys.modules["scitex_container"] = saved_sc
        if saved_sc_apt is None:
            sys.modules.pop("scitex_container.apptainer", None)
        else:
            sys.modules["scitex_container.apptainer"] = saved_sc_apt


def _sc_build_ok(*a, **kw) -> Path:
    """Default stub — returns the path the build verb expects to output."""
    return Path(kw["output_dir"]) / f"{kw['image_name']}.sif"


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------


def test_output_dir_is_under_dotscitex_writer_containers(home_tmp):
    # Arrange — operator convention pinned: ~/.scitex/writer/containers/.
    expected = Path(os.environ["HOME"]) / ".scitex" / "writer" / "containers"
    # Act
    actual = inst._output_dir()
    # Assert
    assert actual == expected


def test_resolve_recipe_finds_texlive_def_in_scripts_containers():
    # Arrange — the shipped recipe lives at scripts/containers/texlive.def.
    # Act
    recipe = inst._resolve_recipe("texlive-sif")
    # Assert
    assert recipe.name == "texlive.def"


def test_resolve_recipe_raises_usage_error_for_unknown_target():
    # Arrange
    import click

    # Act
    def _call():
        return inst._resolve_recipe("bogus-target")

    # Assert
    with pytest.raises(click.UsageError):
        _call()


def test_image_name_for_strips_sif_suffix():
    # Arrange — the SIF artifact's basename is the target minus "-sif".
    # Act
    name = inst._image_name_for("texlive-sif")
    # Assert
    assert name == "texlive"


# ---------------------------------------------------------------------------
# install texlive-sif — happy path
# ---------------------------------------------------------------------------


def test_install_texlive_sif_dry_run_exits_zero(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(install_group, ["texlive-sif", "--dry-run"])
    # Assert
    assert result.exit_code == 0


def test_install_texlive_sif_dry_run_prints_dry_run_marker(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(install_group, ["texlive-sif", "--dry-run"])
    # Assert
    assert "dry-run" in result.output


def test_install_texlive_sif_refuses_without_yes_flag(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(install_group, ["texlive-sif"])
    # Assert
    assert result.exit_code == 2


def test_install_texlive_sif_refusal_names_the_target_path(home_tmp):
    # Arrange
    runner = CliRunner()
    expected = str(inst._output_dir() / "texlive.sif")
    # Act
    result = runner.invoke(install_group, ["texlive-sif"])
    # Assert
    assert expected in result.output


def test_install_texlive_sif_with_yes_delegates_to_scitex_container_build(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    with _swap_sc_build(_sc_build_ok) as calls:
        runner.invoke(install_group, ["texlive-sif", "--yes"])
    # Assert
    assert len(calls) == 1


def test_install_texlive_sif_passes_def_path_to_build(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    with _swap_sc_build(_sc_build_ok) as calls:
        runner.invoke(install_group, ["texlive-sif", "--yes"])
    # Assert
    assert calls[0][1]["def_path"].name == "texlive.def"


def test_install_texlive_sif_passes_image_name_texlive(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    with _swap_sc_build(_sc_build_ok) as calls:
        runner.invoke(install_group, ["texlive-sif", "--yes"])
    # Assert
    assert calls[0][1]["image_name"] == "texlive"


def test_install_texlive_sif_passes_output_dir_under_writer_containers(home_tmp):
    # Arrange
    runner = CliRunner()
    expected = Path(os.environ["HOME"]) / ".scitex" / "writer" / "containers"
    # Act
    with _swap_sc_build(_sc_build_ok) as calls:
        runner.invoke(install_group, ["texlive-sif", "--yes"])
    # Assert
    assert calls[0][1]["output_dir"] == expected


def test_install_texlive_sif_creates_output_dir_before_calling_build(home_tmp):
    # Arrange
    runner = CliRunner()
    out = Path(os.environ["HOME"]) / ".scitex" / "writer" / "containers"
    # Act
    with _swap_sc_build(_sc_build_ok):
        runner.invoke(install_group, ["texlive-sif", "--yes"])
    # Assert
    assert out.is_dir()


def test_install_texlive_sif_force_flag_propagates_to_build(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    with _swap_sc_build(_sc_build_ok) as calls:
        runner.invoke(install_group, ["texlive-sif", "--yes", "--force"])
    # Assert
    assert calls[0][1]["force"] is True


def test_install_texlive_sif_success_prints_built_message(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    with _swap_sc_build(_sc_build_ok):
        result = runner.invoke(install_group, ["texlive-sif", "--yes"])
    # Assert
    assert "built" in result.output


# ---------------------------------------------------------------------------
# install texlive-sif — failure paths
# ---------------------------------------------------------------------------


def test_install_texlive_sif_reports_build_failure_loudly(home_tmp):
    # Arrange — the build engine raises a RuntimeError (mirrors what
    # scitex-container does on apptainer-cli failure).
    def _build_fails(*a, **kw):
        raise RuntimeError("apptainer broken: rc=1")

    runner = CliRunner()
    # Act
    with _swap_sc_build(_build_fails):
        result = runner.invoke(install_group, ["texlive-sif", "--yes"])
    # Assert
    assert "apptainer build failed" in result.output


def test_install_texlive_sif_reports_missing_recipe_loudly(home_tmp, monkeypatch):
    # Arrange — point _RECIPES_DIR at an empty real dir; no monkeypatch
    # on the deep import — just swap the module attribute (same
    # convention as sac).
    saved = inst._RECIPES_DIR
    inst._RECIPES_DIR = home_tmp / "absent-recipes"
    runner = CliRunner()
    try:
        # Act
        result = runner.invoke(install_group, ["texlive-sif", "--yes"])
    finally:
        inst._RECIPES_DIR = saved
    # Assert
    assert "recipe not found" in result.output


# ---------------------------------------------------------------------------
# install (group) — CLI surface
# ---------------------------------------------------------------------------


def test_install_group_lists_texlive_sif_in_help():
    # Arrange — group --help should advertise the texlive-sif target so
    # discoverability is from `scitex-writer install --help` only.
    runner = CliRunner()
    # Act
    result = runner.invoke(install_group, ["--help"])
    # Assert
    assert "texlive-sif" in result.output


def test_install_group_help_mentions_scitex_writer_containers_path():
    # Arrange — the group docstring names the canonical install path
    # so operators reading --help see the convention without digging.
    runner = CliRunner()
    # Act
    result = runner.invoke(install_group, ["--help"])
    # Assert
    assert ".scitex/writer/containers" in result.output


def test_install_texlive_sif_rejects_unknown_subcommand(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(install_group, ["totally-bogus-target"])
    # Assert
    assert result.exit_code != 0
