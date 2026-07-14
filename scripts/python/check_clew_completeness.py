#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/python/check_clew_completeness.py
# Purpose: Pre-compile COVERAGE gate — assert that the claims the MANUSCRIPT
#          renders are the claims clew has GROUNDED. Its sibling
#          check_clew_verify.py asks "are the grounded claims still valid
#          against their sources?"; this asks the question that one cannot:
#          "did the gate look at the manuscript AT ALL?".
#
# WHY THIS EXISTS. check_clew_verify delegates to `clew verify`, which reports
# a verdict over CLEW'S STORE. So it can pass having checked a claim set that is
# DISJOINT from what the PDF renders — a green gate certifying a paper it never
# looked at. Measured on a real manuscript (paper-scitex-clew): clew's store had
# 1 claim; the manuscript rendered 83; the intersection was 0. "0/1 verified"
# reads like one near-miss; it MEANS "I have never seen your manuscript". A
# verdict without a denominator taken from the manuscript is not a verdict.
# (Reported as writer-clew-gate-verifies-disjoint-claimset, Defect A.)
#
# HOW. The manuscript claim set = the raw \vclaim{...} arguments the paper cites
# + the 00_shared/claims.json keys. The join key is the RAW claim_id, no
# transform on either side (confirmed with scitex-clew: claim_id is clew's
# identity; the sanitized macro name is writer's rendering plumbing, not the
# join key). We hand that set to `clew gate-completeness --submission <identity
# mapping> --json`, which checks it against clew's grounded claim_ids and returns
# {ok, grounded, missing, orphan}. `missing` = manuscript claims clew has NOT
# grounded = uncertified values in the PDF = the coverage gap we hard-fail on.
#
# `orphan` (grounded but never cited) does NOT reduce coverage and is reported
# as advisory, not fatal — a registered claim the paper does not use is
# housekeeping, not a wrong value in the manuscript.
#
# CLI-only, like check_clew_verify: shells the clew binary, never imports
# scitex_clew, so it works with just "clew on PATH".

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _severity import resolve_level  # noqa: E402

# Reuse the sibling gate's helpers so research-default, clew discovery, and the
# require_claims knob can never drift between the two provenance gates.
from check_clew_verify import (  # noqa: E402
    _find_clew,
    _is_research_project,
    resolve_require_claims,
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
    global FAIL_COUNT
    print(f"  {RED}[FAIL]{NC} {msg}")
    FAIL_COUNT += 1


def log_detail(msg):
    print(f"    {DIM}{msg}{NC}")


def _collect_tex_files(doc_dir):
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


def manuscript_claim_set(project_dir):
    """Every claim the manuscript RENDERS: raw \\vclaim{...} args + claims.json
    keys. Raw, no sanitize — this is the join key clew reconciles on."""
    ids = set()
    for doc in ("01_manuscript", "02_supplementary", "03_revision"):
        d = project_dir / doc
        if not d.exists():
            continue
        for f in _collect_tex_files(d):
            text = f.read_text(encoding="utf-8", errors="replace")
            for line in text.splitlines():
                stripped = line.split("%")[0] if "%" in line else line
                for m in _VCLAIM.finditer(stripped):
                    k = m.group(1).strip()
                    if k and not k.startswith("#"):
                        ids.add(k)
    claims_json = project_dir / "00_shared" / "claims.json"
    if claims_json.exists():
        try:
            data = json.loads(claims_json.read_text(encoding="utf-8"))
            claims = data.get("claims", {})
            if isinstance(claims, dict):
                ids.update(claims.keys())
            else:
                ids.update(
                    c.get("claim_id") or c.get("id")
                    for c in claims
                    if isinstance(c, dict) and (c.get("claim_id") or c.get("id"))
                )
        except Exception:
            pass
    return {i for i in ids if i}


def _resolve_clew_workdir(project_dir):
    """Where clew's CANONICAL DB lives, which is NOT always project_dir.

    A vendored project keeps the manuscript at <repo>/.scitex/writer while clew's
    canonical store is <repo>/.scitex/clew/runtime/clew.db (the fleet
    runtime-state-DB layout). Pointing `clew gate-completeness --workdir` at the
    writer subdir resolves a DIFFERENT (or nested, stale) clew DB and reports a
    WRONG coverage denominator — measured on a real project that carried two
    clew DBs of different contents (0 vs ~30 grounded). A coverage gate that
    reconciles against the wrong DB is the same silent-wrong-answer it exists to
    catch, so resolve the canonical store deterministically: walk up from
    project_dir to the nearest ancestor that has `.scitex/clew`, else fall back
    to project_dir.
    """
    for d in (project_dir, *project_dir.parents):
        if (d / ".scitex" / "clew").is_dir():
            return d
    return project_dir


def _run_gate_completeness(clew_bin, project_dir, claim_ids):
    """Shell `clew gate-completeness` with an IDENTITY submission over the
    manuscript claim set. Returns (exit_code, parsed_json_or_None, raw_output)."""
    submission = {cid: cid for cid in claim_ids}
    tmp = Path(tempfile.mkstemp(suffix=".json", prefix="writer-coverage-")[1])
    tmp.write_text(json.dumps(submission))
    try:
        proc = subprocess.run(
            [
                clew_bin,
                "gate-completeness",
                "--submission",
                str(tmp),
                "--workdir",
                str(_resolve_clew_workdir(project_dir)),
                "--json",
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return 124, None, "clew gate-completeness timed out after 120s"
    except OSError as exc:
        return 125, None, f"could not execute clew: {exc}"
    finally:
        try:
            tmp.unlink()
        except OSError:
            pass
    raw = (proc.stdout or "") + (proc.stderr or "")
    try:
        parsed = json.loads(proc.stdout)
    except Exception:
        parsed = None
    return proc.returncode, parsed, raw.strip()


def main():
    global FAIL_COUNT

    parser = argparse.ArgumentParser(
        description="Pre-compile clew COVERAGE gate: assert the manuscript's "
        "rendered claims are the claims clew has grounded. Defaults ON (error) "
        "for research projects, off otherwise."
    )
    parser.add_argument("project_dir", nargs="?", default=".")
    parser.add_argument(
        "--level",
        choices=["off", "warn", "error"],
        default=None,
        help="Severity: off, warn, or error. Overrides env and config.",
    )
    parser.add_argument(
        "--require-claims",
        action="store_true",
        help="Reclassify a missing clew CLI as a real failure (ADR-0021).",
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()
    research = _is_research_project(project_dir)
    default = "error" if research else "off"
    level = resolve_level(
        "clew_completeness",
        args.level,
        project_dir,
        default=default,
        env_var="SCITEX_WRITER_CLEW_COMPLETENESS",
    )
    require_claims = resolve_require_claims(args.require_claims, project_dir)
    soft_report = (
        (log_fail if level == "error" else log_warn) if require_claims else log_warn
    )
    kind = "research" if research else "non-research"
    print(f"\n{BOLD}=== Clew Coverage Gate (level={level}, {kind}) ==={NC}\n")

    if level == "off":
        print(
            f"  {DIM}[INFO]{NC} clew coverage gate is disabled (level=off). "
            f"Set clew_completeness.level or --level to enable."
        )
        _summary()
        return 0

    manuscript = manuscript_claim_set(project_dir)
    if not manuscript:
        log_pass("no manuscript claims to reconcile (\\vclaim / claims.json empty)")
        _summary()
        return 0

    clew_bin = _find_clew()
    if clew_bin is None:
        soft_report(
            "clew CLI not found -- manuscript coverage is UNVERIFIED for this build."
        )
        log_detail(
            "install scitex-clew to enable, or set clew_completeness.level: off."
        )
        _summary()
        return 1 if FAIL_COUNT > 0 else 0

    code, parsed, raw = _run_gate_completeness(clew_bin, project_dir, manuscript)

    if parsed is None:
        # A gate that cannot get an answer must not pass silently.
        report = log_fail if level == "error" else log_warn
        report(f"clew gate-completeness gave no parseable verdict (exit {code}).")
        for line in raw.splitlines()[:20]:
            log_detail(line)
        _summary()
        return 1 if FAIL_COUNT > 0 else 0

    missing = parsed.get("missing") or {}
    orphan = parsed.get("orphan") or {}
    total = len(manuscript)
    covered = total - len(missing)
    pct = (covered * 100 // total) if total else 100

    if missing:
        report = log_fail if level == "error" else log_warn
        report(
            f"coverage {covered}/{total} ({pct}%): {len(missing)} manuscript "
            f"claim(s) are RENDERED but NOT clew-grounded -- their values are "
            f"uncertified in the PDF"
        )
        for cid in sorted(missing)[:40]:
            log_detail(f"ungrounded: {cid}")
        if len(missing) > 40:
            log_detail(f"... and {len(missing) - 40} more")
        log_detail(
            "fix: register + ground these claims in clew (they must trace to a "
            "signed source), or remove the \\vclaim citation. Override with "
            "clew_completeness.level if intended."
        )
    else:
        log_pass(
            f"coverage {total}/{total} (100%): every manuscript claim is clew-grounded"
        )

    # Orphans do not reduce coverage; report advisory so a registered-but-uncited
    # claim is visible without blocking the compile.
    if orphan:
        log_warn(
            f"{len(orphan)} grounded claim(s) are never cited in the manuscript "
            f"(orphan -- housekeeping, not a wrong value)"
        )
        for cid in sorted(orphan)[:20]:
            log_detail(f"orphan: {cid}")

    _summary()
    return 1 if FAIL_COUNT > 0 else 0


def _summary():
    print()
    print(
        f"{BOLD}Summary:{NC} {GREEN}{PASS_COUNT} passed{NC}, "
        f"{YELLOW}{WARN_COUNT} warnings{NC}, {RED}{FAIL_COUNT} errors{NC}"
    )


if __name__ == "__main__":
    sys.exit(main())

# EOF
