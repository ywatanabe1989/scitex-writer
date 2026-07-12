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

from ._mcp.handlers import check_caption_footnote as _check_caption_footnote
from ._mcp.handlers import check_citation_trust as _check_citation_trust
from ._mcp.handlers import check_float_order as _check_float_order
from ._mcp.handlers import check_limits as _check_limits
from ._mcp.handlers import check_media_provenance as _check_media_provenance
from ._mcp.handlers import check_overflow as _check_overflow
from ._mcp.handlers import check_paper_symlink as _check_paper_symlink
from ._mcp.handlers import check_ref_integrity as _check_ref_integrity
from ._mcp.handlers import check_references as _check_references
from ._mcp.handlers import check_table_decimals as _check_table_decimals

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

    * ``off`` — check disabled, zero noise.
    * ``warn`` — report drift as a warning (``exit_code`` 0). **This is the
      public default** (when nothing is configured), so the package surfaces
      drift but never errors-by-default.
    * ``error`` — report drift as an error (``exit_code`` 1).
    * ``repair`` — actively fix the safe cases (create / repoint the symlink;
      convert a non-diverged real ``paper/`` dir after backing it up).

    Severity precedence (highest → lowest): the ``level`` argument, env
    ``SCITEX_WRITER_PAPER_SYMLINK``, project ``./config.yaml``
    (``paper_symlink.level``), user ``~/.scitex/writer/config.yaml``
    (``paper_symlink.level``), then the ``warn`` default.

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


def caption_footnote(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision", "all"] = "all",
    level: _Optional[_Literal["off", "warn", "error"]] = None,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Lint: flag ``\\footnote``/``\\footnotetext`` inside a ``\\caption{}``.

    ``\\footnote`` in a caption is a fatal LaTeX pattern — the caption argument
    is reprocessed (list-of-figures + heading), yielding
    ``\\caption@ydblarg`` "extra }" and a runaway ``\\@xfootnote``, fatal in
    ``figure*``/``table*`` spanning floats. The blessed pattern is
    ``\\caption[short]{long\\protect\\footnotemark}`` with ``\\footnotetext``
    **after** the float, so ``\\footnotemark`` in a caption is allowed and is
    **not** flagged.

    Scans the source ``.tex`` under ``<doc>/contents/`` — every
    ``caption_and_media/*.tex`` whole-file (the engine wraps it in
    ``\\caption{}``) plus brace-matched ``\\caption{}`` arguments in other
    source files. The generated assembled doc is not scanned (it duplicates the
    sources), keeping this a pre-compile lint.

    Severity:

    * ``error`` — report as an error (``exit_code`` 1). **The default**, because
      the pattern is always a fatal compile bug; a clean manuscript never fires.
    * ``warn`` — report as a warning (``exit_code`` 0).
    * ``off`` — check disabled.

    Severity precedence (highest → lowest): the ``level`` argument, env
    ``SCITEX_WRITER_CAPTION_FOOTNOTE``, project ``./config.yaml``
    (``caption_footnote.level``), user ``~/.scitex/writer/config.yaml``, then
    the ``error`` default.

    Returns a dict with ``success``, ``exit_code``, ``stdout``, ``stderr``,
    and ``summary={passed, warnings, errors}``.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_caption_footnote`. Exposed so
    callers (and tests) can supply an alternate implementation without patching
    internals.
    """
    handler = handler or _check_caption_footnote
    return handler(project_dir, doc_type, level)


def ref_integrity(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision", "all"] = "all",
    level: _Optional[_Literal["off", "warn", "error"]] = None,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Pre-compile reference-integrity gate over all four reference classes.

    Validates, reporting **all** problems at once (file:line):

    * **figure** ``\\ref`` resolves to a figure label / auto-label,
    * **table** ``\\ref`` resolves to a table label / auto-label,
    * every ``\\cite`` key exists in the merged bibliography,
    * every ``supple-`` cross-document xref resolves against the supplement's
      ``.aux`` — and if the supplement has not been compiled (its ``.aux`` is
      missing) that is reported explicitly as "not compiled", not as a pile of
      undefined refs.

    Designed to run FIRST, fail-fast: at ``error`` it exits non-zero so the
    compile stage blocks (proceeding only on an explicit ``--yes``); ``warn``
    reports without blocking; ``off`` skips. Reuses the ``check_references``
    extractors.

    Severity:

    * ``error`` — report and exit 1. **The default** (a broken ref ships a
      ?-mark / wrong PDF).
    * ``warn`` — report, exit 0 (does not block).
    * ``off`` — gate disabled.

    Severity precedence (highest → lowest): the ``level`` argument, env
    ``SCITEX_WRITER_REF_INTEGRITY``, project ``./config.yaml``
    (``ref_integrity.level``), user ``~/.scitex/writer/config.yaml``, then the
    ``error`` default.

    Returns a dict with ``success``, ``exit_code``, ``stdout``, ``stderr``,
    and ``summary={passed, warnings, errors}``.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_ref_integrity`. Exposed so callers
    (and tests) can supply an alternate implementation without patching
    internals.
    """
    handler = handler or _check_ref_integrity
    return handler(project_dir, doc_type, level)


def table_decimals(
    project_dir: str,
    doc_type: _Literal["manuscript", "supplementary", "revision", "all"] = "all",
    level: _Optional[_Literal["off", "warn", "error"]] = None,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Safety-net lint: warn on inconsistent per-column decimals in compiled tables.

    Companion to the PR #185 auto-pad. That auto-pad (``csv_to_latex.py``
    per-column decimal padding, ``0.35`` -> ``0.350``) is the systemic
    prevention, but it runs ONLY on the pandas backend of the CSV->LaTeX
    pipeline. The external ``csv2latex`` binary (selected with HIGHER priority
    than pandas) and the AWK fallback do not pad, and hand-authored ``.tex``
    tables are never converted -- so a real table can still ship mismatched
    decimals. This lint reads the COMPILED table ``.tex`` under
    ``<doc>/contents/tables/compiled/``: on the pandas path the cells are
    already padded uniform (it does NOT re-flag what the auto-pad fixed), and it
    fires exactly on the un-normalized backends + hand-authored tables. A column
    is flagged only when EVERY data cell is a plain number, the column has a
    fractional value, and the cells disagree on decimal places.

    Severity:

    * ``warn`` — report inconsistent columns, exit 0. **The default** (a safety
      net; the auto-pad prevents the misalignment systemically, so this never
      blocks by default).
    * ``error`` — report and exit 1 (blocks the compile).
    * ``off`` — lint disabled.

    Severity precedence (highest → lowest): the ``level`` argument, env
    ``SCITEX_WRITER_TABLE_DECIMALS``, project ``./config.yaml``
    (``table_decimals.level``), user ``~/.scitex/writer/config.yaml``, then the
    ``warn`` default.

    Returns a dict with ``success``, ``exit_code``, ``stdout``, ``stderr``,
    and ``summary={passed, warnings, errors}``.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_table_decimals`. Exposed so callers
    can supply an alternate implementation without patching internals.
    """
    handler = handler or _check_table_decimals
    return handler(project_dir, doc_type, level)


def citation_trust(
    project_dir: str,
    level: _Optional[_Literal["off", "warn", "error"]] = None,
    offline: bool = False,
    min_confidence: _Optional[float] = None,
    no_cache: bool = False,
    handler: _Optional[_Callable[..., dict]] = None,
) -> dict:
    """Verify every ``\\cite`` resolves to a REAL, trustworthy source.

    Goes beyond :func:`ref_integrity` ("the key exists in the .bib") and the
    citation gate ("the entry is not a scholar stub"): each cited entry is
    RESOLVED against the real bibliographic record via **scitex-scholar**
    (``scitex_scholar.verify_cites``, the ``scholar`` extra) — CrossRef /
    OpenAlex / arXiv / Semantic Scholar — and every citation that cannot be
    shown to be a real source with a matching title is flagged.

    Status → severity (as agreed for the findings feed):

    * ``verified`` → info (suppressed; counted as a pass),
    * ``unverified`` / ``stub`` / ``unlinked`` → warning,
    * ``hallucinated`` → error.

    **Fail-loud, never a silent pass.** When verification cannot RUN —
    scitex-scholar is not installed, the bibliography cannot be resolved, the
    network is unavailable, or the resolver raises — the check reports *that*
    condition at the resolved level (a warning by default, an error with
    ``exit_code`` 1 at ``level="error"``) and never reports the citations as
    trustworthy.

    Verdicts are **cached** in ``.scitex/writer/runtime/citation_trust.json``
    (scholar has no persistent cache in this path), keyed by cite key + a
    content hash of the bib entry, so an edited entry re-verifies. A cache miss
    forces real verification; offline verdicts are never cached.

    **Known gap:** scholar does not check retraction status or predatory
    venues — a resolvable, title-matching citation to a retracted paper still
    classifies as ``verified``.

    Severity:

    * ``warn`` — report, exit 0. **The default** (a network-dependent check must
      never block a compile by default).
    * ``error`` — hallucinated citations (and an un-runnable check) exit 1.
    * ``off`` — check disabled.

    Severity precedence (highest → lowest): the ``level`` argument, env
    ``SCITEX_WRITER_CITATION_TRUST``, project ``./config.yaml``
    (``citation_trust.level``), user ``~/.scitex/writer/config.yaml``, then the
    ``warn`` default.

    Returns a dict with ``success``, ``exit_code``, ``stdout``, ``stderr``,
    and ``summary={passed, warnings, errors}``.

    ``handler`` is the underlying check implementation; it defaults to
    :func:`scitex_writer._mcp.handlers.check_citation_trust`. Exposed so callers
    can supply an alternate implementation without patching internals.
    """
    handler = handler or _check_citation_trust
    return handler(project_dir, level, offline, min_confidence, no_cache)


__all__ = [
    "references",
    "float_order",
    "limits",
    "overflow",
    "paper_symlink",
    "media_provenance",
    "caption_footnote",
    "ref_integrity",
    "table_decimals",
    "citation_trust",
]

# EOF
