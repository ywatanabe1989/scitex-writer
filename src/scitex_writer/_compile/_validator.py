#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_compile/_validator.py

"""
Pre-compile validation for writer projects.

Fast, no-heavy-work checks run at the START of compilation (fail-fast) so a
broken or over-limit manuscript is rejected before any pdflatex pass.
"""

from __future__ import annotations

import sys
from logging import getLogger
from pathlib import Path

from .._utils._verify_tree_structure import verify_tree_structure

logger = getLogger(__name__)


def validate_before_compile(project_dir: Path, doc_type: str = "manuscript") -> None:
    """Validate a project before compilation (cheap pre-flight, no heavy work).

    Runs in milliseconds so problems surface immediately instead of after a
    full compile:

    1. Tree-structure verification.
    2. Section word limits + reference cap from ``config/config_<doc_type>.yaml``
       (the ``limits:`` block). Over-limit is a warning and does NOT block
       unless strict mode is on (``limits.strict: true`` /
       ``SCITEX_WRITER_LINT_STRICT=1``), in which case this raises before any
       pdflatex work.
    3. Provenance/symlink checks (paper-symlink, media-provenance) at their
       configured severity. ``off``/``warn`` never block; ``error`` raises
       before any pdflatex work. Mirrors the shell compile gate so the API and
       ``./compile.sh`` paths enforce identically.

    Parameters
    ----------
    project_dir : Path
        Path to project directory.
    doc_type : str
        ``manuscript`` (default), ``supplementary``, or ``revision``.

    Raises
    ------
    RuntimeError
        If structure verification fails, a limit is exceeded under strict, or a
        provenance check is at error severity with a violation.
    """
    verify_tree_structure(project_dir)
    _validate_limits(Path(project_dir), doc_type)
    _validate_provenance(Path(project_dir))


def _validate_limits(project_dir: Path, doc_type: str) -> None:
    """Run the fast limit check; warn (non-strict) or raise (strict)."""
    if doc_type not in ("manuscript", "supplementary", "revision"):
        return
    try:
        from .._mcp.handlers._checks import check_limits
    except Exception as exc:  # pragma: no cover - defensive import guard
        logger.info("Limit check unavailable (%s) - skipping", exc)
        return

    result = check_limits(str(project_dir), doc_type=doc_type)

    # Projects predating check_limits.py: skip quietly, never block compile.
    if not result.get("success") and "exit_code" not in result:
        logger.info("Limit check skipped: %s", result.get("error"))
        return

    findings = (result.get("stdout") or "").strip()
    summary = result.get("summary") or {}
    if summary.get("warnings") or summary.get("errors"):
        # Surface over-limit sections (feedback A->B->A, not fire-and-forget).
        sys.stderr.write(findings + "\n")

    if result.get("exit_code", 0) != 0:
        raise RuntimeError(
            "Section/reference limits exceeded in strict mode — trim the "
            "flagged sections or set limits.strict: false.\n" + findings
        )


def _provenance_runners():
    """Return the (name, callable) provenance checks, or None if unavailable.

    Lazy import so this module stays importable where the MCP handlers (and
    their deps) are absent — the compile path simply skips the checks then.
    """
    try:
        from .._mcp.handlers._checks import (
            check_media_provenance,
            check_paper_symlink,
        )
    except Exception as exc:  # pragma: no cover - defensive import guard
        logger.info("Provenance checks unavailable (%s) - skipping", exc)
        return None
    return (
        ("paper-symlink", check_paper_symlink),
        ("media-provenance", check_media_provenance),
    )


def _validate_provenance(project_dir: Path, runners=None) -> None:
    """Run the config-driven provenance checks; raise if one is at error level
    with a violation.

    paper-symlink and media-provenance each resolve their own severity
    (off|warn|error) from CLI/env/config. ``off``/``warn`` never block; ``error``
    raises before any compile work (fail-loud). Without this, setting a check to
    ``error`` was a silent no-op on the API compile path.

    ``runners`` is an injection seam (a sequence of ``(name, callable)`` pairs):
    production passes ``None`` and the real check handlers are used; tests inject
    real callables returning canned result envelopes.
    """
    if runners is None:
        runners = _provenance_runners()
    if not runners:
        return

    for name, run in runners:
        result = run(str(project_dir))
        # Projects predating the check script: skip quietly, never block compile.
        if not result.get("success") and "exit_code" not in result:
            logger.info("%s check skipped: %s", name, result.get("error"))
            continue
        findings = (result.get("stdout") or "").strip()
        summary = result.get("summary") or {}
        if summary.get("warnings") or summary.get("errors"):
            # Surface findings (feedback A->B->A, not fire-and-forget).
            sys.stderr.write(findings + "\n")
        if result.get("exit_code", 0) != 0:
            raise RuntimeError(
                f"{name} check failed at error severity — fix the violation or "
                "lower its level (off/warn).\n" + findings
            )


__all__ = ["validate_before_compile"]

# EOF
