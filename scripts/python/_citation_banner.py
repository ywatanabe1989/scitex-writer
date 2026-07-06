#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/python/_citation_banner.py
# Purpose: The citation-gate BANNER render layer. When the gate runs in `banner`
#          mode (compile-anyway, accepted-risk draft), it emits a red page-1
#          "unverified citations" box as a LaTeX artifact; the flattener
#          (compile_tex_structure.py) injects that artifact after
#          \begin{document} (before \maketitle) when it exists. Kept separate
#          from check_citations.py so the detect/classify gate logic and the
#          LaTeX-generation responsibility live in focused modules.
#
# Self-contained: stdlib only.

from pathlib import Path

# Where the banner-mode compile artifact is written, relative to the project
# root. The flattener derives the same path from its resolved project root.
_BANNER_TEX = ".scitex/writer/.citation_banner.tex"


def banner_tex_path(project_dir):
    """Absolute path of the banner-mode compile artifact for this project."""
    return Path(project_dir) / _BANNER_TEX


def reset_banner(project_dir):
    """Remove any stale banner artifact so a clean run never re-injects it."""
    try:
        banner_tex_path(project_dir).unlink()
    except OSError:
        pass


def _latex_escape(s):
    r"""Escape the LaTeX specials that can appear in a cite key / reason."""
    out = []
    for ch in str(s):
        if ch in "&%$#_{}":
            out.append("\\" + ch)
        elif ch == "~":
            out.append(r"\textasciitilde{}")
        elif ch == "^":
            out.append(r"\textasciicircum{}")
        elif ch == "\\":
            out.append(r"\textbackslash{}")
        else:
            out.append(ch)
    return "".join(out)


def build_banner_tex(failing, clew_unreachable=False):
    r"""Return the LaTeX for a red page-1 "unverified citations" banner.

    ``failing`` is a list of (key, reason) tuples. When ``clew_unreachable`` is
    set, a prominent "clew UNREACHABLE" line is added so a down verifier never
    silently passes. Uses tcolorbox + xcolor (already preamble dependencies).
    Self-contained (\begingroup..\endgroup) and safe to inject verbatim.
    """
    lines = []
    a = lines.append
    a("% scitex-writer citation banner (auto-generated in banner mode; do not edit)")
    a(r"\begingroup")
    a(r"\definecolor{scitexBannerRed}{HTML}{C0271A}")
    a(
        r"\noindent\begin{tcolorbox}[colback=scitexBannerRed!10,"
        r"colframe=scitexBannerRed,boxrule=1.2pt,arc=1pt,left=6pt,right=6pt,"
        r"top=4pt,bottom=4pt,width=\textwidth,before skip=0pt,after skip=8pt]"
    )
    a(
        r"{\bfseries\color{scitexBannerRed}\large UNVERIFIED CITATIONS "
        r"---\ NOT FOR SUBMISSION}\\[2pt]"
    )
    if clew_unreachable:
        a(
            r"{\bfseries\color{scitexBannerRed}\small clew verification "
            r"UNREACHABLE --- citations NOT verified.}\\[2pt]"
        )
    if failing:
        a(
            r"{\small The following cited reference(s) are unresolved/unverified "
            r"and must be fixed before submission:}\\[2pt]"
        )
        a(r"{\small\ttfamily%")
        for i, (key, reason) in enumerate(failing):
            sep = r"\\" if i < len(failing) - 1 else ""
            a(
                "\\mbox{"
                + _latex_escape(key)
                + "} --- "
                + _latex_escape(reason)
                + sep
            )
        a(r"}")
    a(r"\end{tcolorbox}")
    a(r"\endgroup")
    return "\n".join(lines) + "\n"


def write_banner_tex(project_dir, failing, clew_unreachable=False):
    """Write the banner artifact and return its path (creating parent dirs)."""
    path = banner_tex_path(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(build_banner_tex(failing, clew_unreachable), encoding="utf-8")
    return path


__all__ = [
    "banner_tex_path",
    "reset_banner",
    "build_banner_tex",
    "write_banner_tex",
]
