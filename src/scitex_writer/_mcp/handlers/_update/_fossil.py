#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_mcp/handlers/_update/_fossil.py

"""Neutralise scaffolding debris that impersonates a version marker.

A project is scaffolded by copying the template repo, which brings the ENGINE's
``CHANGELOG.md`` along. That file is in no sync list (see ``_constants.py``:
only ``scripts/``, ``compile.sh`` and a few named engine paths refresh), so it
freezes at the version the project was created on while everything around it
keeps updating. The gap widens with every release.

That would be harmless debris except for one thing: **it names a version**, so
it reads as authoritative. A real tree stamped 2.24.7 carried a changelog whose
top entry said 2.9.0, and a reader (me, 2026-07-14) reported the engine four
months stale to the whole fleet on its authority.

The fix is not to refresh it -- the engine's changelog already has an
authoritative home on GitHub, and copying it into every paper repo would give
one fact two places to live (constitution SSoT). Instead the vendored copy is
replaced by a pointer to the real one, so the tree stops carrying a second,
lying answer to "what version is this?".

Identification is by CONTENT, never by path: ``project_path`` is normally the
vendored engine tree (``<repo>/.scitex/writer/``), but in a directly-scaffolded
layout a ``CHANGELOG.md`` at that path could be the AUTHOR's own. We only touch
a file we can positively recognise as the engine's, and leave anything else
alone.
"""

from __future__ import annotations

from pathlib import Path

CHANGELOG_PATH = "CHANGELOG.md"
CHANGELOG_URL = "https://github.com/ywatanabe1989/scitex-writer/blob/main/CHANGELOG.md"
VENDOR_STAMP_NAME = "00_shared/.scitex-writer-vendored-version"


def is_engine_changelog(text: str) -> bool:
    """True only for a file we can positively identify as the engine's changelog.

    Deliberately strict. A false positive here overwrites an author's own
    CHANGELOG.md, so anything we cannot recognise is left untouched.
    """
    head = text[:400]
    if not head.lstrip().startswith("# Changelog"):
        return False
    return "SciTeX Writer" in head


def pointer_text(pkg_version: str) -> str:
    """The replacement: says what this tree is, and where the real log lives."""
    return (
        f"# Changelog — not here\n"
        f"\n"
        f"This is a **vendored scitex-writer engine tree**, not the engine's\n"
        f"repository. It used to carry a copy of the engine's CHANGELOG.md that\n"
        f"was written once when this project was scaffolded and never refreshed\n"
        f"again — so it kept naming the version you started on, long after the\n"
        f"engine had moved on. It read as authoritative and was not.\n"
        f"\n"
        f"The engine's changelog lives at:\n"
        f"\n"
        f"    {CHANGELOG_URL}\n"
        f"\n"
        f"The version THIS tree was vendored from is recorded in:\n"
        f"\n"
        f"    {VENDOR_STAMP_NAME}\n"
        f"\n"
        f"which `scitex-writer update-project` rewrites on every vendor, and\n"
        f"which the compile-time freshness gate reads. That file is the single\n"
        f'answer to "what engine is this project on?" — at the time of writing,\n'
        f"{pkg_version}.\n"
    )


def neutralise_fossil_changelog(
    project_path: Path, pkg_version: str, dry_run: bool = False
) -> bool:
    """Replace a recognisable engine CHANGELOG fossil with a pointer.

    Returns True when the file was (or would be) replaced. Does nothing and
    returns False when the file is absent, already a pointer, or not
    recognisable as the engine's changelog -- the last case matters, because in
    a directly-scaffolded layout this path could be the AUTHOR's own changelog,
    and overwriting that would be far worse than the fossil.

    Not best-effort-silent: an OSError here is a real failure to fix a known
    lying marker, and the caller reports the outcome either way.
    """
    target = project_path / CHANGELOG_PATH
    if not target.is_file():
        return False
    text = target.read_text(encoding="utf-8", errors="replace")
    if not is_engine_changelog(text):
        return False
    if not dry_run:
        target.write_text(pointer_text(pkg_version), encoding="utf-8")
    return True
