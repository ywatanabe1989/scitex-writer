#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_utils/_latexdiff.py

r"""The ONE latexdiff backend, plus the diff-document signature block.

``process_diff.sh`` resolved ``latexdiff`` through a three-rung cascade (native
-> TeXLive module -> Apptainer container) in ``command_switching.src``. Only the
NATIVE rung is portable and verifiable; the other two silently produced either an
un-runnable command string or nothing at all, and the caller could not tell which.
This module keeps the native rung and FAILS LOUD with an install hint otherwise --
an empty or missing diff PDF is a wrong answer, not a degraded one.

The latexdiff invocation is the shell's, flag for flag::

    latexdiff --encoding=utf8 --type=UNDERLINE --disable-citation-markup \
              --append-safecmd=cite,cite,citet OLD.tex NEW.tex > DIFF.tex

:func:`add_signature` ports ``add_diff_signature.sh``: a metadata comment block
plus a ``fancyhdr`` page style, both inserted immediately before
``\begin{document}``. One hardening: the shell typeset a literal ``U+2192`` arrow
inside ``\fancyhead``; this emits ``$\rightarrow$``, which renders identically and
cannot blow up on a preamble whose Unicode setup differs from the compiled
manuscript's.
"""

from __future__ import annotations

import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

# latexdiff/perl noise that says nothing about the diff itself (the shell grepped
# these out of stderr, and so do we -- they are not failures).
_NOISE = ("gocryptfs not found", "Wide character in print")

BEGIN_DOCUMENT = "\\begin{document}"


class LatexdiffUnavailableError(RuntimeError):
    """Raised when ``latexdiff`` is not installed (fail loud, never no-op)."""


class LatexdiffFailedError(RuntimeError):
    """Raised when ``latexdiff`` ran but produced no usable diff document."""


def require_latexdiff() -> str:
    """Return the absolute path of ``latexdiff``, or raise with an install hint."""
    binary = shutil.which("latexdiff")
    if binary is None:
        raise LatexdiffUnavailableError(
            "latexdiff not found on PATH. It is REQUIRED to build the version-diff "
            "PDF -- there is no in-repo substitute, and emitting an unmarked PDF "
            "would misreport 'no changes'. Fix: install it (Debian/Ubuntu: "
            "`apt-get install latexdiff`; TeX Live: `tlmgr install latexdiff`), or "
            "skip the diff stage."
        )
    return binary


def _clean_stderr(text: str) -> str:
    """Drop the known-noise lines the shell filtered out of latexdiff's stderr."""
    lines = [
        line
        for line in (text or "").splitlines()
        if line.strip() and not any(noise in line for noise in _NOISE)
    ]
    return "\n".join(lines)


def run_latexdiff(old_tex: Path, new_tex: Path, out_tex: Path) -> Path:
    """Write the latexdiff of ``old_tex`` -> ``new_tex`` to ``out_tex``.

    Raises :class:`LatexdiffUnavailableError` when the binary is missing, and
    :class:`LatexdiffFailedError` when it fails or yields an empty document (the
    shell warned and carried on -- leaving a stale PDF to be mistaken for fresh).
    """
    binary = require_latexdiff()
    proc = subprocess.run(
        [
            binary,
            "--encoding=utf8",
            "--type=UNDERLINE",
            "--disable-citation-markup",
            "--append-safecmd=cite,cite,citet",
            str(old_tex),
            str(new_tex),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    stderr = _clean_stderr(proc.stderr)
    if proc.returncode != 0:
        raise LatexdiffFailedError(
            f"latexdiff exited {proc.returncode} comparing {old_tex} -> {new_tex}"
            + (f": {stderr}" if stderr else "")
        )
    if not proc.stdout.strip():
        raise LatexdiffFailedError(
            f"latexdiff produced an EMPTY document for {old_tex} -> {new_tex}"
            + (f": {stderr}" if stderr else "")
            + ". The inputs are probably not standalone LaTeX documents."
        )
    out_tex.parent.mkdir(parents=True, exist_ok=True)
    out_tex.write_text(proc.stdout, encoding="utf-8")
    return out_tex


def _signature_comment(
    old_version: str,
    new_version: str,
    doc_type: str,
    author: str,
    email: str,
    commit: str,
    branch: str,
    stamp: str,
) -> str:
    """The ``%%``-comment metadata block (never typeset; the arrow is safe here)."""
    rule = "%% " + "=" * 77
    return "\n".join(
        [
            "",
            rule,
            "%% Diff Document Metadata (Auto-generated)",
            rule,
            f"%% Comparison: v{old_version} → v{new_version}",
            f"%% Generated: {stamp}",
            f"%% User: {author} <{email}>",
            f"%% Document: {doc_type}",
            f"%% Git commit: {commit}",
            f"%% Git branch: {branch}",
            rule,
            "",
        ]
    )


def _signature_preamble(
    old_version: str, new_version: str, doc_type: str, author: str, stamp: str
) -> str:
    """The ``fancyhdr`` page style stamped onto every page of the diff PDF."""
    return "\n".join(
        [
            "\\usepackage{fancyhdr}",
            "\\usepackage{lastpage}",
            "",
            "\\fancypagestyle{diffstyle}{",
            "    \\fancyhf{}",
            "    \\renewcommand{\\headrulewidth}{0.4pt}",
            "    \\renewcommand{\\footrulewidth}{0.4pt}",
            "    \\fancyhead[L]{\\small\\textit{Diff: v"
            f"{old_version}" + " $\\rightarrow$ v" + f"{new_version}" + "}}",
            f"    \\fancyhead[R]{{\\small\\textit{{{doc_type}}}}}",
            f"    \\fancyfoot[L]{{\\small Generated: {stamp}}}",
            "    \\fancyfoot[C]{\\small Page \\thepage\\ of \\pageref{LastPage}}",
            f"    \\fancyfoot[R]{{\\small {author}}}",
            "}",
            "",
            "\\AtBeginDocument{\\pagestyle{diffstyle}}",
            "",
        ]
    )


def add_signature(
    diff_tex: Path,
    old_version: str,
    new_version: str,
    doc_type: str = "manuscript",
    author: str = "unknown",
    email: str = "unknown",
    commit: str = "unknown",
    branch: str = "unknown",
    now: Optional[datetime] = None,
) -> Path:
    """Stamp the metadata comment + ``fancyhdr`` style into ``diff_tex`` in place.

    Both blocks land immediately before the FIRST ``\\begin{document}``. A diff
    document with no ``\\begin{document}`` is not a compilable document, so this
    raises instead of writing an unusable file (the shell silently skipped the
    preamble half and left the comment half behind).
    """
    text = diff_tex.read_text(encoding="utf-8")
    if BEGIN_DOCUMENT not in text:
        raise LatexdiffFailedError(
            f"{diff_tex} carries no {BEGIN_DOCUMENT} -- it is not a standalone "
            "LaTeX document and cannot be compiled into a diff PDF."
        )
    stamp = (now or datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    comment = _signature_comment(
        old_version, new_version, doc_type, author, email, commit, branch, stamp
    )
    preamble = _signature_preamble(
        old_version, new_version, doc_type, author, stamp[:16]
    )
    head, sep, tail = text.partition(BEGIN_DOCUMENT)
    diff_tex.write_text(
        head + comment + preamble + sep + tail,
        encoding="utf-8",
    )
    return diff_tex


__all__ = [
    "BEGIN_DOCUMENT",
    "LatexdiffFailedError",
    "LatexdiffUnavailableError",
    "add_signature",
    "require_latexdiff",
    "run_latexdiff",
]

# EOF
