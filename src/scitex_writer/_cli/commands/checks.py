#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_cli/commands/checks.py

"""Fast pre-compile check commands (flat verb-noun per §1)."""

from __future__ import annotations

import click

from .._core import main_group
from .._helpers import _DOC_TYPE, _emit_json

# =========================================================================
# check-limits / check-references  (fast pre-compile checks; flat verb-noun
# per §1 — top-level commands are verb-noun, e.g. compile-manuscript)
# =========================================================================


@main_group.command("check-limits")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE, default="manuscript")
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Treat over-limit sections as errors (non-zero exit).",
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def check_limits_cmd(project, doc_type, strict, as_json):
    """Check section word limits + reference cap against config ``limits:``.

    Reads the ``limits:`` block from config/config_<doc-type>.yaml and compares
    it to texcount word counts + unique \\cite keys. Over-limit warns by
    default; --strict (or limits.strict) makes it a non-zero-exit error. This
    is the same check the compiler runs as a fast pre-flight gate.

    \b
    Example:
        $ scitex-writer check-limits
        $ scitex-writer check-limits -t supplementary --strict
        $ scitex-writer check-limits --json
    """
    from ... import checks

    result = checks.limits(project, doc_type=doc_type, strict=strict)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    out = (result.get("stdout") or "").rstrip()
    if out:
        click.echo(out)
    err = (result.get("stderr") or "").rstrip()
    if err:
        click.echo(err, err=True)
    return result.get("exit_code", 0)


@main_group.command("check-overflow")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option("-t", "--doc-type", type=_DOC_TYPE, default="manuscript")
@click.option(
    "--strict",
    is_flag=True,
    default=False,
    help="Treat overflow as errors (non-zero exit).",
)
@click.option(
    "--max-pt",
    type=float,
    default=None,
    help="Ignore boxes overflowing by <= this many pt (default 5; overrides config).",
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def check_overflow_cmd(project, doc_type, strict, max_pt, as_json):
    """Detect off-page content (wide tables/figures, over-tall pages) from the .log.

    Parses the LaTeX log from the last compile for ``Overfull \\hbox`` / ``\\vbox``
    boxes -- a table that is not shown entirely appears as a large hbox. Boxes
    overflowing by <= overflow.max_pt are cosmetic; larger ones warn (or error
    with --strict). Run AFTER a compile, since it reads the produced log.

    \b
    Example:
        $ scitex-writer check-overflow
        $ scitex-writer check-overflow -t supplementary --strict
        $ scitex-writer check-overflow --max-pt 2
    """
    from ... import checks

    result = checks.overflow(project, doc_type=doc_type, strict=strict, max_pt=max_pt)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    out = (result.get("stdout") or "").rstrip()
    if out:
        click.echo(out)
    err = (result.get("stderr") or "").rstrip()
    if err:
        click.echo(err, err=True)
    return result.get("exit_code", 0)


@main_group.command("check-paper-symlink")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option(
    "--level",
    type=click.Choice(["off", "warn", "error", "repair"]),
    default=None,
    help="Severity: off (default), warn, error, or repair. Overrides env/config.",
)
@click.option(
    "--force-after-backup",
    is_flag=True,
    default=False,
    help="On repair, convert even a diverged paper/ dir -- but back it up first.",
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def check_paper_symlink_cmd(project, level, force_after_backup, as_json):
    """Detect/repair drift in the `paper` -> `.scitex/writer` convenience symlink.

    `paper -> .scitex/writer` is a private convention -- disabled (off) by
    default. When `paper` silently becomes a REAL directory it diverges into
    two manuscript copies; this finds that drift. With --level repair it fixes
    the safe cases, but NEVER deletes diverged content (use --force-after-backup
    to back it up first). Severity precedence: --level > env
    SCITEX_WRITER_PAPER_SYMLINK > ./config.yaml > ~/.scitex/writer/config.yaml.

    \b
    Example:
        $ scitex-writer check-paper-symlink
        $ scitex-writer check-paper-symlink --level repair
        $ scitex-writer check-paper-symlink --level repair --force-after-backup
    """
    from ... import checks

    result = checks.paper_symlink(
        project, level=level, force_after_backup=force_after_backup
    )
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    out = (result.get("stdout") or "").rstrip()
    if out:
        click.echo(out)
    err = (result.get("stderr") or "").rstrip()
    if err:
        click.echo(err, err=True)
    return result.get("exit_code", 0)


@main_group.command("check-references")
@click.option("-p", "--project", default=".", help="Project path.")
@click.option(
    "-t",
    "--doc-type",
    type=click.Choice(["manuscript", "supplementary", "all"]),
    default="all",
)
@click.option(
    "--log",
    "parse_log",
    is_flag=True,
    default=False,
    help="Also parse LaTeX .log files for cross-ref/citation warnings.",
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Emit JSON.")
def check_references_cmd(project, doc_type, parse_log, as_json):
    """Validate cross-references, citations, labels, and duplicate headings.

    Duplicate \\section headings (e.g. "Figures" rendered twice) are flagged
    from the compiled manuscript .tex.

    \b
    Example:
        $ scitex-writer check-references
        $ scitex-writer check-references --log
    """
    from ... import checks

    result = checks.references(project, doc_type=doc_type, parse_log=parse_log)
    if as_json:
        _emit_json(result)
        return 0 if result.get("success") else 1
    out = (result.get("stdout") or "").rstrip()
    if out:
        click.echo(out)
    err = (result.get("stderr") or "").rstrip()
    if err:
        click.echo(err, err=True)
    return result.get("exit_code", 0)


# EOF
