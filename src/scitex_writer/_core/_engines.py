#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_core/_engines.py

"""LaTeX compilation-engine detection.

Pure-Python port of ``scripts/shell/modules/select_compilation_engine.sh``'s
detection/verification/listing logic (``auto_detect_engine`` /
``verify_engine`` / ``get_engine_info`` / ``get_engine_version`` /
``list_available_engines``). The compile pipeline itself still shells out to
that bash module today -- this port is additive (the ``list-engines``
introspection verb), not yet wired into the live compile path; swapping the
pipeline's own detection call is a separate, compile-tested slice.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess

#: Engine name -> (human description, binaries required to run it).
_ENGINE_BINARIES: dict[str, tuple[str, tuple[str, ...]]] = {
    "tectonic": ("Tectonic (Reproducible, 4-5s per compile)", ("tectonic",)),
    "latexmk": ("latexmk (Smart incremental, 3s)", ("latexmk", "pdflatex")),
    "3pass": ("3-pass (Guaranteed correctness, 6-7s)", ("pdflatex", "bibtex")),
}

#: Default auto-detect priority order (fastest-for-dev first, guaranteed last).
DEFAULT_AUTO_ORDER: tuple[str, ...] = ("latexmk", "tectonic", "3pass")

#: Regex to pull a dotted version number out of a `--version`/`-version` banner.
_VERSION_RE = re.compile(r"\d+\.\d+(?:\.\d+)?")


def verify_engine(engine: str) -> bool:
    """True if every binary ``engine`` needs is on ``PATH``."""
    binaries = _ENGINE_BINARIES.get(engine, (None, ()))[1]
    return bool(binaries) and all(shutil.which(b) for b in binaries)


def auto_detect_engine(order: tuple[str, ...] | None = None) -> str:
    """First verified engine in ``order`` (default: env override or the
    latexmk/tectonic/3pass priority), falling back to ``3pass`` (assumed
    always installed alongside a LaTeX distribution)."""
    if order is None:
        env_order = os.environ.get("SCITEX_WRITER_AUTO_ORDER")
        order = tuple(env_order.split()) if env_order else DEFAULT_AUTO_ORDER
    for engine in order:
        if verify_engine(engine):
            return engine
    return "3pass"


def get_engine_info(engine: str) -> str:
    """Human-readable one-line description of ``engine`` (empty if unknown)."""
    return _ENGINE_BINARIES.get(engine, ("", ()))[0]


def get_engine_version(engine: str) -> str | None:
    """The installed version string for ``engine``, or None if unavailable /
    unparseable. ``3pass`` has no single version (it's pdflatex+bibtex) so it
    reports the fixed token ``"native"``, matching the shell source."""
    if engine == "3pass":
        return "native" if verify_engine(engine) else None
    binary = {"tectonic": "tectonic", "latexmk": "latexmk"}.get(engine)
    if not binary or not shutil.which(binary):
        return None
    flag = "--version" if engine == "tectonic" else "-version"
    try:
        out = subprocess.run(
            [binary, flag], capture_output=True, text=True, timeout=5
        ).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    match = _VERSION_RE.search(out.splitlines()[0] if out else "")
    return match.group(0) if match else None


def list_available_engines() -> list[dict]:
    """Availability + version + description for every known engine, in the
    canonical order (tectonic, latexmk, 3pass -- the shell source's order)."""
    return [
        {
            "engine": engine,
            "available": verify_engine(engine),
            "version": get_engine_version(engine),
            "info": get_engine_info(engine),
        }
        for engine in ("tectonic", "latexmk", "3pass")
    ]


# EOF
