#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_utils/_latexmk.py

r"""The ONE LaTeX compile backend used by the diff pipeline: ``latexmk``.

``process_diff.sh`` picked between ``tectonic``, ``latexmk`` and a hand-rolled
3-pass ``pdflatex`` loop via ``SCITEX_WRITER_SELECTED_ENGINE``, and an unknown
value fell back to ``latexmk`` with a warning. Every rung then resolved its own
binary through ``command_switching.src``'s native/module/container cascade, so a
missing engine surfaced as a mystery non-zero exit far from its cause.

The diff document is a derived artifact, not the manuscript: it needs one
reliable engine, not three. This module keeps ``latexmk`` (the shell's default and
the only rung installed by ``scitex-writer``'s own container recipe) and fails loud
with an install hint when it is absent.

The flags are the shell's ``compile_with_latexmk``: ``-pdf -bibtex -synctex=1
-interaction=nonstopmode -file-line-error -output-directory=<log_dir> -gg``, with
``BIBINPUTS`` pointed at the project root so ``bibtex`` -- which latexmk runs from
the output directory -- still finds the bibliography.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional

DEFAULT_TIMEOUT_SEC = 120
"""The shell's ``SCITEX_WRITER_DIFF_TIMEOUT`` default: latexdiff output can send
latexmk into an endless rerun loop, so the diff compile is always bounded."""


class LatexmkUnavailableError(RuntimeError):
    """Raised when ``latexmk`` is not installed (fail loud, never no-op)."""


class LatexmkFailedError(RuntimeError):
    """Raised when ``latexmk`` ran but produced no PDF (or timed out)."""


def require_latexmk() -> str:
    """Return the absolute path of ``latexmk``, or raise with an install hint."""
    binary = shutil.which("latexmk")
    if binary is None:
        raise LatexmkUnavailableError(
            "latexmk not found on PATH. It is REQUIRED to compile the diff "
            "document. Fix: install TeX Live (Debian/Ubuntu: `apt-get install "
            "latexmk texlive-latex-extra`), or build the writer's TeX Live "
            "container with `scitex-writer containers install texlive`."
        )
    return binary


def compile_tex(
    tex_file: Path,
    output_dir: Path,
    project_root: Optional[Path] = None,
    timeout_sec: int = DEFAULT_TIMEOUT_SEC,
) -> Path:
    """Compile ``tex_file`` with latexmk into ``output_dir``; return the PDF path.

    Raises :class:`LatexmkUnavailableError` when latexmk is missing, and
    :class:`LatexmkFailedError` on a non-zero exit, a timeout, or a run that
    reported success yet produced no PDF. The caller is responsible for moving the
    PDF out of ``output_dir`` -- this function never touches anything outside it.
    """
    binary = require_latexmk()
    if not tex_file.is_file():
        raise LatexmkFailedError(f"TeX source not found: {tex_file}")
    output_dir.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    if project_root is not None:
        env["BIBINPUTS"] = f"{project_root}:"

    command = [
        binary,
        "-pdf",
        "-bibtex",
        "-synctex=1",
        "-interaction=nonstopmode",
        "-file-line-error",
        f"-output-directory={output_dir}",
        "-pdflatex=pdflatex -shell-escape %O %S",
        "-gg",
        str(tex_file),
    ]
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=str(project_root) if project_root else None,
            env=env,
            timeout=timeout_sec,
        )
    except subprocess.TimeoutExpired as exc:
        raise LatexmkFailedError(
            f"latexmk timed out after {timeout_sec}s on {tex_file.name}. "
            "latexdiff markup can drive latexmk into an endless rerun loop. "
            "Raise the bound with diff(..., timeout_sec=300)."
        ) from exc

    pdf_file = output_dir / f"{tex_file.stem}.pdf"
    if proc.returncode != 0:
        tail = "\n".join((proc.stdout or "").splitlines()[-20:])
        raise LatexmkFailedError(
            f"latexmk exited {proc.returncode} on {tex_file.name}. Last output:\n{tail}"
        )
    if not pdf_file.is_file():
        raise LatexmkFailedError(
            f"latexmk reported success but wrote no PDF at {pdf_file}."
        )
    return pdf_file


__all__ = [
    "DEFAULT_TIMEOUT_SEC",
    "LatexmkFailedError",
    "LatexmkUnavailableError",
    "compile_tex",
    "require_latexmk",
]

# EOF
