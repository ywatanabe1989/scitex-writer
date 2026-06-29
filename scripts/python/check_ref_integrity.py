#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: scripts/python/check_ref_integrity.py
# Purpose: Pre-compile REFERENCE-INTEGRITY gate. Validate every reference class
#          up front, report ALL problems at once (file:line), then exit non-zero
#          so the caller can BLOCK the compile (the compile stage proceeds only
#          on an explicit --yes/--force). Catches ?-refs and undefined \cite
#          BEFORE a full compile instead of after, buried in the log.
#
#          Four classes:
#            1. FIGURE  \ref  -> resolves to a \label / auto-label (fig:STEM)
#            2. TABLE   \ref  -> resolves to a \label / auto-label (tab:STEM)
#            3. CITATION      -> every \cite key exists in the merged bib
#            4. SUPPLEMENTARY -> every supple- xref resolves against the
#               supplement's .aux (base.tex \link[supple-]{...}); if the
#               supplement hasn't been compiled (its .aux is missing), say so
#               explicitly rather than reporting every supple- ref as undefined.
#
#          Reuses scripts/python/check_references.py's extractors (don't
#          rewrite). Severity off|warn|error (DEFAULT error -- a broken ref ships
#          a ?-mark / wrong PDF):
#            off   -- skip the gate
#            warn  -- report problems, exit 0 (does NOT block)
#            error -- report problems, exit 1 (caller blocks the compile)
#          Precedence (highest -> lowest): --level, env SCITEX_WRITER_REF_INTEGRITY,
#          project ./config.yaml ref_integrity.level, user
#          ~/.scitex/writer/config.yaml, default error. (To migrate onto the
#          unified scripts/python/_severity.py resolver once that lands.)
#
# Usage:
#   python check_ref_integrity.py [project_dir]
#                                 [--doc-type manuscript|supplementary|revision|all]
#                                 [--level off|warn|error]
#
# Self-contained: stdlib + optional PyYAML (config only) + sibling
# check_references.py (same scripts/python/ dir).

import argparse
import re
import sys
from pathlib import Path

# Reuse the proven extractors from the sibling check (same dir).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _severity import resolve_level  # noqa: E402
from check_references import (  # noqa: E402
    collect_tex_files,
    extract_bib_keys,
    extract_citations,
    extract_labels,
    extract_refs,
    infer_auto_labels,
)

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

_DOC_DIRS = {
    "manuscript": "01_manuscript",
    "supplementary": "02_supplementary",
    "revision": "03_revision",
}

# The supplement's labels are pulled into the main doc with this prefix
# (base.tex: \link[supple-]{./02_supplementary/supplementary}).
_SUPPLE_PREFIX = "supple-"
_SUPPLE_AUX = Path("02_supplementary") / "supplementary.aux"

_MAX_LIST = 100


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




def _read_aux_labels(aux_path):
    """Return the set of \\newlabel keys recorded in a LaTeX .aux file."""
    if not aux_path.exists():
        return None  # distinguish "not compiled" from "compiled, zero labels"
    text = aux_path.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r"\\newlabel\{([^}]+)\}", text))


def _classify(key):
    """Human label for a ref key by its prefix."""
    if key.startswith(_SUPPLE_PREFIX):
        return "supplementary"
    if key.startswith("fig:"):
        return "figure"
    if key.startswith("tab:"):
        return "table"
    return "reference"


def main():
    parser = argparse.ArgumentParser(
        description="Pre-compile reference-integrity gate: validate figure/table "
        "\\ref, \\cite-in-bib, and supple- xrefs; report all, then block."
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument(
        "--doc-type",
        choices=[*_DOC_DIRS, "all"],
        default="all",
        help="Which document(s) to scan (default: all present).",
    )
    parser.add_argument(
        "--level",
        choices=list(_LEVELS),
        default=None,
        help="Severity: off, warn, or error (default). Overrides env and config.",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    level = resolve_level(
        "ref_integrity",
        args.level,
        project_dir,
        default="error",
        env_var="SCITEX_WRITER_REF_INTEGRITY",
    )

    print(f"\n{BOLD}=== Reference Integrity Gate (level={level}) ==={NC}\n")
    if level == "off":
        print(f"  {DIM}[INFO]{NC} reference-integrity gate is disabled (level=off).")
        print(
            f"\n{BOLD}Summary:{NC} {GREEN}0 passed{NC}, "
            f"{YELLOW}0 warnings{NC}, {RED}0 errors{NC}"
        )
        return 0

    report = log_fail if level == "error" else log_warn
    doc_types = list(_DOC_DIRS) if args.doc_type == "all" else [args.doc_type]
    bib_keys = extract_bib_keys(project_dir / "00_shared" / "bib_files")

    # Supplement labels (for the supple- class). None => supplement not compiled.
    supp_labels = _read_aux_labels(project_dir / _SUPPLE_AUX)

    any_doc = False
    for doc_type in doc_types:
        doc_dir = project_dir / _DOC_DIRS[doc_type]
        if not doc_dir.is_dir():
            continue
        any_doc = True
        tex_files = collect_tex_files(doc_dir)
        refs = extract_refs(tex_files)
        labels = set(extract_labels(tex_files)) | set(infer_auto_labels(doc_dir))
        cites = extract_citations(tex_files)

        # Classes 1, 2, (other) + 4: every \ref resolves.
        supple_refs = {k: v for k, v in refs.items() if k.startswith(_SUPPLE_PREFIX)}
        local_refs = {k: v for k, v in refs.items() if not k.startswith(_SUPPLE_PREFIX)}

        for key, locs in sorted(local_refs.items()):
            if key in labels:
                continue
            for f, line in locs:
                report(f"{doc_type}: {f.name}:{line}: {_classify(key)} \\ref{{{key}}} -> ?? (no \\label)")

        # Class 4: supple- xrefs need the supplement .aux.
        if supple_refs:
            if supp_labels is None:
                report(
                    f"{doc_type}: supplement not compiled -- "
                    f"{(project_dir / _SUPPLE_AUX)} missing; "
                    f"{len(supple_refs)} supple- xref(s) cannot resolve"
                )
                log_detail("fix: run `compile.sh -s` before `compile.sh -m` so the supplement .aux exists.")
            else:
                for key, locs in sorted(supple_refs.items()):
                    bare = key[len(_SUPPLE_PREFIX):]
                    if bare in supp_labels:
                        continue
                    for f, line in locs:
                        report(
                            f"{doc_type}: {f.name}:{line}: supplementary \\ref{{{key}}} "
                            f"-> ?? (no \\label{{{bare}}} in supplement)"
                        )

        # Class 3: every \cite key exists in the merged bib.
        for key, locs in sorted(cites.items()):
            if key in bib_keys:
                continue
            for f, line in locs:
                report(f"{doc_type}: {f.name}:{line}: \\cite{{{key}}} -> not in bibliography")

    if not any_doc:
        log_pass("no document directories found to check")
    elif FAIL_COUNT == 0 and WARN_COUNT == 0:
        log_pass("all references, citations, and supple- xrefs resolve")

    print()
    print(
        f"{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )
    return 1 if FAIL_COUNT > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
