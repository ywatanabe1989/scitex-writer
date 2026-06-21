#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: src/scitex_writer/_utils/_mermaid_precheck.py

"""Crash-early dependency check for the mermaid CLI (mmdc).

Background
----------
``mmdc`` (``@mermaid-js/mermaid-cli``) drives a headless Chromium under
the hood (via puppeteer). On stock Linux hosts and inside thin
Apptainer/Singularity images, that Chromium needs a handful of shared
libraries that are NOT always present even when ``mmdc`` itself is on
PATH. The two most common failure modes we have seen in the wild:

1. ``libnspr4.so`` missing — common on minimal Linux images and inside
   Apptainer/Singularity containers built without the NSS/NSPR stack.
2. A puppeteer-launched chromium subprocess dying with SIGSEGV /
   "Aborted (core dumped)" — typically inside Apptainer where shared
   memory or sandbox flags trip the renderer.

Either failure makes ``mmdc`` exit non-zero AFTER it has already
written a half-baked / corrupted output file. The downstream LaTeX
build then either silently embeds garbage or fails much later with an
opaque error far from the real root cause.

This module fails LOUD, EARLY, with an install hint:

  >>> from scitex_writer._utils._mermaid_precheck import check_mmdc_or_raise
  >>> check_mmdc_or_raise()
  scitex_writer._utils._mermaid_precheck.MermaidDependencyError:
  mmdc is installed but cannot start: missing libnspr4. Install it
  with: sudo apt install libnspr4 libnss3
  (or rebuild your apptainer image with the NSPR/NSS libs included).

The intent: call this at the top of any entrypoint that shells out to
``mmdc`` (the mmd2png shell helper, a future python wrapper, an MCP
tool, etc.). The check is cheap (single subprocess call) and runs
exactly once per process.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import Optional


class MermaidDependencyError(RuntimeError):
    """Raised when the mermaid CLI (mmdc) cannot be invoked safely.

    Distinct from FileNotFoundError so callers can tell "user has not
    installed mmdc at all" apart from "mmdc is installed but the
    runtime environment is broken (missing libnspr4 / chromium SIGSEGV
    inside apptainer)". Inherits RuntimeError because both are runtime
    environment problems, not programmer errors.
    """


_LIBNSPR4_HINT = (
    "mmdc is installed but its headless-chromium dependency cannot "
    "start: 'libnspr4' is missing. On Debian/Ubuntu install with "
    "'sudo apt install libnspr4 libnss3'. Inside an Apptainer/"
    "Singularity image, rebuild the container with the NSPR/NSS "
    "stack baked in (libnspr4, libnss3, libatk1.0, libxcomposite1, "
    "libxdamage1, libxrandr2, libgbm1, libasound2)."
)

_SIGSEGV_HINT = (
    "mmdc crashed (SIGSEGV / Aborted) while launching its headless "
    "chromium. This is a known Apptainer/Singularity gap: the "
    "container's chromium cannot create its sandbox. Re-run mmdc "
    "with '--puppeteerConfigFile' pointing at a config that sets "
    '\'args: ["--no-sandbox", "--disable-dev-shm-usage"]\', or '
    "pull a mermaid-cli image rebuilt with the sandbox-friendly "
    "options."
)

_NOT_INSTALLED_HINT = (
    "mmdc (mermaid-cli) is not installed or not on PATH. Install "
    "with: 'npm install -g @mermaid-js/mermaid-cli' "
    "(requires node>=18). For HPC/Apptainer environments without "
    "npm, pull the prebuilt image: "
    "'apptainer pull docker://minlag/mermaid-cli:latest'."
)


def _detect_libnspr4(stderr: str) -> bool:
    return "libnspr4" in stderr or "libnspr4.so" in stderr


def _detect_apptainer_segfault(stderr: str) -> bool:
    needles = ("SIGSEGV", "Aborted", "segmentation fault", "core dumped")
    low = stderr.lower()
    return any(n.lower() in low for n in needles)


def check_mmdc_or_raise(
    mmdc_path: Optional[str] = None,
    timeout: float = 10.0,
) -> str:
    """Crash-early check that the mermaid CLI (mmdc) is actually usable.

    Parameters
    ----------
    mmdc_path:
        Override the discovered path (mainly for testing). If None,
        ``shutil.which("mmdc")`` is used.
    timeout:
        Seconds to wait for ``mmdc --version`` to return. Default 10s
        — the goal is to fail fast, not hang CI.

    Returns
    -------
    The resolved path to a working ``mmdc`` binary.

    Raises
    ------
    MermaidDependencyError
        ``mmdc`` is not on PATH, or it is on PATH but cannot start
        because of a missing system library / sandbox failure.
    """
    resolved = mmdc_path if mmdc_path is not None else shutil.which("mmdc")
    if not resolved:
        raise MermaidDependencyError(_NOT_INSTALLED_HINT)

    try:
        result = subprocess.run(
            [resolved, "--version"],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        # Race: which() saw the binary but it disappeared (or perm bits flipped).
        raise MermaidDependencyError(_NOT_INSTALLED_HINT) from exc
    except subprocess.TimeoutExpired as exc:
        raise MermaidDependencyError(
            "mmdc --version timed out after "
            f"{timeout:g}s — its headless chromium is likely hanging "
            "on a missing sandbox. " + _SIGSEGV_HINT
        ) from exc

    if result.returncode == 0:
        return resolved

    combined_err = (result.stderr or "") + (result.stdout or "")
    if _detect_libnspr4(combined_err):
        raise MermaidDependencyError(_LIBNSPR4_HINT)
    if _detect_apptainer_segfault(combined_err):
        raise MermaidDependencyError(_SIGSEGV_HINT)

    raise MermaidDependencyError(
        f"mmdc --version exited with code {result.returncode}. "
        f"stderr: {combined_err.strip() or '<empty>'}. " + _NOT_INSTALLED_HINT
    )


# EOF
