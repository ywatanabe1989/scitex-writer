#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/python/check_claim_citations.py
# Purpose: Hard-fail an undefined \vclaim{id}, the same way check_references.py
#          hard-fails an undefined \cite / \ref.
#
# WHY THIS EXISTS. \vclaim{id} looks up \v@claim@<sanitized-id>@<style>; when
# that macro is undefined the \vclaim fallback SILENTLY prints
# "[\texttt{claim:id}]" into the PDF. So a headline number a paragraph cites
# renders as a literal "[claim:x]" placeholder, and nothing fails — the exact
# opposite of how the same toolchain treats a missing \cite key. \vclaim is the
# ONE citation class whose whole purpose is binding prose to computational
# evidence; a silent placeholder there is a wrong answer about the science.
# (Reported by paper-scitex-clew, 2026-07-14: 4 abstract headline numbers
# rendered as [claim:...] placeholders and shipped through review.)
#
# THE SANITIZE TRAP. The defined macro name is built from _sanitize_id(id),
# which strips everything except [a-zA-Z0-9]. So a claim cited as
# \vclaim{cohorta_inter_ncaps} (underscores) must be matched against the
# DEFINED id "cohortainterncaps" — a raw string compare silently misses. This
# check imports the renderer's own _sanitize_id so the two can never drift.
#
# SCOPE. This matches \vclaim only. The report also mentioned \l{id}, but no
# \l claim macro is defined anywhere in writer (LaTeX's built-in \l is the
# barred-L ł); matching it would cry wolf on every legitimate ł, which is its
# own silent-wrong-answer (a check that fails on correct input trains people to
# ignore it). If \l is a clew-layer citation macro, that belongs in a clew-side
# or separate check — flagged back to the reporter.

import argparse
import re
import sys
from collections import defaultdict
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
_LEVEL = "error"

# \vclaim[optional-style]{id} — the optional [..] is the render style; the
# mandatory {..} is the claim id we validate.
_VCLAIM = re.compile(r"\\vclaim(?:\[[^\]]*\])?\{([^}]+)\}")


def log_pass(msg):
    global PASS_COUNT
    print(f"  {GREEN}[PASS]{NC} {msg}")
    PASS_COUNT += 1


def log_warn(msg):
    global WARN_COUNT
    print(f"  {YELLOW}[WARN]{NC} {msg}")
    WARN_COUNT += 1


def log_fail(msg):
    """Report a defect. At level ``warn`` it is demoted to a non-fatal
    ``[WARN]`` (report but exit 0); at ``error`` (default) it is a fatal
    ``[FAIL]`` driving exit 1 — same severity model as check_references.py."""
    global FAIL_COUNT
    if _LEVEL == "warn":
        log_warn(msg)
        return
    print(f"  {RED}[FAIL]{NC} {msg}")
    FAIL_COUNT += 1


def log_detail(msg):
    print(f"    {DIM}{msg}{NC}")


def _sanitize(claim_id):
    """The renderer's macro-name rule. Imported from the package so this check
    can never drift from how the macros are actually named; if the import fails
    the install is broken and we fall back to the identical regex rather than
    guess a different rule."""
    try:
        from scitex_writer._mcp.handlers._claim_format import _sanitize_id

        return _sanitize_id(claim_id)
    except Exception:
        return re.sub(r"[^a-zA-Z0-9]", "", claim_id)


def collect_tex_files(doc_dir):
    """SOURCE .tex only — same set check_references.py validates."""
    skip = re.compile(r"_v\d+\.tex$|_diff\.tex$")
    files = []
    content_dir = doc_dir / "contents"
    if content_dir.exists():
        for f in content_dir.glob("*.tex"):
            if not skip.search(f.name):
                files.append(f)
        for subdir in ["figures/caption_and_media", "tables/caption_and_media"]:
            d = content_dir / subdir
            if d.exists():
                files.extend(d.glob("*.tex"))
    base = doc_dir / "base.tex"
    if base.exists():
        files.append(base)
    return list(set(files))


def extract_vclaims(tex_files):
    """Every \\vclaim{id} use. Returns raw_id -> [(file, line_no), ...]."""
    used = defaultdict(list)
    for f in tex_files:
        text = f.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(text.splitlines(), 1):
            stripped = line.split("%")[0] if "%" in line else line
            for m in _VCLAIM.finditer(stripped):
                key = m.group(1).strip()
                if key and not key.startswith("#"):  # skip macro args like #2
                    used[key].append((f, line_no))
    return dict(used)


def defined_claim_ids(project_dir):
    """Sanitized ids of every claim defined in 00_shared/claims.json (the SSoT
    the renderer builds macros from). Returns None when claims.json is absent —
    distinct from an empty set (present but no claims)."""
    import json

    claims_json = project_dir / "00_shared" / "claims.json"
    if not claims_json.exists():
        return None
    try:
        data = json.loads(claims_json.read_text(encoding="utf-8"))
    except Exception:
        return None
    claims = data.get("claims", {})
    ids = (
        claims.keys()
        if isinstance(claims, dict)
        else (c.get("claim_id") or c.get("id") for c in claims if isinstance(c, dict))
    )
    return {_sanitize(str(cid)) for cid in ids if cid}


def main():
    global _LEVEL

    parser = argparse.ArgumentParser(
        description="Hard-fail an undefined \\vclaim{id} (mirrors the undefined-\\cite check)"
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument(
        "--doc-type",
        choices=["manuscript", "supplementary", "all"],
        default="all",
    )
    parser.add_argument(
        "--level",
        choices=["off", "warn", "error"],
        default=None,
        help="Severity: error (default), warn (report but exit 0), or off.",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    _LEVEL = resolve_level(
        "claim_citations",
        args.level,
        project_dir,
        default="error",
        env_var="SCITEX_WRITER_CLAIM_CITATIONS",
    )

    print(f"\n{BOLD}=== Claim-Citation Check ==={NC}\n")
    if _LEVEL == "off":
        print(
            f"  {DIM}[INFO]{NC} claim-citation check is disabled (level=off). "
            f"Set claim_citations.level or --level to enable."
        )
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0

    doc_dirs = []
    if args.doc_type in ("manuscript", "all"):
        d = project_dir / "01_manuscript"
        if d.exists():
            doc_dirs.append(("manuscript", d))
    if args.doc_type in ("supplementary", "all"):
        d = project_dir / "02_supplementary"
        if d.exists():
            doc_dirs.append(("supplementary", d))

    used = {}
    for _, doc_dir in doc_dirs:
        for k, v in extract_vclaims(collect_tex_files(doc_dir)).items():
            used.setdefault(k, []).extend(v)

    if not used:
        log_pass("No \\vclaim citations to validate")
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
            f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
        )
        return 0

    defined = defined_claim_ids(project_dir)
    if defined is None:
        # \vclaim is used but there is no claims.json to define ANY of them:
        # every use is an undefined placeholder. This is exactly the silent
        # failure — a manuscript citing computed values with no value store.
        log_fail(
            f"{len(used)} \\vclaim citation(s) used but 00_shared/claims.json "
            f"is absent — every one renders as a [claim:...] placeholder"
        )
        for key, locations in sorted(used.items()):
            for f, line in locations:
                log_detail(f"{f.name}:{line}: \\vclaim{{{key}}} -> no claims.json")
        defined = set()

    missing = {k: v for k, v in used.items() if _sanitize(k) not in defined}
    if not missing:
        log_pass(f"All \\vclaim citations resolved: {len(used)} claim(s)")
    else:
        log_fail(
            f"Undefined claim citations: {len(missing)} of {len(used)} "
            f"\\vclaim id(s) have no definition in claims.json"
        )
        for key, locations in sorted(missing.items()):
            for f, line in locations:
                log_detail(
                    f"{f.name}:{line}: \\vclaim{{{key}}} -> [claim:{key}] "
                    f"placeholder (sanitized '{_sanitize(key)}' not defined)"
                )

    print(
        f"\n{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )
    if FAIL_COUNT > 0:
        print(
            f"\n{RED}Undefined \\vclaim citations render as [claim:...] "
            f"placeholders in the PDF.{NC}"
        )
        return 1
    print(f"\n{GREEN}All claim citations bind to a defined value.{NC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# EOF
