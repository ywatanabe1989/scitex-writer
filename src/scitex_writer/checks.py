#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/checks.py
# Purpose: Public Python API for pre-compilation project checks.
#
# Wraps the same handlers that MCP and check_project.sh use so that three
# interfaces (scripts, MCP, Python) share one implementation — writer
# issues #44 (float order) and #45 (cross-refs + citations).

"""Pre-compilation check functions.

Usage::

    import scitex_writer as sw

    # Validate every \\ref / \\cite / \\label resolves
    result = sw.checks.references("./my-paper")
    if result["summary"].get("errors"):
        raise SystemExit("Broken references — see result['stdout']")

    # Preview float renumbering
    sw.checks.float_order("./my-paper", dry_run=True)

    # Apply the renumbering
    sw.checks.float_order("./my-paper", fix=True)
"""

from typing import Callable as _Callable
from typing import Literal as _Literal
from typing import Optional as _Optional

from ._mcp.handlers import check_float_order as _check_float_order
from ._mcp.handlers import check_limits as _check_limits
from ._mcp.handlers import check_media_provenance as _check_media_provenance
from ._mcp.handlers import check_overflow as _check_overflow
from ._mcp.handlers import check_paper_symlink as _check_paper_symlink
from ._mcp.handlers import check_references as _check_references

try:
    from scitex_dev.decorators import supports_return_as as _supports_return_as
except ImportError:

    def _supports_return_as(fn):
        return fn


@_supports_return_as
def references(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "all"] = "all",
    parse_log: bool = False,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Validate cross-references, citations, and labels (writer #45).

    Returns a dict with ``success``, ``exit_code``, ``stdout``,
    ``stderr``, and ``summary={passed, warnings, errors}``.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_references`. Exposed so
    callers (and tests) can supply an alternate implementation without
    patching module internals.
    """
    handler = handler or _check_references
    return handler(project_dir, doc_type, parse_log)


@_supports_return_as
def float_order(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "all"] = "manuscript",
    fix: bool = False,
    dry_run: bool = False,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Validate / renumber figure + table reference order (writer #44).

    With ``fix=True`` renames files and updates ``\\ref{}`` / ``\\label{}``
    so floats appear in numerical order. ``dry_run=True`` previews.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_float_order`. Exposed so
    callers (and tests) can supply an alternate implementation without
    patching module internals.
    """
    handler = handler or _check_float_order
    return handler(project_dir, doc_type, fix, dry_run)


@_supports_return_as
def limits(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision"] = "manuscript",
    strict: bool = False,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Validate section word limits + the reference cap (the ``limits:`` block).

    Fast pre-compile check — the same one ``compile`` runs as a gate. Reads the
    ``limits:`` block from ``config/config_<doc_type>.yaml`` and compares it
    against ``texcount`` word counts + unique ``\\cite`` keys. Over-limit is a
    warning by default; ``strict=True`` (or ``limits.strict`` /
    ``SCITEX_WRITER_LINT_STRICT=1``) makes breaches errors with a non-zero
    ``exit_code``.

    Returns a dict with ``success``, ``exit_code``, ``stdout``, ``stderr``,
    and ``summary={passed, warnings, errors}``.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_limits`. Exposed so callers (and
    tests) can supply an alternate implementation without patching module
    internals.
    """
    handler = handler or _check_limits
    return handler(project_dir, doc_type, strict)


@_supports_return_as
def overflow(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision"] = "manuscript",
    strict: bool = False,
    max_pt: _Optional[float] = None,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Detect off-page content — wide tables/figures and over-tall pages.

    Parses the ``.log`` from the last compile for ``Overfull \\hbox`` (too wide)
    and ``Overfull \\vbox`` (too high) boxes; a table that is not shown entirely
    appears as a large hbox. Boxes overflowing by <= ``overflow.max_pt`` (default
    5pt) are cosmetic and ignored; larger ones are warnings, or errors under
    ``strict=True`` (or ``overflow.strict`` / ``SCITEX_WRITER_LINT_STRICT=1``)
    with a non-zero ``exit_code``. Runs AFTER compile — it reads the log —
    unlike the pre-compile :func:`limits`.

    Returns a dict with ``success``, ``exit_code``, ``stdout``, ``stderr``,
    and ``summary={passed, warnings, errors}``.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_overflow`. Exposed so callers (and
    tests) can supply an alternate implementation without patching internals.
    """
    handler = handler or _check_overflow
    return handler(project_dir, doc_type, strict, max_pt)


@_supports_return_as
def paper_symlink(
    project_dir: str,
    level: _Optional[_Literal["off", "warn", "error", "repair"]] = None,
    force_after_backup: bool = False,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Detect / repair drift in the ``paper`` -> ``.scitex/writer`` symlink.

    The ``paper -> .scitex/writer`` link is a **private** convention, so it is
    never enforced by default. Severity is a user-level knob with four levels:

    * ``off`` — check disabled, zero noise. **This is the public default**
      (when nothing is configured), so the package never errors-by-default.
    * ``warn`` — report drift as a warning (``exit_code`` 0).
    * ``error`` — report drift as an error (``exit_code`` 1).
    * ``repair`` — actively fix the safe cases (create / repoint the symlink;
      convert a non-diverged real ``paper/`` dir after backing it up).

    Severity precedence (highest → lowest): the ``level`` argument, env
    ``SCITEX_WRITER_PAPER_SYMLINK``, project ``./config.yaml``
    (``paper_symlink.level``), user ``~/.scitex/writer/config.yaml``
    (``paper_symlink.level``), then the ``off`` default.

    Safety: if ``paper/`` is a real directory holding content that is **not**
    present (same path + same SHA-256) under ``.scitex/writer``, conversion is
    REFUSED and the directory is preserved — it is never deleted or
    overwritten. ``force_after_backup=True`` still moves ``paper/`` to a
    timestamped backup dir before symlinking, so diverged work is never lost.

    Returns a dict with ``success``, ``exit_code``, ``stdout``, ``stderr``,
    and ``summary={passed, warnings, errors}``.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_paper_symlink`. Exposed so callers
    (and tests) can supply an alternate implementation without patching
    internals.
    """
    handler = handler or _check_paper_symlink
    return handler(project_dir, level, force_after_backup)


@_supports_return_as
def media_provenance(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision", "all"] = "all",
    level: _Optional[_Literal["off", "warn", "error"]] = None,
    require_under_scripts: bool = False,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Verify manuscript media are symlinks chained to the producing code.

    Rendered artifacts under ``<doc>/contents/figures/caption_and_media/``
    (image/pdf/tif/svg) and ``<doc>/contents/tables/caption_and_media/``
    (``.csv``) should be **symlinks**, not loose committed copies — so a paper
    stays chained to the scripts that generated it. Caption ``.tex`` files and
    ``.md/.yaml/.yml/.json`` sidecars (incl. figrecipe recipe yamls) are not
    media and are ignored.

    This is a **private** convention, never enforced by default:

    * ``off`` — check disabled (the public default).
    * ``warn`` — report non-symlink media as a warning (``exit_code`` 0).
    * ``error`` — report non-symlink media as an error (``exit_code`` 1).

    ``require_under_scripts`` is the strict mode: each media symlink must also
    resolve to a path under the project ``scripts/`` dir. The flag only ever
    tightens; ``media_provenance.require_under_scripts`` in config can enable it.

    Severity precedence (highest → lowest): the ``level`` argument, env
    ``SCITEX_WRITER_MEDIA_PROVENANCE``, project ``./config.yaml``
    (``media_provenance.level``), user ``~/.scitex/writer/config.yaml``, then
    the ``off`` default.

    Returns a dict with ``success``, ``exit_code``, ``stdout``, ``stderr``,
    and ``summary={passed, warnings, errors}``.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_media_provenance`. Exposed so
    callers (and tests) can supply an alternate implementation without patching
    internals.
    """
    handler = handler or _check_media_provenance
    return handler(project_dir, doc_type, level, require_under_scripts)


__all__ = [
    "references",
    "float_order",
    "limits",
    "overflow",
    "paper_symlink",
    "media_provenance",
]

# EOF
