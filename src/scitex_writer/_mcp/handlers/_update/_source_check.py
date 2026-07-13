#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Say WHICH scitex-writer the engine is being vendored FROM, and refuse if stale.

`update-project` vendors from the **installed** package. So an agent running an
old scitex-writer vendors an OLD engine — and update-project reports success. The
project ends up carrying bugs the fleet has already fixed, and nothing anywhere
says so. That is the same silent-wrong-answer class this engine exists to prevent,
sitting inside the very command we hand people to fix it.

It is not hypothetical: on 2026-07-14 both neurovista and paper-scitex-clew were
told to run `update-project`. Their installed writer was 2.29.0 while 2.32.1 was
current. Running it verbatim would have quietly vendored 2.29.0 while they
reported "done". paper-scitex-clew caught it by hand and asked for this guard.

So: when we can PROVE the vendor source is outdated, refuse and hand back the
command that fixes it. When we cannot reach PyPI, proceed — but SAY we could not
check, rather than let silence read as "you are current".
"""

import json
import urllib.request
from typing import Optional

PYPI_URL = "https://pypi.org/pypi/scitex-writer/json"


def latest_on_pypi(timeout: float = 3.0) -> Optional[str]:
    """Newest published scitex-writer, or None if we could not ask.

    None means "unknown", never "you are up to date" — the caller must not
    collapse the two.
    """
    try:
        with urllib.request.urlopen(PYPI_URL, timeout=timeout) as resp:
            return json.load(resp)["info"]["version"]
    except Exception:
        return None


def _parts(version: str):
    out = []
    for chunk in version.split("."):
        digits = "".join(c for c in chunk if c.isdigit())
        out.append(int(digits) if digits else 0)
    return tuple(out)


def is_older(installed: str, latest: str) -> bool:
    """True when `installed` is strictly behind `latest`."""
    try:
        from packaging.version import Version

        return Version(installed) < Version(latest)
    except Exception:
        return _parts(installed) < _parts(latest)


def outdated_source_error(installed: str, latest: str) -> str:
    """The refusal, with the command that actually fixes it."""
    return (
        f"REFUSING TO VENDOR A STALE ENGINE.\n"
        f"\n"
        f"  update-project vendors from the INSTALLED scitex-writer, and yours "
        f"is out of date:\n"
        f"      installed (the vendor source): {installed}\n"
        f"      latest on PyPI:                {latest}\n"
        f"\n"
        f"  Running it now would copy the {installed} engine into your project "
        f"and report success.\n"
        f"  You would carry bugs that are already fixed, and nothing would say so.\n"
        f"\n"
        f"  Upgrade first, then re-run:\n"
        f"      uv pip install -U 'scitex-writer[all]'\n"
        f"      scitex-writer update-project\n"
        f"\n"
        f"  To vendor from the old version anyway, pass allow_outdated=True "
        f"(CLI: --allow-outdated)."
    )


def source_report(installed: str) -> dict:
    """Describe the vendor source. Never claims currency it has not verified."""
    latest = latest_on_pypi()
    if latest is None:
        return {
            "source_version": installed,
            "latest_version": None,
            "is_outdated": None,
            "source_note": (
                f"Vendoring from the INSTALLED scitex-writer {installed}. "
                f"Could not reach PyPI, so whether a newer engine exists is "
                f"UNKNOWN — this is not a statement that you are current."
            ),
        }
    outdated = is_older(installed, latest)
    return {
        "source_version": installed,
        "latest_version": latest,
        "is_outdated": outdated,
        "source_note": (
            f"Vendoring from the INSTALLED scitex-writer {installed} "
            f"(latest on PyPI: {latest})."
        ),
    }
