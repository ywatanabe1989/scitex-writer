"""Tests for ``scitex_writer/_cli/install.py`` — sub-tool SIF installer.

Per operator design 8566: scitex-writer owns its texlive.def + its
``containers install texlive`` CLI verb that drops the built SIF at
``~/.scitex/writer/containers/texlive.sif``. The build is delegated
to ``scitex_container.apptainer.build`` — same engine sac uses for
``:base`` / ``:scitex`` — for uniform versioning.

Real on-disk via ``tmp_path``; no mocks. The build delegate is
swapped through ``sys.modules`` (a hand-rolled module stand-in, not
``unittest.mock``) — same hand-rolled-callable pattern sac's
``test_image_group.py`` uses for its build runner. AAA, ≥3-word
test names, one assert per test.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

import pytest
from click.testing import CliRunner

from scitex_writer._cli import install as inst
from scitex_writer._cli.install import containers_group

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


@contextmanager
def _swap_recipes_dir(tmp_dir: Path) -> Iterator[None]:
    """Swap the module-level recipes-dir pointer.

    Same swap/restore discipline as ``home_tmp`` — a tmp pointer is
    real (no mock), and the original is restored on exit even when
    the body raises. Used to cover the "recipe not found" branch
    without touching the real ``scripts/containers/`` tree.
    """
    saved = inst._RECIPES_DIR
    inst._RECIPES_DIR = tmp_dir
    try:
        yield
    finally:
        inst._RECIPES_DIR = saved


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
    recipe = inst._resolve_recipe("texlive")
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


# ---------------------------------------------------------------------------
# containers install texlive — happy path
# ---------------------------------------------------------------------------


def test_containers_install_texlive_dry_run_exits_zero(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(containers_group, ["install", "texlive", "--dry-run"])
    # Assert
    assert result.exit_code == 0


def test_containers_install_texlive_dry_run_prints_dry_run_marker(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(containers_group, ["install", "texlive", "--dry-run"])
    # Assert
    assert "dry-run" in result.output


def test_containers_install_texlive_refuses_without_yes_flag(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    result = runner.invoke(containers_group, ["install", "texlive"])
    # Assert
    assert result.exit_code == 2


def test_containers_install_refusal_names_the_target_path(home_tmp):
    # Arrange
    runner = CliRunner()
    expected = str(inst._output_dir() / "texlive.sif")
    # Act
    result = runner.invoke(containers_group, ["install", "texlive"])
    # Assert
    assert expected in result.output


def test_containers_install_with_yes_delegates_to_scitex_container_build(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    with _swap_sc_build(_sc_build_ok) as calls:
        runner.invoke(containers_group, ["install", "texlive", "--yes"])
    # Assert
    assert len(calls) == 1


def test_containers_install_passes_def_path_to_build(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    with _swap_sc_build(_sc_build_ok) as calls:
        runner.invoke(containers_group, ["install", "texlive", "--yes"])
    # Assert
    assert calls[0][1]["def_path"].name == "texlive.def"


def test_containers_install_passes_image_name_texlive(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    with _swap_sc_build(_sc_build_ok) as calls:
        runner.invoke(containers_group, ["install", "texlive", "--yes"])
    # Assert
    assert calls[0][1]["image_name"] == "texlive"


def test_containers_install_passes_output_dir_under_writer_containers(home_tmp):
    # Arrange
    runner = CliRunner()
    expected = Path(os.environ["HOME"]) / ".scitex" / "writer" / "containers"
    # Act
    with _swap_sc_build(_sc_build_ok) as calls:
        runner.invoke(containers_group, ["install", "texlive", "--yes"])
    # Assert
    assert calls[0][1]["output_dir"] == expected


def test_containers_install_creates_output_dir_before_calling_build(home_tmp):
    # Arrange
    runner = CliRunner()
    out = Path(os.environ["HOME"]) / ".scitex" / "writer" / "containers"
    # Act
    with _swap_sc_build(_sc_build_ok):
        runner.invoke(containers_group, ["install", "texlive", "--yes"])
    # Assert
    assert out.is_dir()


def test_containers_install_force_flag_propagates_to_build(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    with _swap_sc_build(_sc_build_ok) as calls:
        runner.invoke(containers_group, ["install", "texlive", "--yes", "--force"])
    # Assert
    assert calls[0][1]["force"] is True


def test_containers_install_success_prints_built_message(home_tmp):
    # Arrange
    runner = CliRunner()
    # Act
    with _swap_sc_build(_sc_build_ok):
        result = runner.invoke(containers_group, ["install", "texlive", "--yes"])
    # Assert
    assert "built" in result.output


# ---------------------------------------------------------------------------
# containers install texlive — failure paths
# ---------------------------------------------------------------------------


def test_containers_install_reports_build_failure_loudly(home_tmp):
    # Arrange — the build engine raises a RuntimeError (mirrors what
    # scitex-container does on apptainer-cli failure).
    def _build_fails(*a, **kw):
        raise RuntimeError("apptainer broken: rc=1")

    runner = CliRunner()
    # Act
    with _swap_sc_build(_build_fails):
        result = runner.invoke(containers_group, ["install", "texlive", "--yes"])
    # Assert
    assert "apptainer build failed" in result.output


def test_containers_install_reports_missing_recipe_loudly(home_tmp, tmp_path):
    # Arrange — point _RECIPES_DIR at an empty real dir (no
    # monkeypatch — the swap is a hand-rolled context manager that
    # restores on exit, same shape as sac's _use_apptainer pattern).
    runner = CliRunner()
    # Act
    with _swap_recipes_dir(tmp_path / "absent-recipes"):
        result = runner.invoke(containers_group, ["install", "texlive", "--yes"])
    # Assert
    assert "recipe not found" in result.output


# ---------------------------------------------------------------------------
# containers (group) — CLI surface
# ---------------------------------------------------------------------------


def test_containers_group_lists_install_subcommand_in_help():
    # Arrange — group --help should advertise the install verb so
    # discoverability is from `scitex-writer containers --help` only.
    runner = CliRunner()
    # Act
    result = runner.invoke(containers_group, ["--help"])
    # Assert
    assert "install" in result.output


def test_containers_group_help_mentions_scitex_writer_containers_path():
    # Arrange — the group docstring names the canonical install path
    # so operators reading --help see the convention without digging.
    runner = CliRunner()
    # Act
    result = runner.invoke(containers_group, ["--help"])
    # Assert
    assert ".scitex/writer/containers" in result.output


def test_containers_install_rejects_unknown_target_via_choice():
    # Arrange — click.Choice on the TARGET argument enforces a closed
    # set at parse time, so an unknown target trips a usage error
    # before _run_install runs.
    runner = CliRunner()
    # Act
    result = runner.invoke(containers_group, ["install", "totally-bogus-target"])
    # Assert
    assert result.exit_code != 0
