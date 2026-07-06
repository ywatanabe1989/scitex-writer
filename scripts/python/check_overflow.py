#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/python/check_overflow.py
# Purpose: Detect content that runs off the page -- wide tables/figures and
#          over-tall pages -- by parsing the LaTeX .log for `Overfull \hbox`
#          (too wide) and `Overfull \vbox` (too high) boxes produced by the
#          last compile. A tabular reports `in alignment at lines X--Y`, so a
#          table that is not shown entirely shows up here as a large hbox.
#
#          Boxes at or below `overflow.max_pt` (default 5pt) are treated as
#          cosmetic and ignored. Anything larger ->
#            WARNING with a hint (compilation already finished).
#          With --strict (or overflow.strict: true, or
#          SCITEX_WRITER_LINT_STRICT=1) -> ERROR + non-zero exit.
#
# Usage:
#   python check_overflow.py [project_dir] [--doc-type manuscript]
#                            [--strict] [--max-pt 5]
#
# This runs AFTER compilation (it reads the produced .log), unlike
# check_limits.py which runs before. Self-contained: stdlib + optional PyYAML.

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _severity import resolve_level  # noqa: E402

# ANSI colors (match check_limits.py / check_references.py)
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
DIM = "\033[0;90m"
BOLD = "\033[1m"
NC = "\033[0m"

PASS_COUNT = 0
WARN_COUNT = 0
FAIL_COUNT = 0

_DOC_DIRS = {
    "manuscript": "01_manuscript",
    "supplementary": "02_supplementary",
    "revision": "03_revision",
}

_DEFAULT_MAX_PT = 5.0

# "Overfull \hbox (72.26999pt too wide) in alignment at lines 120--145"
# "Overfull \vbox (31.0pt too high) has occurred while \output is active"
_OVERFULL_RE = re.compile(
    r"Overfull \\(?P<kind>[hv])box \((?P<pts>\d+(?:\.\d+)?)pt too (?P<dim>wide|high)\)"
    r"(?:.*?in (?P<ctx>alignment|paragraph) at lines (?P<l1>\d+)--(?P<l2>\d+))?"
)

# context -> (human label, fix hint)
_HINTS = {
    "alignment": (
        "table too wide",
        "wrap the tabular in \\resizebox{\\linewidth}{!}{...}, use a landscape "
        "page, drop/merge columns, or \\footnotesize",
    ),
    "paragraph": (
        "text too wide",
        "often a long URL or unbreakable token -- use \\url{}/\\seqsplit, allow "
        "hyphenation, or rephrase",
    ),
    "page": (
        "content too tall for the page",
        "move a float, shorten the text, or allow \\raggedbottom",
    ),
}


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


def load_overflow_config(config_path):
    """Load the ``overflow:`` block from a doc-type config YAML.

    Returns the dict, ``{}`` when there is no block, or ``None`` on a hard
    error (missing PyYAML, invalid YAML, wrong shape) -- a fail-loud signal
    the caller turns into a non-zero exit.
    """
    try:
        import yaml
    except ImportError:
        print(
            f"{RED}ERROR:{NC} PyYAML not installed -- cannot read overflow "
            f"config from {config_path}. Fix: pip install pyyaml",
            file=sys.stderr,
        )
        return None
    if not config_path.exists():
        return {}
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        print(f"{RED}ERROR:{NC} {config_path} is not valid YAML: {e}", file=sys.stderr)
        return None
    overflow = data.get("overflow")
    if overflow is None:
        return {}
    if not isinstance(overflow, dict):
        print(
            f"{RED}ERROR:{NC} `overflow:` in {config_path} must be a mapping, "
            f"got {type(overflow).__name__}",
            file=sys.stderr,
        )
        return None
    return overflow


def resolve_log(doc_dir, doc_type):
    """Locate the .log produced by the last compile.

    Looks in ``<doc>/logs/<doc>.log`` first (the standard location), then a
    couple of fallbacks. Returns the Path or ``None`` if no log exists yet.
    """
    candidates = [
        doc_dir / "logs" / f"{doc_type}.log",
        doc_dir / f"{doc_type}.log",
    ]
    for c in candidates:
        if c.exists():
            return c
    # last resort: any *.log under the doc dir, newest first
    logs = sorted(doc_dir.rglob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def parse_overflows(log_text, min_pt):
    """Yield overflow boxes at or above ``min_pt`` as dicts.

    Keys: kind ('h'/'v'), pts (float), dim ('wide'/'high'),
    context ('alignment'/'paragraph'/'page'), lines (str or None).
    """
    seen = set()
    out = []
    for m in _OVERFULL_RE.finditer(log_text):
        pts = float(m.group("pts"))
        if pts < min_pt:
            continue
        ctx = m.group("ctx") or "page"
        l1, l2 = m.group("l1"), m.group("l2")
        lines = f"{l1}--{l2}" if l1 else None
        # de-duplicate identical box reports (multi-pass compiles repeat them)
        key = (m.group("kind"), round(pts, 2), ctx, lines)
        if key in seen:
            continue
        seen.add(key)
        out.append(
            {
                "kind": m.group("kind"),
                "pts": pts,
                "dim": m.group("dim"),
                "context": ctx,
                "lines": lines,
            }
        )
    return out


def report(box, strict):
    label, hint = _HINTS[box["context"]]
    where = f" at lines {box['lines']}" if box["lines"] else ""
    msg = f"{label}{where}: {box['pts']:.1f}pt too {box['dim']}"
    (log_fail if strict else log_warn)(msg)
    log_detail(f"fix: {hint}")


def main():
    parser = argparse.ArgumentParser(
        description="Detect off-page content (wide tables/figures, over-tall "
        "pages) from the LaTeX .log produced by the last compile."
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument("--doc-type", choices=list(_DOC_DIRS), default="manuscript")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Promote overflow warnings to errors (non-zero exit).",
    )
    parser.add_argument(
        "--level",
        choices=["off", "warn", "error"],
        default=None,
        help="Severity: warn (default), off, or error. Overrides env and "
        "config; --strict is a tightening alias for error.",
    )
    parser.add_argument(
        "--max-pt",
        type=float,
        default=None,
        help=f"Ignore boxes overflowing by <= this many pt (default "
        f"{_DEFAULT_MAX_PT}; overridden by overflow.max_pt in config).",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    doc_dir = project_dir / _DOC_DIRS[args.doc_type]
    config_path = project_dir / "config" / f"config_{args.doc_type}.yaml"

    print(f"\n{BOLD}=== Overflow Check ({args.doc_type}) ==={NC}\n")

    cfg = load_overflow_config(config_path)
    if cfg is None:
        return 1  # hard error already printed loudly

    level = resolve_level(
        "overflow",
        args.level,
        project_dir,
        default="warn",
        env_var="SCITEX_WRITER_OVERFLOW",
        legacy_strict=args.strict or bool(cfg.get("strict", False)),
    )
    if level == "off":
        print(
            f"  {DIM}[INFO]{NC} overflow check is disabled (level=off). "
            f"Set overflow.level or --level to enable."
        )
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0
    strict = level == "error"
    if args.max_pt is not None:
        min_pt = args.max_pt
    elif cfg.get("max_pt") is not None:
        min_pt = float(cfg["max_pt"])
    else:
        min_pt = _DEFAULT_MAX_PT

    if not doc_dir.exists():
        print(f"{RED}ERROR:{NC} {doc_dir} not found", file=sys.stderr)
        return 1

    log_file = resolve_log(doc_dir, args.doc_type)
    if log_file is None:
        print(
            f"  {DIM}[INFO]{NC} No .log found under {doc_dir.name}/ -- compile "
            f"first, then overflow can be checked."
        )
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0

    log_text = log_file.read_text(encoding="utf-8", errors="replace")
    boxes = parse_overflows(log_text, min_pt)

    if not boxes:
        log_pass(f"no overflow > {min_pt:g}pt in {log_file.name}")
    else:
        # tables first (most likely the user-visible "not shown entirely")
        boxes.sort(key=lambda b: (b["context"] != "alignment", -b["pts"]))
        for box in boxes:
            report(box, strict)

    print()
    print(
        f"{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )
    if FAIL_COUNT > 0:
        print(
            f"\n{RED}Content overflows the page (strict) -- fix before submission.{NC}"
        )
        return 1
    if WARN_COUNT > 0:
        print(
            f"\n{YELLOW}Content overflows the page. Set overflow.strict: true "
            f"(or --strict) to make this an error.{NC}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
