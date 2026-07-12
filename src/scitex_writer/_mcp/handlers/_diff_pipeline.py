#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_diff_pipeline.py

r"""The diff pipeline: a pure-Python port of ``process_diff.sh``.

Ports the shell module (plus the ``add_diff_signature.sh`` it sourced) stage for
stage, reading the SAME config keys the shell read via ``yq`` out of
``config/config_<doc_type>.yaml``: ``paths.compiled_tex``, ``paths.diff_tex``,
``paths.diff_pdf`` and ``paths.doc_log_dir``.

Stages (``process`` runs them in order):

1. ``resolve_versions``  -- pick the OLD commit (explicit ``diff_from``, else the
                            previous commit that touched the compiled ``.tex``)
                            and the NEW label (``HEAD``, ``+``-suffixed when the
                            tree is dirty).
2. ``take_diff_tex``     -- extract the OLD ``.tex`` from git, run the ONE
                            latexdiff backend, stamp the signature block.
3. ``compile_diff_tex``  -- compile with the ONE latexmk backend into the log dir,
                            bounded by a timeout (latexdiff markup can send
                            latexmk into an endless rerun loop).
4. ``collect_pdf``       -- move the PDF out of the log dir onto ``diff_pdf``.

Three shell behaviours this port deliberately CHANGES. Each replaced a SILENT
degradation, never a working path:

* NO previous version in git history is now an ERROR. The shell warned, then set
  ``previous_tex`` to the CURRENT tex and compiled "current vs current" -- a PDF
  with zero diff markup, indistinguishable from "nothing changed since the last
  version". A reviewer cannot tell those apart, so we refuse to emit it.
* ONE latexdiff backend and ONE compile backend (``latexdiff`` / ``latexmk``),
  each fail-loud with an install hint. The shell resolved both through a
  native/module/container cascade whose lower rungs silently emitted un-runnable
  command strings, and its engine switch defaulted an unknown engine to latexmk
  with a warning nobody reads.
* A failed compile no longer leaves a stale PDF behind, and a compile that
  reports success but writes no PDF is an error rather than a shrug.

Robust by construction: pathlib only; every write target is resolved and asserted
to live INSIDE the project root; fail-loud (explicit error dict + actionable hint)
on a missing project dir / config / binary.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Optional, Tuple

from ..._dataclasses import DiffResult
from ..._utils import _git
from ..._utils._latexdiff import add_signature, run_latexdiff
from ..._utils._latexmk import DEFAULT_TIMEOUT_SEC, compile_tex
from ..utils import resolve_project_path
from ._engine_paths import DOC_DIRS, load_doc_config, resolve_paths

_CFG_KEYS = {
    "compiled_tex": ("paths", "compiled_tex"),
    "diff_tex": ("paths", "diff_tex"),
    "diff_pdf": ("paths", "diff_pdf"),
    "log_dir": ("paths", "doc_log_dir"),
}


def resolve_versions(
    project_path: Path, compiled_tex: Path, diff_from: Optional[str]
) -> Tuple[str, str, str]:
    """Return ``(old_commit, old_hash, new_label)`` for the two versions to compare.

    ``old_commit`` is what git is asked to ``show``; ``old_hash`` is its 7-char
    display form; ``new_label`` is HEAD's short hash, suffixed with ``+`` when the
    working tree carries uncommitted changes (the shell's convention).

    Raises ValueError -- never falls back to "current vs current" -- when there is
    no OLD version to compare against.
    """
    if not _git.has_commits(project_path):
        raise ValueError(
            f"{project_path} is not a git repository with commits. The diff "
            "pipeline reads the previous version of the manuscript from git "
            "history. Fix: `git init` and commit the compiled .tex at least once."
        )

    rel_tex = str(compiled_tex.relative_to(project_path.resolve()))

    if diff_from:
        old_hash = _git.short_hash(project_path, diff_from)
        if old_hash is None:
            raise ValueError(
                f"diff_from '{diff_from}' does not resolve to a commit in "
                f"{project_path}. Fix: pass a commit-ish that exists "
                "(`git log --oneline`)."
            )
        old_commit = diff_from
    else:
        old_commit = _git.previous_commit(project_path, rel_tex)
        if old_commit is None:
            raise ValueError(
                f"No PREVIOUS version of {rel_tex} in git history (it has at most "
                "one commit). Refusing to diff the file against itself: the result "
                "would be an unmarked PDF that looks exactly like 'nothing "
                "changed'. Fix: commit a second revision, or pass an explicit "
                "diff_from commit."
            )
        old_hash = _git.short_hash(project_path, old_commit)

    new_label = _git.short_hash(project_path, "HEAD") or "HEAD"
    if not _git.is_clean(project_path):
        new_label += "+"
    return old_commit, old_hash, new_label


def take_diff_tex(
    project_path: Path,
    compiled_tex: Path,
    diff_tex: Path,
    old_commit: str,
    old_hash: str,
    new_label: str,
    doc_type: str,
) -> Path:
    """Stage 2: latexdiff the OLD tex (from git) against the CURRENT one, + signature.

    The old version is materialised into a temp file, exactly as the shell did --
    latexdiff takes two paths, not two streams -- and the temp file is always
    removed, including on failure.
    """
    rel_tex = str(compiled_tex.relative_to(project_path.resolve()))
    old_text = _git.show_file(project_path, old_commit, rel_tex)
    if old_text is None:
        raise ValueError(
            f"{rel_tex} does not exist at commit {old_hash}. Fix: pass a "
            "diff_from commit in which the compiled .tex was already tracked."
        )

    handle = tempfile.NamedTemporaryFile(
        "w", suffix=".tex", delete=False, encoding="utf-8"
    )
    old_tex = Path(handle.name)
    try:
        handle.write(old_text)
        handle.close()
        run_latexdiff(old_tex, compiled_tex, diff_tex)
    finally:
        old_tex.unlink(missing_ok=True)

    add_signature(
        diff_tex,
        old_hash,
        new_label,
        doc_type=doc_type,
        author=_git.user_name(project_path),
        email=_git.user_email(project_path),
        commit=_git.short_hash(project_path, "HEAD") or "unknown",
        branch=_git.current_branch(project_path),
    )
    return diff_tex


def collect_pdf(built_pdf: Path, diff_pdf: Path) -> int:
    """Stage 4: move the compiled PDF out of the log dir onto ``diff_pdf``.

    Returns its size in bytes. An empty PDF is an error, not a result.
    """
    diff_pdf.parent.mkdir(parents=True, exist_ok=True)
    diff_pdf.unlink(missing_ok=True)
    built_pdf.replace(diff_pdf)
    size = diff_pdf.stat().st_size
    if size == 0:
        raise ValueError(f"{diff_pdf} was written but is EMPTY (0 bytes).")
    return size


def process(
    project_dir: str,
    doc_type: str = "manuscript",
    no_diff: bool = False,
    diff_from: Optional[str] = None,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
) -> dict:
    """Build and compile the version-diff PDF for ``doc_type``.

    Parameters
    ----------
    project_dir : str
        Path to the scitex-writer project directory (must be a git repository).
    doc_type : str
        One of 'manuscript' (default), 'supplementary', 'revision'.
    no_diff : bool
        Skip the whole pipeline (the shell's ``--no_diff``).
    diff_from : str, optional
        Commit-ish to diff FROM. Default: the previous commit that touched the
        compiled ``.tex`` (the shell's ``SCITEX_DIFF_FROM``).
    timeout_sec : int
        Bound on the latexmk run (the shell's ``SCITEX_WRITER_DIFF_TIMEOUT``).

    Returns
    -------
    dict
        The serialized :class:`DiffResult`. On failure ``error`` carries an
        actionable hint (fail-loud, never a silent no-op).
    """
    try:
        if no_diff:
            return DiffResult(success=True, skipped=True).to_dict()

        if doc_type not in DOC_DIRS:
            return {
                "success": False,
                "error": (
                    f"Invalid doc_type '{doc_type}'. Must be one of: {tuple(DOC_DIRS)}"
                ),
            }

        project_path = resolve_project_path(project_dir)
        if not project_path.is_dir():
            return {
                "success": False,
                "error": (
                    f"Project directory not found: {project_path}. "
                    f"Check the path passed as project_dir."
                ),
            }

        cfg, error = load_doc_config(project_path, doc_type)
        if error:
            return {"success": False, "error": error}
        paths, error = resolve_paths(project_path, cfg, _CFG_KEYS, "paths")
        if error:
            return {"success": False, "error": error}

        compiled_tex = paths["compiled_tex"]
        if not compiled_tex.is_file():
            return {
                "success": False,
                "error": (
                    f"Compiled TeX not found: {compiled_tex}. The diff is taken "
                    "against the compiled manuscript. Fix: run "
                    "`scitex-writer compile manuscript` first."
                ),
            }

        old_commit, old_hash, new_label = resolve_versions(
            project_path, compiled_tex, diff_from
        )
        diff_tex = take_diff_tex(
            project_path,
            compiled_tex,
            paths["diff_tex"],
            old_commit,
            old_hash,
            new_label,
            doc_type,
        )
        try:
            built_pdf = compile_tex(
                diff_tex,
                paths["log_dir"],
                project_root=project_path,
                timeout_sec=timeout_sec,
            )
        except Exception:
            # Drop the PREVIOUS run's PDF: a stale diff_pdf sitting beside a failed
            # compile is read as a fresh one (the shell's own `rm -f` on failure).
            paths["diff_pdf"].unlink(missing_ok=True)
            raise
        pdf_bytes = collect_pdf(built_pdf, paths["diff_pdf"])

        result = DiffResult(
            success=True,
            from_hash=old_hash,
            to_hash=new_label,
            diff_tex=str(diff_tex),
            diff_pdf=str(paths["diff_pdf"]),
            pdf_bytes=pdf_bytes,
        )
        result.validate()
        return result.to_dict()
    except Exception as e:
        return {"success": False, "error": f"{type(e).__name__}: {e}"}


__all__ = ["collect_pdf", "process", "resolve_versions", "take_diff_tex"]

# EOF
