#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: _severity.py (shared severity-model resolver, Part D §9)

import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))

from _severity import (  # noqa: E402
    LEVELS,
    LINT_STRICT_ENV,
    env_truthy,
    resolve_level,
)

# Every per-check env var the resolver may read, isolated per test.
_ENV_KEYS = (
    "SCITEX_WRITER_LIMITS",
    "SCITEX_WRITER_OVERFLOW",
    "SCITEX_WRITER_PAPER_SYMLINK",
    "SCITEX_WRITER_REFERENCES",
    "SCITEX_WRITER_LINT_STRICT",
)


# ============================================================================
# helpers / fixtures
# ============================================================================


@pytest.fixture
def clean_env():
    """Isolate the severity env vars + HOME so config/env never leak in."""
    saved = {k: os.environ.get(k) for k in (*_ENV_KEYS, "HOME")}
    for key in _ENV_KEYS:
        os.environ.pop(key, None)
    with tempfile.TemporaryDirectory() as home:
        os.environ["HOME"] = home
        yield home
    for key, val in saved.items():
        if val is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = val


def _write_yaml(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


# ============================================================================
# precedence ladder
# ============================================================================


def test_default_when_nothing_set(tmp_path, clean_env):
    """With no CLI/env/config, the per-check default is returned."""
    # Arrange
    # Act
    level = resolve_level(
        "limits", None, tmp_path, default="warn", env_var="SCITEX_WRITER_LIMITS"
    )
    # Assert
    assert level == "warn"


def test_cli_overrides_default(tmp_path, clean_env):
    """An explicit --level wins over the default."""
    # Arrange
    # Act
    level = resolve_level(
        "limits", "error", tmp_path, default="warn", env_var="SCITEX_WRITER_LIMITS"
    )
    # Assert
    assert level == "error"


def test_cli_overrides_env(tmp_path, clean_env):
    """CLI --level beats the per-check env var."""
    # Arrange
    os.environ["SCITEX_WRITER_LIMITS"] = "off"
    # Act
    level = resolve_level(
        "limits", "error", tmp_path, default="warn", env_var="SCITEX_WRITER_LIMITS"
    )
    # Assert
    assert level == "error"


def test_env_overrides_project_config(tmp_path, clean_env):
    """The per-check env var beats project ./config.yaml."""
    # Arrange
    pytest.importorskip("yaml")
    _write_yaml(tmp_path / "config.yaml", "limits:\n  level: error\n")
    os.environ["SCITEX_WRITER_LIMITS"] = "off"
    # Act
    level = resolve_level(
        "limits", None, tmp_path, default="warn", env_var="SCITEX_WRITER_LIMITS"
    )
    # Assert
    assert level == "off"


def test_project_config_level_honored(tmp_path, clean_env):
    """`<check>.level` in project ./config.yaml is used when no CLI/env."""
    # Arrange
    pytest.importorskip("yaml")
    _write_yaml(tmp_path / "config.yaml", "limits:\n  level: error\n")
    # Act
    level = resolve_level(
        "limits", None, tmp_path, default="warn", env_var="SCITEX_WRITER_LIMITS"
    )
    # Assert
    assert level == "error"


def test_project_config_overrides_user_config(tmp_path, clean_env):
    """Project ./config.yaml wins over user ~/.scitex/writer/config.yaml."""
    # Arrange
    pytest.importorskip("yaml")
    _write_yaml(tmp_path / "config.yaml", "limits:\n  level: error\n")
    _write_yaml(
        Path(clean_env) / ".scitex" / "writer" / "config.yaml",
        "limits:\n  level: off\n",
    )
    # Act
    level = resolve_level(
        "limits", None, tmp_path, default="warn", env_var="SCITEX_WRITER_LIMITS"
    )
    # Assert
    assert level == "error"


def test_user_config_honored_when_no_project_config(tmp_path, clean_env):
    """User-wide config supplies the level when the project has none."""
    # Arrange
    pytest.importorskip("yaml")
    _write_yaml(
        Path(clean_env) / ".scitex" / "writer" / "config.yaml",
        "limits:\n  level: error\n",
    )
    # Act
    level = resolve_level(
        "limits", None, tmp_path, default="warn", env_var="SCITEX_WRITER_LIMITS"
    )
    # Assert
    assert level == "error"


def test_invalid_env_value_falls_through(tmp_path, clean_env):
    """A bogus env value is ignored and the default applies."""
    # Arrange
    os.environ["SCITEX_WRITER_LIMITS"] = "nonsense"
    # Act
    level = resolve_level(
        "limits", None, tmp_path, default="warn", env_var="SCITEX_WRITER_LIMITS"
    )
    # Assert
    assert level == "warn"


# ============================================================================
# legacy_strict tightening (the --strict / <check>.strict alias)
# ============================================================================


def test_legacy_strict_tightens_warn_to_error(tmp_path, clean_env):
    """legacy_strict promotes a resolved warn to error."""
    # Arrange
    # Act
    level = resolve_level(
        "limits",
        None,
        tmp_path,
        default="warn",
        env_var="SCITEX_WRITER_LIMITS",
        legacy_strict=True,
    )
    # Assert
    assert level == "error"


def test_legacy_strict_does_not_touch_off(tmp_path, clean_env):
    """legacy_strict never tightens an explicit off."""
    # Arrange
    # Act
    level = resolve_level(
        "limits",
        "off",
        tmp_path,
        default="warn",
        env_var="SCITEX_WRITER_LIMITS",
        legacy_strict=True,
    )
    # Assert
    assert level == "off"


# ============================================================================
# SCITEX_WRITER_LINT_STRICT — scoped to limits + overflow only
# ============================================================================


def test_lint_strict_tightens_limits(tmp_path, clean_env):
    """LINT_STRICT promotes limits warn -> error (in scope)."""
    # Arrange
    os.environ[LINT_STRICT_ENV] = "1"
    # Act
    level = resolve_level(
        "limits", None, tmp_path, default="warn", env_var="SCITEX_WRITER_LIMITS"
    )
    # Assert
    assert level == "error"


def test_lint_strict_tightens_overflow(tmp_path, clean_env):
    """LINT_STRICT promotes overflow warn -> error (in scope)."""
    # Arrange
    os.environ[LINT_STRICT_ENV] = "1"
    # Act
    level = resolve_level(
        "overflow", None, tmp_path, default="warn", env_var="SCITEX_WRITER_OVERFLOW"
    )
    # Assert
    assert level == "error"


def test_lint_strict_does_not_affect_unscoped_check(tmp_path, clean_env):
    """LINT_STRICT leaves a non-scoped check (references) at warn."""
    # Arrange
    os.environ[LINT_STRICT_ENV] = "1"
    # Act
    level = resolve_level(
        "references",
        None,
        tmp_path,
        default="warn",
        env_var="SCITEX_WRITER_REFERENCES",
    )
    # Assert
    assert level == "warn"


# ============================================================================
# repair level — only for self-fixing checks (paper_symlink)
# ============================================================================


def test_repair_honored_for_paper_symlink(tmp_path, clean_env):
    """paper_symlink accepts the repair level."""
    # Arrange
    # Act
    level = resolve_level(
        "paper_symlink",
        "repair",
        tmp_path,
        default="warn",
        env_var="SCITEX_WRITER_PAPER_SYMLINK",
    )
    # Assert
    assert level == "repair"


def test_repair_ignored_for_non_repair_check(tmp_path, clean_env):
    """A repair value for a non-self-fixing check falls through to default."""
    # Arrange
    # Act
    level = resolve_level(
        "limits", "repair", tmp_path, default="warn", env_var="SCITEX_WRITER_LIMITS"
    )
    # Assert
    assert level == "warn"


# ============================================================================
# env_truthy + module constants
# ============================================================================


def test_env_truthy_true_for_yes(clean_env):
    """env_truthy recognizes a truthy token."""
    # Arrange
    os.environ["SCITEX_WRITER_LINT_STRICT"] = "yes"
    # Act
    result = env_truthy("SCITEX_WRITER_LINT_STRICT")
    # Assert
    assert result is True


def test_env_truthy_false_for_zero(clean_env):
    """env_truthy treats 0 as not truthy."""
    # Arrange
    os.environ["SCITEX_WRITER_LINT_STRICT"] = "0"
    # Act
    result = env_truthy("SCITEX_WRITER_LINT_STRICT")
    # Assert
    assert result is False


def test_levels_tuple_is_canonical_order(clean_env):
    """LEVELS exposes the canonical off<warn<error<repair order."""
    # Arrange
    # Act
    levels = LEVELS
    # Assert
    assert levels == ("off", "warn", "error", "repair")


# EOF
