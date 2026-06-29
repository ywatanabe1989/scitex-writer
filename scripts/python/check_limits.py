#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/check_limits.py
# Purpose: Fast pre-compile validation of per-section word limits and the
#          reference (citation) cap declared in config/config_<doctype>.yaml
#          under the `limits:` block. Designed to run at the START of
#          compilation, before any heavy pdflatex work (fail-fast).
#
#          Over-limit  -> WARNING with a hint (compilation continues).
#          With --strict (or limits.strict: true, or
#          SCITEX_WRITER_LINT_STRICT=1) -> ERROR + non-zero exit so the
#          build stops early instead of after a full compile.
#
# Usage:
#   python check_limits.py [project_dir] [--doc-type manuscript] [--strict]
#
# Word counts use the SAME `texcount ... -inc -1 -sum` invocation as
# scripts/shell/modules/count_words.sh, so the numbers match what the
# manuscript prints. References are unique \cite* keys in the source .tex
# (the same family of commands check_references.py recognises).

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _severity import resolve_level  # noqa: E402

# ANSI colors (match check_references.py)
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
DIM = "\033[0;90m"
BOLD = "\033[1m"
NC = "\033[0m"

PASS_COUNT = 0
WARN_COUNT = 0
FAIL_COUNT = 0

# IMRD sections + abstract. main_text limit is compared against the IMRD sum.
_IMRD = ["introduction", "methods", "results", "discussion"]
_SECTIONS = ["abstract"] + _IMRD

_DOC_DIRS = {
    "manuscript": "01_manuscript",
    "supplementary": "02_supplementary",
    "revision": "03_revision",
}

# Same citation-command family as check_references.py (+ a few biblatex forms).
_CITE_RE = re.compile(
    r"\\(?:cite|citep|citet|citealt|citealp|citeauthor|citeyear|citenum)\*?\{([^}]+)\}"
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


def load_limits(config_path):
    """Load the ``limits:`` block from a doc-type config YAML.

    Returns the limits dict, ``{}`` when there is no block, or ``None`` on a
    hard error (missing PyYAML, invalid YAML, wrong shape). ``None`` is a
    fail-loud signal — the caller turns it into a non-zero exit rather than
    silently skipping enforcement.
    """
    try:
        import yaml
    except ImportError:
        print(
            f"{RED}ERROR:{NC} PyYAML not installed — cannot read limits from "
            f"{config_path}. Fix: pip install pyyaml",
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
    limits = data.get("limits")
    if limits is None:
        return {}
    if not isinstance(limits, dict):
        print(
            f"{RED}ERROR:{NC} `limits:` in {config_path} must be a mapping, "
            f"got {type(limits).__name__}",
            file=sys.stderr,
        )
        return None
    return limits


def resolve_texcount():
    from shutil import which

    return which("texcount")


def count_words(texcount, section_tex):
    """Words in a section .tex via the same flags count_words.sh uses.

    Returns the integer count, or ``None`` if the file is missing or texcount
    produced no number.
    """
    if not section_tex.exists():
        return None
    try:
        out = subprocess.run(
            [texcount, str(section_tex), "-inc", "-1", "-sum"],
            capture_output=True,
            text=True,
            timeout=30,
        ).stdout
    except (subprocess.TimeoutExpired, OSError):
        return None
    m = re.search(r"\d+", out)
    return int(m.group(0)) if m else None


def collect_source_tex(doc_dir):
    """Source .tex files that may carry \\cite commands (not generated files)."""
    files = []
    content_dir = doc_dir / "contents"
    if content_dir.exists():
        files += [
            f
            for f in content_dir.glob("*.tex")
            if not re.search(r"_v\d+\.tex$|_diff\.tex$", f.name)
        ]
        for sub in ("figures/caption_and_media", "tables/caption_and_media"):
            d = content_dir / sub
            if d.exists():
                files += list(d.glob("*.tex"))
    base = doc_dir / "base.tex"
    if base.exists():
        files.append(base)
    return files


def unique_cite_keys(tex_files):
    """Unique citation keys actually referenced in the source (deduplicated)."""
    keys = set()
    for f in tex_files:
        text = f.read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            stripped = line.split("%")[0] if "%" in line else line
            for m in _CITE_RE.finditer(stripped):
                for key in m.group(1).split(","):
                    key = key.strip()
                    if key and not key.startswith("#"):
                        keys.add(key)
    return keys


def check_limit(label, value, limit, strict, unit):
    """Compare ``value`` to ``limit``; emit pass / warn / fail with a hint."""
    if limit is None:  # ~ in YAML => no limit configured
        return
    if value is None:
        log_warn(f"{label}: source missing — cannot count {unit}")
        return
    if value <= limit:
        log_pass(f"{label}: {value}/{limit} {unit}")
        return
    over = value - limit
    msg = f"{label}: {value}/{limit} {unit} — over by {over} (trim ~{over} {unit})"
    (log_fail if strict else log_warn)(msg)


def main():
    parser = argparse.ArgumentParser(
        description="Validate per-section word limits + reference cap "
        "(fast, runs before compilation)."
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument("--doc-type", choices=list(_DOC_DIRS), default="manuscript")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Promote over-limit warnings to errors (non-zero exit).",
    )
    parser.add_argument(
        "--level",
        choices=["off", "warn", "error"],
        default=None,
        help="Severity: warn (default), off, or error. Overrides env and "
        "config; --strict is a tightening alias for error.",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    doc_dir = project_dir / _DOC_DIRS[args.doc_type]
    config_path = project_dir / "config" / f"config_{args.doc_type}.yaml"

    print(f"\n{BOLD}=== Limit Check ({args.doc_type}) ==={NC}\n")

    limits = load_limits(config_path)
    if limits is None:
        return 1  # hard error already printed loudly
    if not limits:
        print(
            f"  {DIM}[INFO]{NC} No `limits:` block in {config_path.name} — "
            f"nothing to enforce."
        )
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0

    level = resolve_level(
        "limits",
        args.level,
        project_dir,
        default="warn",
        env_var="SCITEX_WRITER_LIMITS",
        legacy_strict=args.strict or bool(limits.get("strict", False)),
    )
    if level == "off":
        print(
            f"  {DIM}[INFO]{NC} limit check is disabled (level=off). "
            f"Set limits.level or --level to enable."
        )
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0
    strict = level == "error"

    if not doc_dir.exists():
        print(f"{RED}ERROR:{NC} {doc_dir} not found", file=sys.stderr)
        return 1

    words = limits.get("words") or {}
    word_limits_set = words.get("main_text") is not None or any(
        words.get(s) is not None for s in _SECTIONS
    )

    # --- Word limits (need texcount; only resolve it if any are set) ---------
    if word_limits_set:
        texcount = resolve_texcount()
        if not texcount:
            (log_fail if strict else log_warn)(
                "texcount not found — cannot enforce word limits. "
                "Fix: install texlive-binaries (provides texcount) or add it to PATH."
            )
        else:
            counts = {}
            for sec in _SECTIONS:
                counts[sec] = count_words(texcount, doc_dir / "contents" / f"{sec}.tex")
                check_limit(
                    sec.capitalize(), counts[sec], words.get(sec), strict, "words"
                )
            if words.get("main_text") is not None:
                imrd = [counts[s] for s in _IMRD if counts.get(s) is not None]
                total = sum(imrd) if imrd else None
                check_limit(
                    "Main text (IMRD)", total, words.get("main_text"), strict, "words"
                )

    # --- Reference cap (unique \cite* keys) ----------------------------------
    if limits.get("references") is not None:
        n_cited = len(unique_cite_keys(collect_source_tex(doc_dir)))
        check_limit(
            "References", n_cited, limits.get("references"), strict, "cited refs"
        )

    print()
    print(
        f"{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )
    if FAIL_COUNT > 0:
        print(f"\n{RED}Limits exceeded (strict) — compilation should stop here.{NC}")
        return 1
    if WARN_COUNT > 0:
        print(
            f"\n{YELLOW}Over limit, but compilation continues (non-strict). "
            f"Set limits.strict: true (or --strict) to enforce.{NC}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
