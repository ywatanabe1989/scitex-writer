#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/_severity.py
# Purpose: Shared severity-model resolver for the writer pre-compile / lint
#          checks. Single source of truth for resolving a check's effective
#          `level` from the documented precedence ladder, plus the two
#          tightening-only overlays (the per-check `strict` alias and the
#          scoped `SCITEX_WRITER_LINT_STRICT` global).
#
#          Ratified contract: docs/03_DESIGN_SEVERITY_MODEL_CONTRACT.md
#          (Part D; §9 sign-off 2026-06-27).
#
#          Precedence (first match wins):
#            1. CLI --level                          (cli_level)
#            2. per-check env SCITEX_WRITER_<CHECK>   (env_var)
#            3. project ./config.yaml                -> <check>.level
#            4. user ~/.scitex/writer/config.yaml    -> <check>.level
#            5. per-check default                    (default)
#          Then warn -> error tightening (never loosens, never touches off):
#            * legacy_strict truthy   (--strict / <check>.strict alias)
#            * SCITEX_WRITER_LINT_STRICT truthy AND check in {limits, overflow}
#
# Self-contained: stdlib + optional PyYAML (config files are silently skipped
# when PyYAML is absent, so CLI + env still resolve). Imported by the sibling
# `check_*.py` standalones.

import os
import sys
from pathlib import Path

# off < warn < error < repair. `repair` is error-semantics plus a safe
# deterministic self-fix and is valid ONLY for checks that can auto-fix.
LEVELS = ("off", "warn", "error", "repair")

LINT_STRICT_ENV = "SCITEX_WRITER_LINT_STRICT"

# SCITEX_WRITER_LINT_STRICT is a SCOPED overlay -- it tightens only these two
# checks (exact back-compat with the historical `strict` bool). It is NOT a
# global tighten-all (operator §9 sign-off, 2026-06-27).
_LINT_STRICT_CHECKS = frozenset({"limits", "overflow"})

# Only these checks accept the `repair` level (they can self-fix safely).
_REPAIR_CHECKS = frozenset({"paper_symlink"})

_TRUTHY = ("1", "true", "yes")


def _valid_levels(check):
    """Levels accepted for ``check`` (``repair`` only for self-fixing checks)."""
    return LEVELS if check in _REPAIR_CHECKS else LEVELS[:3]


def _norm(value, check):
    """Lowercased ``value`` iff it is a level valid for ``check``, else None."""
    if isinstance(value, str):
        low = value.strip().lower()
        if low in _valid_levels(check):
            return low
    return None


def _coerce_config_level(raw, check, source):
    """Coerce a raw config ``level`` value to a valid level, or None.

    YAML 1.1 coerces a bare ``off``/``no``/``false`` to Python ``False``, so
    ``level: off`` arrives as ``False`` rather than the string ``"off"`` -- per
    the §2 contract ruling this MUST still disable the check, so ``False`` maps
    to ``"off"``. A genuinely invalid value (``True`` from ``on``/``yes``, or a
    typo'd string) is NOT silently dropped: a one-line hint is printed and the
    value is treated as unset (caller falls through to its default). A missing
    key (``None``) stays a silent no-op.
    """
    if raw is None:
        return None
    if isinstance(raw, bool):
        if raw is False:  # YAML off / no / false -> disable
            return "off"
        # True came from on / yes / true -- not a meaningful severity level.
        _warn_invalid_level(raw, check, source)
        return None
    norm = _norm(raw, check)
    if norm is not None:
        return norm
    _warn_invalid_level(raw, check, source)
    return None


def _warn_invalid_level(raw, check, source):
    """Fail loud (one line) on an invalid config ``level``; never crash."""
    valid = "/".join(_valid_levels(check))
    sys.stderr.write(
        f"[WARN] {source}: {check}.level must be one of {valid}; got {raw!r} "
        f"-- ignoring (using default). Quote string values, e.g. level: \"off\".\n"
    )


def env_truthy(name):
    """True iff env var ``name`` is set to a truthy token (1/true/yes)."""
    return os.environ.get(name, "").strip().lower() in _TRUTHY


def _read_config_level(config_path, check):
    """Read ``<check>.level`` from a YAML config, or None.

    A missing file/key is None (not an error). PyYAML is optional -- absent it,
    config files are silently skipped so CLI + env still resolve.
    """
    if not config_path.exists():
        return None
    try:
        import yaml
    except ImportError:
        return None
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception:
        return None
    if not isinstance(data, dict):
        return None
    block = data.get(check)
    if not isinstance(block, dict):
        return None
    return _coerce_config_level(block.get("level"), check, str(config_path))


def resolve_level(
    check, cli_level, project_dir, *, default, env_var, legacy_strict=None
):
    """Resolve a check's effective severity level.

    See the module header for the precedence ladder and the two tightening
    overlays. ``repair`` from any source is ignored for checks that cannot
    self-fix. Returns one of ``off`` / ``warn`` / ``error`` / ``repair``.

    Parameters
    ----------
    check : str
        Check name; also the ``<check>`` config-block stem.
    cli_level : str or None
        The check's ``--level`` value (None when unset).
    project_dir : str or Path
        Project root (holds ``./config.yaml``).
    default : str
        Per-check default when nothing else matches.
    env_var : str
        The check's ``SCITEX_WRITER_<CHECK>`` env var name.
    legacy_strict : bool or None
        The legacy strict alias (``--strict`` / ``<check>.strict``). None/False
        is a no-op; True tightens a resolved ``warn`` to ``error``.
    """
    # `default` runs through the same gate as every other source: a default of
    # `repair` for a non-self-fixing check is rejected (falls to `error`), so
    # the repair gate is airtight even against a mis-specified caller default.
    level = (
        _norm(cli_level, check)
        or _norm(os.environ.get(env_var, ""), check)
        or _read_config_level(Path(project_dir) / "config.yaml", check)
        # Path.home() is resolved at call time (not import) so a changed $HOME
        # is honored -- matches the sibling check_*.py resolvers.
        or _read_config_level(
            Path.home() / ".scitex" / "writer" / "config.yaml", check
        )
        or _norm(default, check)
        or "error"
    )

    # Tightening-only overlays: warn -> error. Never loosen; never touch off.
    if level == "warn":
        if legacy_strict:
            level = "error"
        elif check in _LINT_STRICT_CHECKS and env_truthy(LINT_STRICT_ENV):
            level = "error"

    return level


__all__ = ["resolve_level", "env_truthy", "LEVELS", "LINT_STRICT_ENV"]

# EOF
