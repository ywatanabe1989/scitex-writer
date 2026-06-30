#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/check_version_freshness.py
# Purpose: Pre-compile VERSION-FRESHNESS gate. Fails loud when the VENDORED
#          engine tree is STALE relative to the installed scitex-writer.
#
#          Incident (2026-06-30): consumers silently compiled with a vendored
#          engine 11 minor versions behind (2.13.4 vs 2.24.0) -- reintroducing
#          already-fixed bugs and shipping deficient PDFs, with no signal. A
#          one-off "please upgrade" broadcast is vigilance, not a mechanism;
#          this is the mechanism (constitution §2 fail-loud, §3 durable).
#
#          Signal: update-project stamps the version it vendored FROM into
#          00_shared/.scitex-writer-vendored-version (compile-immutable; NOT
#          scitex_writer_version.tex, which the compile rewrites from the
#          installed version for PDF metadata). This gate compares that stamp
#          to the installed scitex_writer.__version__:
#            vendored < installed -> FAIL (re-vendor available, clearly stale)
#            stamp absent          -> WARN (pre-feature vendor; re-vendor to arm)
#            not installed / equal -> pass (can't prove stale, or current)
#          Optional --check-pypi adds an installed-vs-PyPI-latest WARN (network;
#          off by default to keep the compile offline-safe).
#
#          Severity (SCITEX_WRITER_VERSION_FRESHNESS / --level / config),
#          default error. The "stale" FAIL gates at the resolved level; the
#          soft cases (absent stamp, not installed) always warn, never block.
#
# Usage:
#   python check_version_freshness.py [project_dir] [--level off|warn|error]
#       [--installed X.Y.Z]  (override; default = scitex_writer.__version__)
#       [--check-pypi]
#
# Self-contained: stdlib + optional PyYAML (config).

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _severity import resolve_level  # noqa: E402

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
DIM = "\033[0;90m"
BOLD = "\033[1m"
NC = "\033[0m"

PASS_COUNT = 0
WARN_COUNT = 0
FAIL_COUNT = 0

_LEVELS = ("off", "warn", "error")

VENDOR_STAMP = "00_shared/.scitex-writer-vendored-version"


def log_pass(msg):
    global PASS_COUNT
    print(f"  {GREEN}[PASS]{NC} {msg}")
    PASS_COUNT += 1


def log_warn(msg):
    global WARN_COUNT
    print(f"  {YELLOW}[WARN]{NC} {msg}")
    WARN_COUNT += 1


def log_fail(msg):
    global FAIL_COUNT
    print(f"  {RED}[FAIL]{NC} {msg}")
    FAIL_COUNT += 1


def log_detail(msg):
    print(f"    {DIM}{msg}{NC}")


def version_tuple(s):
    """Leading numeric components of a version string, e.g. '2.24.0rc1' ->
    (2, 24, 0). Returns None if no leading number is found."""
    if not s:
        return None
    parts = []
    for chunk in str(s).strip().split("."):
        m = re.match(r"\d+", chunk)
        if not m:
            break
        parts.append(int(m.group()))
    return tuple(parts) if parts else None


def read_vendor_stamp(project_dir):
    """Version this tree was vendored from (first line of the stamp), or None."""
    stamp = Path(project_dir) / VENDOR_STAMP
    if not stamp.exists():
        return None
    try:
        for line in stamp.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    except OSError:
        return None
    return None


def installed_version():
    """Installed scitex_writer.__version__, or None if not importable."""
    try:
        import scitex_writer

        return getattr(scitex_writer, "__version__", None)
    except Exception:
        return None


def pypi_latest(timeout=3):
    """Latest scitex-writer version on PyPI (best-effort), or None."""
    try:
        import json
        import urllib.request

        with urllib.request.urlopen(
            "https://pypi.org/pypi/scitex-writer/json", timeout=timeout
        ) as resp:
            return json.load(resp).get("info", {}).get("version")
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Pre-compile version-freshness gate: fail loud when the "
        "vendored engine is stale vs the installed scitex-writer."
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument("--level", choices=list(_LEVELS), default=None)
    parser.add_argument("--installed", default=None, help="override installed version")
    parser.add_argument(
        "--check-pypi", action="store_true", help="also warn if behind PyPI latest"
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    level = resolve_level(
        "version_freshness",
        args.level,
        project_dir,
        default="error",
        env_var="SCITEX_WRITER_VERSION_FRESHNESS",
    )

    print(f"\n{BOLD}=== Version Freshness Gate (level={level}) ==={NC}\n")
    if level == "off":
        print(f"  {DIM}[INFO]{NC} version-freshness gate disabled (level=off).")
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0

    report = log_fail if level == "error" else log_warn

    vendored = read_vendor_stamp(project_dir)
    installed = args.installed or installed_version()

    vt, it = version_tuple(vendored), version_tuple(installed)

    if installed is None:
        log_warn(
            "scitex-writer is not importable here -- cannot compare versions "
            "(compile uses the vendored scripts; install scitex-writer to verify)."
        )
    elif vendored is None:
        log_warn(
            "no vendor stamp (00_shared/.scitex-writer-vendored-version) -- this "
            f"tree predates the freshness stamp; re-vendor to arm it (installed "
            f"{installed})."
        )
        log_detail("fix: scitex-writer update-project <project_dir>")
    elif vt is not None and it is not None and vt < it:
        report(
            f"vendored engine {vendored} is STALE vs installed {installed} -- "
            f"re-vendor before compiling (stale engines reintroduce fixed bugs)."
        )
        log_detail("fix: scitex-writer update-project <project_dir>")
    else:
        log_pass(f"vendored {vendored} is current vs installed {installed}")

    if args.check_pypi and installed is not None:
        latest = pypi_latest()
        lt = version_tuple(latest)
        if lt is not None and it is not None and it < lt:
            log_warn(
                f"installed scitex-writer {installed} is behind PyPI latest "
                f"{latest} -- pip install -U scitex-writer."
            )

    print()
    print(
        f"{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )
    return 1 if FAIL_COUNT > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
