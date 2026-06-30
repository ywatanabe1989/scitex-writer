#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/check_compile_artifacts.py
# Purpose: POST-compile verification gate. Catches a FALSE-SUCCESS compile --
#          one that exits 0 but produced a DEFICIENT PDF -- and fails loud.
#
#          Motivating incident (2026-06-30): a manuscript compiled exit 0 with
#          a CLEAN log, yet embedded ZERO figures (the \includegraphics targets
#          -- jpg_for_compilation/*.jpg -- were unmaterialized .txt pointers). A
#          missing \includegraphics target emitted NO "File not found" warning,
#          so a log scan alone would NOT have caught it. The decisive check is
#          PDF-LEVEL: the compiled .tex emits N \includegraphics but the output
#          PDF embeds 0 images.
#
#          Checks (severity-gated; default error):
#            PRIMARY (log-independent): N = \includegraphics count in the
#              compiled .tex; M = embedded-image count in the PDF (pdfimages,
#              poppler). N>0 and M==0 -> FAIL; 0<M<N -> WARN. Needs poppler;
#              when absent the image check is skipped with a warning. The
#              compute env that actually compiles has poppler (e.g. Spartan via
#              `module load texlive`); a bare laptop/container may not.
#            SECONDARY (log scan): missing-graphics / "File `..' not found" /
#              "There were undefined references" / "Citation `..' undefined" in
#              the LaTeX .log. The intentional scitex self-citation NUDGE
#              ("SciTeX Writer citation not found") is NOT a trigger.
#
#          Severity precedence (highest -> lowest):
#            1. --level {off,warn,error}
#            2. env SCITEX_WRITER_COMPILE_ARTIFACTS
#            3. project ./config.yaml  compile_artifacts.level
#            4. user ~/.scitex/writer/config.yaml compile_artifacts.level
#            5. default error
#
# Usage:
#   python check_compile_artifacts.py [project_dir]
#       [--compiled-tex PATH]  (default env SCITEX_WRITER_COMPILED_TEX)
#       [--pdf PATH]           (default env SCITEX_WRITER_COMPILED_PDF)
#       [--log PATH]           (default env SCITEX_WRITER_GLOBAL_LOG_FILE)
#       [--level off|warn|error]
#
# Self-contained: stdlib + optional PyYAML (config) + optional poppler
# (pdfimages) at runtime.

import argparse
import os
import re
import shutil
import subprocess
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

# Secondary log-scan deficiency patterns. The scitex self-citation nudge is a
# stdout print (not in the .log) AND intentional -- never a trigger.
_LOG_PATTERNS = (
    (re.compile(r"File [`'][^']+' not found"), "missing file/graphic"),
    (re.compile(r"!\s*LaTeX Error: File [`'][^']+' not found"), "missing input file"),
    (re.compile(r"There were undefined references"), "undefined references"),
    (re.compile(r"Citation [`'][^']+' (?:on page .*)?undefined"), "undefined citation"),
)


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


def _strip_comments(text):
    """Drop LaTeX comments (unescaped % to EOL) so commented \\includegraphics
    and commented warnings are not counted."""
    out = []
    for line in text.split("\n"):
        m = re.search(r"(?<!\\)%", line)
        out.append(line[: m.start()] if m else line)
    return "\n".join(out)


def count_includegraphics(compiled_tex):
    """Count un-commented \\includegraphics in the compiled .tex."""
    try:
        text = Path(compiled_tex).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    return len(re.findall(r"\\includegraphics\b", _strip_comments(text)))


def count_pdf_images(pdf_path):
    """Embedded-image count via `pdfimages -list` (poppler), or None if poppler
    is unavailable / the call fails. Counts data rows (skip the 2 header lines)."""
    if shutil.which("pdfimages") is None:
        return None
    try:
        proc = subprocess.run(
            ["pdfimages", "-list", str(pdf_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    # Data rows start with "<page> <num> ...", e.g. "   1   0 image ...".
    rows = [
        ln for ln in proc.stdout.splitlines() if re.match(r"\s*\d+\s+\d+\s", ln)
    ]
    return len(rows)


def _scan_log(log_path, report):
    """Secondary: scan the LaTeX log for deficiency signals (not the self-cite
    nudge). ``report`` is log_fail or log_warn per resolved level."""
    if not log_path or not Path(log_path).exists():
        return
    try:
        text = Path(log_path).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for pattern, label in _LOG_PATTERNS:
        if pattern.search(text):
            report(f"log: {label}")


def main():
    parser = argparse.ArgumentParser(
        description="Post-compile verification gate: fail loud on a deficient "
        "PDF (figures referenced but not embedded; log deficiency signals)."
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument("--compiled-tex", default=os.environ.get("SCITEX_WRITER_COMPILED_TEX"))
    parser.add_argument("--pdf", default=os.environ.get("SCITEX_WRITER_COMPILED_PDF"))
    parser.add_argument("--log", default=os.environ.get("SCITEX_WRITER_GLOBAL_LOG_FILE"))
    parser.add_argument("--level", choices=list(_LEVELS), default=None)
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    level = resolve_level(
        "compile_artifacts",
        args.level,
        project_dir,
        default="error",
        env_var="SCITEX_WRITER_COMPILE_ARTIFACTS",
    )

    print(f"\n{BOLD}=== Compile Artifacts Gate (level={level}) ==={NC}\n")
    if level == "off":
        print(f"  {DIM}[INFO]{NC} compile-artifacts gate disabled (level=off).")
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0

    report = log_fail if level == "error" else log_warn

    # --- PRIMARY: \includegraphics (N) vs embedded images (M) ---
    n_graphics = count_includegraphics(args.compiled_tex) if args.compiled_tex else None
    if n_graphics is None:
        log_warn("could not read compiled .tex -- skipping figure-embedding check")
    elif n_graphics == 0:
        log_pass("no figures referenced (\\includegraphics count = 0)")
    else:
        m_images = count_pdf_images(args.pdf) if args.pdf else None
        if m_images is None:
            log_warn(
                f"{n_graphics} figure(s) referenced; cannot verify embedding "
                f"(pdfimages/poppler unavailable or PDF unreadable)"
            )
            log_detail("install poppler-utils to enable the PDF embedding check.")
        elif m_images == 0:
            report(
                f"{n_graphics} \\includegraphics referenced but the PDF embeds "
                f"ZERO images -- figures did not materialize (silent miss)."
            )
            log_detail(
                "fix: build the figure images (caption_and_media/jpg_for_compilation/"
                "*.jpg) before compiling; .txt pointers do not embed."
            )
        elif m_images < n_graphics:
            log_warn(
                f"{n_graphics} \\includegraphics referenced but only {m_images} "
                f"image(s) embedded -- some figures may be missing."
            )
        else:
            log_pass(f"{n_graphics} figure(s) referenced, {m_images} embedded")

    # --- SECONDARY: log deficiency scan ---
    _scan_log(args.log, report)

    print()
    print(
        f"{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )
    return 1 if FAIL_COUNT > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
