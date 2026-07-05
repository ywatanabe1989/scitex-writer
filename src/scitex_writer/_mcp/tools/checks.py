#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/tools/checks.py
# Purpose: MCP tool registrations for pre-compilation project checks.
#   - writer_checks_references (issue #45)
#   - writer_checks_float_order (issue #44)
#   - writer_checks_limits
#   - writer_checks_overflow
#   - writer_checks_paper_symlink
#   - writer_checks_media_provenance
#   - writer_checks_caption_footnote
#   - writer_checks_ref_integrity

"""Pre-compilation check MCP tools.

Thin ``@mcp.tool()`` wrappers over ``_mcp.handlers`` -- same handlers backing
the ``scitex_writer.checks`` Python API (see ``checks.py``), so the Python,
MCP, and (where one still exists) shell-script interfaces share one
implementation.
"""

from typing import Literal, Optional

from fastmcp import FastMCP

from ..handlers import (
    check_caption_footnote as _check_caption_footnote,
)
from ..handlers import (
    check_float_order as _check_float_order,
)
from ..handlers import (
    check_limits as _check_limits,
)
from ..handlers import (
    check_media_provenance as _check_media_provenance,
)
from ..handlers import (
    check_overflow as _check_overflow,
)
from ..handlers import (
    check_paper_symlink as _check_paper_symlink,
)
from ..handlers import (
    check_ref_integrity as _check_ref_integrity,
)
from ..handlers import (
    check_references as _check_references,
)


def register_tools(mcp: FastMCP) -> None:
    """Register project-check tools."""

    @mcp.tool()
    def writer_checks_references(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "all"] = "all",
        parse_log: bool = False,
    ) -> dict:
        """Validate cross-references, citations, and labels (issue #45).

        Detects undefined ``\\ref{}`` (PDF ??), undefined ``\\cite{}``,
        multiply-defined ``\\label{}``, orphan labels, and orphan bib
        entries before LaTeX compilation makes them visible. Set
        ``parse_log=True`` to also surface warnings from a previously-
        compiled ``.log`` file.
        """
        return _check_references(project_dir, doc_type, parse_log)

    @mcp.tool()
    def writer_checks_float_order(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "all"] = "manuscript",
        fix: bool = False,
        dry_run: bool = False,
    ) -> dict:
        """Validate (and optionally renumber) float reference order (issue #44).

        ``fix=True`` renames figure/table files and updates ``\\ref{}``
        and ``\\label{}`` so floats appear in numerical order in the
        text. ``dry_run=True`` previews the rename without writing. At
        most one of ``fix`` / ``dry_run`` may be set.
        """
        return _check_float_order(project_dir, doc_type, fix, dry_run)

    @mcp.tool()
    def writer_checks_limits(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
        strict: bool = False,
    ) -> dict:
        """Validate per-section word limits + the reference cap (``limits:`` block).

        Fast pre-compile check: reads ``config/config_<doc_type>.yaml`` and
        compares its ``limits:`` block against ``texcount`` word counts plus
        unique ``\\cite`` keys. Over-limit is a warning by default;
        ``strict=True`` (or ``limits.strict`` / ``SCITEX_WRITER_LINT_STRICT=1``)
        promotes breaches to errors with a non-zero exit code.
        """
        return _check_limits(project_dir, doc_type, strict)

    @mcp.tool()
    def writer_checks_overflow(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "revision"] = "manuscript",
        strict: bool = False,
        max_pt: Optional[float] = None,
    ) -> dict:
        """Detect off-page content (wide tables/figures, over-tall pages).

        Parses the ``.log`` from the last compile for ``Overfull \\hbox``
        (too wide) and ``Overfull \\vbox`` (too tall) boxes. Boxes
        overflowing by <= ``max_pt`` (default 5pt) are cosmetic and
        ignored; larger ones are warnings, or errors under ``strict=True``
        (or ``overflow.strict`` / ``SCITEX_WRITER_LINT_STRICT=1``). Runs
        AFTER compile -- it reads the log -- unlike the pre-compile
        ``writer_checks_limits``.
        """
        return _check_overflow(project_dir, doc_type, strict, max_pt)

    @mcp.tool()
    def writer_checks_paper_symlink(
        project_dir: str,
        level: Optional[Literal["off", "warn", "error", "repair"]] = None,
        force_after_backup: bool = False,
    ) -> dict:
        """Detect / repair drift in the ``paper`` -> ``.scitex/writer`` symlink.

        A PRIVATE convention -- never enforced by default (``warn`` when
        nothing is configured). ``level="repair"`` actively fixes the safe
        cases (create/repoint the symlink; convert a non-diverged real
        ``paper/`` dir after backing it up). Diverged content is NEVER
        deleted or overwritten; ``force_after_backup=True`` still moves
        ``paper/`` to a timestamped backup before symlinking.
        """
        return _check_paper_symlink(project_dir, level, force_after_backup)

    @mcp.tool()
    def writer_checks_media_provenance(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "revision", "all"] = "all",
        level: Optional[Literal["off", "warn", "error"]] = None,
        require_under_scripts: bool = False,
    ) -> dict:
        """Verify manuscript media are symlinks chained to the producing code.

        Rendered artifacts under
        ``<doc>/contents/figures/caption_and_media/`` (image/pdf/tif/svg)
        and ``<doc>/contents/tables/caption_and_media/`` (``.csv``) should
        be symlinks, not loose committed copies. A PRIVATE convention --
        disabled (``off``) by default. ``require_under_scripts=True`` also
        requires each symlink to resolve under the project ``scripts/``
        dir.
        """
        return _check_media_provenance(
            project_dir, doc_type, level, require_under_scripts
        )

    @mcp.tool()
    def writer_checks_caption_footnote(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "revision", "all"] = "all",
        level: Optional[Literal["off", "warn", "error"]] = None,
    ) -> dict:
        """Lint: flag ``\\footnote``/``\\footnotetext`` inside a ``\\caption{}``.

        ``\\footnote`` in a caption is a fatal LaTeX pattern; the blessed
        alternative is ``\\footnotemark`` in-caption with ``\\footnotetext``
        after the float. ``error`` (the default) reports and blocks;
        ``warn`` reports without blocking; ``off`` disables the check.
        """
        return _check_caption_footnote(project_dir, doc_type, level)

    @mcp.tool()
    def writer_checks_ref_integrity(
        project_dir: str,
        doc_type: Literal["manuscript", "supplementary", "revision", "all"] = "all",
        level: Optional[Literal["off", "warn", "error"]] = None,
    ) -> dict:
        """Pre-compile reference-integrity gate over all four reference classes.

        Validates, reporting ALL problems at once (file:line): figure
        ``\\ref`` resolution, table ``\\ref`` resolution, every ``\\cite``
        key existing in the merged bibliography, and ``supple-``
        cross-document xrefs against the supplement's ``.aux`` (a missing
        supplement ``.aux`` is reported explicitly as "not compiled", not
        as undefined refs). ``error`` (the default) exits non-zero so the
        compile stage blocks; ``warn`` reports without blocking; ``off``
        disables the gate.
        """
        return _check_ref_integrity(project_dir, doc_type, level)


# EOF
