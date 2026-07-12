#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_checks.py
# Purpose: Expose scripts/python/check_references.py and check_float_order.py
#          over MCP. Keeps the existing scripts as the single source of truth;
#          this module is a thin subprocess wrapper that normalises their
#          exit codes and text output into a dict the MCP layer can ship.
#
# See writer issues #44 (float order) and #45 (cross-ref + citation check).

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from ..utils import resolve_project_path

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def _run_script(
    script_path: Path,
    project_dir: Path,
    extra_args: list[str],
    timeout: int,
) -> dict:
    if not script_path.exists():
        return {
            "success": False,
            "error": f"Script not found: {script_path}",
        }
    cmd = ["python3", str(script_path), str(project_dir), *extra_args]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Check timed out after {timeout}s",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

    stdout = _strip_ansi(result.stdout)
    stderr = _strip_ansi(result.stderr)
    return {
        "success": result.returncode == 0,
        "exit_code": result.returncode,
        "stdout": stdout,
        "stderr": stderr,
        "summary": _extract_summary(stdout),
    }


def _extract_summary(stdout: str) -> dict:
    """Pull the PASS/WARN/FAIL counts out of the script's summary line."""
    m = re.search(
        r"Summary:\s+(\d+)\s+passed,\s+(\d+)\s+warnings,\s+(\d+)\s+errors",
        stdout,
    )
    if not m:
        return {}
    return {
        "passed": int(m.group(1)),
        "warnings": int(m.group(2)),
        "errors": int(m.group(3)),
    }


def _script_path(project_path: Path, name: str) -> Path:
    return project_path / "scripts" / "python" / name


def check_references(
    project_dir: str,
    doc_type: str = "all",
    parse_log: bool = False,
    timeout: int = 60,
) -> dict:
    """Run cross-reference, citation, and label validation (issue #45).

    Args:
        project_dir: Project root containing ``01_manuscript/``,
            ``02_supplementary/``, and ``00_shared/bib_files/``.
        doc_type: One of ``manuscript``, ``supplementary``, ``all``.
        parse_log: Also parse ``*.log`` files for LaTeX cross-ref warnings.
        timeout: Subprocess timeout in seconds.
    """
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_references.py")
    args = ["--doc-type", doc_type]
    if parse_log:
        args.append("--log")
    return _run_script(script, project_path, args, timeout)


def check_float_order(
    project_dir: str,
    doc_type: str = "manuscript",
    fix: bool = False,
    dry_run: bool = False,
    timeout: int = 60,
) -> dict:
    """Validate (and optionally renumber) figure/table reference order (issue #44).

    Args:
        project_dir: Project root.
        doc_type: ``manuscript``, ``supplementary``, or ``all``.
        fix: Apply rename + reference updates.
        dry_run: Preview the fix without writing.
        timeout: Subprocess timeout in seconds.
    """
    if fix and dry_run:
        return {
            "success": False,
            "error": "Choose either fix=True or dry_run=True, not both.",
        }
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_float_order.py")
    args = ["--doc-type", doc_type]
    if fix:
        args.append("--fix")
    if dry_run:
        args.append("--dry-run")
    return _run_script(script, project_path, args, timeout)


def check_limits(
    project_dir: str,
    doc_type: str = "manuscript",
    strict: bool = False,
    timeout: int = 60,
) -> dict:
    """Validate per-section word limits + the reference cap (``limits:`` block).

    Fast pre-compile check: reads ``config/config_<doc_type>.yaml`` and compares
    the ``limits:`` block against ``texcount`` word counts + unique ``\\cite``
    keys. Over-limit is a warning by default; ``strict`` (or ``limits.strict`` /
    ``SCITEX_WRITER_LINT_STRICT=1``) promotes breaches to errors and a non-zero
    exit code.

    Args:
        project_dir: Project root.
        doc_type: ``manuscript``, ``supplementary``, or ``revision``.
        strict: Force strict mode (over-limit => error). Config/env can also
            enable it; this flag only ever tightens, never loosens.
        timeout: Subprocess timeout in seconds.
    """
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_limits.py")
    args = ["--doc-type", doc_type]
    if strict:
        args.append("--strict")
    return _run_script(script, project_path, args, timeout)


def check_overflow(
    project_dir: str,
    doc_type: str = "manuscript",
    strict: bool = False,
    max_pt: float | None = None,
    timeout: int = 60,
) -> dict:
    """Detect off-page content (wide tables/figures, over-tall pages).

    Parses the ``.log`` from the last compile for ``Overfull \\hbox`` (too wide)
    and ``Overfull \\vbox`` (too high) boxes -- a table that is not shown
    entirely appears here as a large hbox. Boxes overflowing by <=
    ``overflow.max_pt`` (default 5pt) are treated as cosmetic; larger ones are
    warnings, or errors under ``strict`` (or ``overflow.strict`` /
    ``SCITEX_WRITER_LINT_STRICT=1``). Runs AFTER compile -- it needs the log --
    unlike the pre-compile ``check_limits``.

    Args:
        project_dir: Project root.
        doc_type: ``manuscript``, ``supplementary``, or ``revision``.
        strict: Force strict mode (overflow => error). Config/env can also
            enable it; this flag only ever tightens, never loosens.
        max_pt: Ignore boxes overflowing by <= this many pt (overrides the
            ``overflow.max_pt`` config value when given).
        timeout: Subprocess timeout in seconds.
    """
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_overflow.py")
    args = ["--doc-type", doc_type]
    if strict:
        args.append("--strict")
    if max_pt is not None:
        args += ["--max-pt", str(max_pt)]
    return _run_script(script, project_path, args, timeout)


def check_paper_symlink(
    project_dir: str,
    level: str | None = None,
    force_after_backup: bool = False,
    timeout: int = 60,
) -> dict:
    """Detect/repair drift in the top-level ``paper`` -> ``.scitex/writer`` symlink.

    The ``paper -> .scitex/writer`` link is a PRIVATE convention -- warns
    (non-fatally) by default. When ``paper`` silently becomes a REAL directory it
    diverges into two manuscript copies; this check finds that drift and, only
    under ``level="repair"``, fixes the safe cases. Diverged content (files in
    ``paper/`` missing from or differing against ``.scitex/writer``) is NEVER
    deleted or overwritten: ``repair`` refuses unless ``force_after_backup`` is
    set, which always moves ``paper/`` to a timestamped backup first.

    Severity precedence (highest -> lowest): ``level`` arg, env
    ``SCITEX_WRITER_PAPER_SYMLINK``, project ``./config.yaml``
    (``paper_symlink.level``), user ``~/.scitex/writer/config.yaml``, default
    ``warn``.

    Args:
        project_dir: Project root (holds ``.scitex/writer`` and the ``paper``
            link).
        level: One of ``off``, ``warn``, ``error``, ``repair``. When ``None``,
            the env/config precedence resolves the level.
        force_after_backup: On ``repair``, convert even diverged ``paper/`` --
            but always back it up first. Never deletes content.
        timeout: Subprocess timeout in seconds.
    """
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_paper_symlink.py")
    args: list[str] = []
    if level is not None:
        args += ["--level", level]
    if force_after_backup:
        args.append("--force-after-backup")
    return _run_script(script, project_path, args, timeout)


def check_media_provenance(
    project_dir: str,
    doc_type: str = "all",
    level: str | None = None,
    require_under_scripts: bool = False,
    timeout: int = 60,
) -> dict:
    """Verify manuscript media are symlinks (chained to the producing code).

    Rendered artifacts under ``<doc>/contents/figures/caption_and_media/``
    (image/pdf/tif/svg) and ``<doc>/contents/tables/caption_and_media/``
    (``.csv``) should be SYMLINKS, not loose committed copies; caption ``.tex``
    and ``.md/.yaml/.yml/.json`` sidecars are ignored. PRIVATE convention --
    disabled (``off``) by default, so it never errors-by-default.

    Severity precedence (highest -> lowest): ``level`` arg, env
    ``SCITEX_WRITER_MEDIA_PROVENANCE``, project ``./config.yaml``
    (``media_provenance.level``), user ``~/.scitex/writer/config.yaml``, default
    ``off``. ``require_under_scripts`` (strict mode) additionally requires each
    media symlink to resolve under the project ``scripts/`` dir; the flag only
    ever tightens, config can also enable it.

    Args:
        project_dir: Project root.
        doc_type: ``manuscript``, ``supplementary``, ``revision``, or ``all``.
        level: One of ``off``, ``warn``, ``error``. When ``None``, env/config
            precedence resolves the level.
        require_under_scripts: Strict mode -- each symlink must resolve under
            ``scripts/``.
        timeout: Subprocess timeout in seconds.
    """
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_media_provenance.py")
    args = ["--doc-type", doc_type]
    if level is not None:
        args += ["--level", level]
    if require_under_scripts:
        args.append("--require-under-scripts")
    return _run_script(script, project_path, args, timeout)


def check_caption_footnote(
    project_dir: str,
    doc_type: str = "all",
    level: str | None = None,
    timeout: int = 60,
) -> dict:
    """Lint: flag ``\\footnote``/``\\footnotetext`` inside a ``\\caption{}``.

    ``\\footnote`` in a caption is a fatal LaTeX pattern (the caption arg is
    reprocessed -> ``\\caption@ydblarg`` "extra }" + runaway ``\\@xfootnote``,
    fatal in figure*/table* floats). ``\\footnotemark`` is the blessed in-caption
    pattern and is NOT flagged. Scans the source ``.tex`` under
    ``<doc>/contents/`` (caption_and_media/*.tex whole-file, plus brace-matched
    ``\\caption{}`` args elsewhere); the generated assembled doc is not scanned.

    Severity precedence (highest -> lowest): ``level`` arg, env
    ``SCITEX_WRITER_CAPTION_FOOTNOTE``, project ``./config.yaml``
    (``caption_footnote.level``), user ``~/.scitex/writer/config.yaml``, default
    ``error`` (the pattern is always a fatal compile bug; a clean manuscript
    never triggers it).

    Args:
        project_dir: Project root.
        doc_type: ``manuscript``, ``supplementary``, ``revision``, or ``all``.
        level: One of ``off``, ``warn``, ``error``. When ``None``, env/config
            precedence resolves the level.
        timeout: Subprocess timeout in seconds.
    """
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_caption_footnote.py")
    args = ["--doc-type", doc_type]
    if level is not None:
        args += ["--level", level]
    return _run_script(script, project_path, args, timeout)


def check_ref_integrity(
    project_dir: str,
    doc_type: str = "all",
    level: str | None = None,
    timeout: int = 60,
) -> dict:
    """Pre-compile reference-integrity gate: validate every reference class.

    Reports ALL problems at once (file:line) across four classes -- figure
    ``\\ref``, table ``\\ref``, ``\\cite``-key-in-merged-bib, and ``supple-``
    cross-document xrefs (resolved against the supplement's ``.aux``; a missing
    supplement ``.aux`` is reported explicitly as "not compiled" rather than as
    undefined refs) -- then exits non-zero so the compile stage can BLOCK
    (proceeding only on an explicit ``--yes``). Reuses ``check_references.py``'s
    extractors.

    Severity precedence (highest -> lowest): ``level`` arg, env
    ``SCITEX_WRITER_REF_INTEGRITY``, project ``./config.yaml``
    (``ref_integrity.level``), user ``~/.scitex/writer/config.yaml``, default
    ``error`` (a broken ref ships a ?-mark / wrong PDF).

    Args:
        project_dir: Project root.
        doc_type: ``manuscript``, ``supplementary``, ``revision``, or ``all``.
        level: One of ``off``, ``warn``, ``error``. When ``None``, env/config
            precedence resolves the level.
        timeout: Subprocess timeout in seconds.
    """
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_ref_integrity.py")
    args = ["--doc-type", doc_type]
    if level is not None:
        args += ["--level", level]
    return _run_script(script, project_path, args, timeout)


def check_table_decimals(
    project_dir: str,
    doc_type: str = "all",
    level: str | None = None,
    timeout: int = 60,
) -> dict:
    """Safety-net lint: warn on inconsistent per-column decimals in compiled tables.

    The PRIMARY fix (PR #185) makes ``csv_to_latex.py`` per-column decimal-pad
    (``0.35`` -> ``0.350`` so a column aligns), but that auto-pad runs ONLY on
    the pandas backend of the CSV->LaTeX pipeline. The external ``csv2latex``
    binary (chosen with HIGHER priority than pandas) and the AWK fallback do NOT
    pad, and hand-authored ``.tex`` tables are never touched -- so a real table
    can still ship mismatched decimals. This lint reads the COMPILED table
    ``.tex`` (not the source CSV): on the pandas path the cells are already
    padded uniform, so it does NOT re-flag what the auto-pad fixed; it fires
    exactly on the un-normalized backends + hand-authored tables.

    Severity precedence (highest -> lowest): ``level`` arg, env
    ``SCITEX_WRITER_TABLE_DECIMALS``, project ``./config.yaml``
    (``table_decimals.level``), user ``~/.scitex/writer/config.yaml``, default
    ``warn`` (a safety net; the auto-pad is the systemic prevention, so this
    never blocks by default).

    Args:
        project_dir: Project root.
        doc_type: ``manuscript``, ``supplementary``, ``revision``, or ``all``.
        level: One of ``off``, ``warn``, ``error``. When ``None``, env/config
            precedence resolves the level.
        timeout: Subprocess timeout in seconds.
    """
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_table_decimals.py")
    args = ["--doc-type", doc_type]
    if level is not None:
        args += ["--level", level]
    return _run_script(script, project_path, args, timeout)


def check_citation_trust(
    project_dir: str,
    level: str | None = None,
    offline: bool = False,
    min_confidence: float | None = None,
    no_cache: bool = False,
    timeout: int = 300,
) -> dict:
    """Citation-TRUSTWORTHINESS check: does each \\cite resolve to a real source?

    Beyond "the key exists in the .bib" (``check_ref_integrity``) and "the entry
    is not a scholar stub" (``check_citations``): this RESOLVES every cited entry
    against the real bibliographic record via scitex-scholar
    (``scitex_scholar.verify_cites``, the ``scholar`` extra) -- CrossRef /
    OpenAlex / arXiv / Semantic Scholar -- and flags every citation that cannot
    be shown to be a real, trustworthy source. Status -> severity: ``verified``
    -> info (pass), ``unverified``/``stub``/``unlinked`` -> warning,
    ``hallucinated`` -> error.

    FAIL-LOUD: when verification cannot RUN (scitex-scholar not installed, bib
    unresolvable, network down, resolver crash) the check reports that condition
    at the resolved level -- WARN by default, FAIL at ``error`` -- and NEVER
    reports the citations as trustworthy. Verdicts are cached (scholar has no
    cache) in ``.scitex/writer/runtime/citation_trust.json``, keyed by cite key +
    bib-entry content hash.

    KNOWN GAP: scholar does not check retraction status or predatory venues.

    Severity precedence (highest -> lowest): ``level`` arg, env
    ``SCITEX_WRITER_CITATION_TRUST``, project ``./config.yaml``
    (``citation_trust.level``), user ``~/.scitex/writer/config.yaml``, default
    ``warn`` (a network-dependent check must not block a compile by default).

    Args:
        project_dir: Project root.
        level: One of ``off``, ``warn``, ``error``. When ``None``, env/config
            precedence resolves the level.
        offline: Never touch the network (deterministic; unresolvable entries
            are reported UNVERIFIED/HALLUCINATED, never as trustworthy).
        min_confidence: Minimum title-match confidence for a VERIFIED verdict.
        no_cache: Ignore (and do not write) the verdict cache.
        timeout: Subprocess timeout in seconds (network resolution is slow).
    """
    project_path = resolve_project_path(project_dir)
    script = _script_path(project_path, "check_citation_trust.py")
    args: list[str] = []
    if level is not None:
        args += ["--level", level]
    if offline:
        args.append("--offline")
    if min_confidence is not None:
        args += ["--min-confidence", str(min_confidence)]
    if no_cache:
        args.append("--no-cache")
    return _run_script(script, project_path, args, timeout)


__all__ = [
    "check_references",
    "check_float_order",
    "check_limits",
    "check_overflow",
    "check_paper_symlink",
    "check_media_provenance",
    "check_caption_footnote",
    "check_ref_integrity",
    "check_table_decimals",
    "check_citation_trust",
]

# EOF
