#!/bin/bash
# -*- coding: utf-8 -*-
# File: scripts/shell/modules/run_provenance_checks.sh
#
# Run the config-driven pre-compile checks at their RESOLVED severity
# (off|warn|error via CLI/env/config). Each underlying script
# (scripts/python/check_{paper_symlink,media_provenance,caption_footnote,
#  clew_verify}.py) resolves its own level and exits non-zero ONLY at
# error-level with a violation. So:
#   off   -> no-op (exit 0)
#   warn  -> reports, exit 0 (does NOT block the compile)
#   error -> exit 1 (blocks the compile, fail-loud)
# This is what makes `paper_symlink: error` / `media_provenance: error` /
# `caption_footnote: error` actually enforce at compile time -- previously the
# compile ran none of them. caption_footnote defaults to error (a \footnote in
# a \caption{} is always a fatal compile pattern). clew_verify is the
# provenance GATE (ADR-0021): it re-verifies every clew-registered claim
# against its bound source and defaults to error for research projects
# (.scitex/dev/config.yaml project-type: research), off otherwise. citations is
# the CITATION GATE: it fails the build when a cited reference is an unresolved
# scholar stub (auto-generated placeholder), also error for research / warn
# otherwise -- the compiler-owns half of the citation->clew verification
# contract (a stub \cite can never reach a compiled research manuscript).
# figure_media is the FIGURE-MEDIA GATE: it fails the build when a figure is
# DECLARED (a caption .tex) but has NO rendered media asset, so the compile can
# no longer silently substitute a "Missing Figure" placeholder. It runs BEFORE
# process_figures.sh (which creates the placeholder), so at error-level the
# placeholder path is never reached; defaults to error for research projects,
# warn otherwise (the public template ships example captions without media).
#
# Returns the worst exit code across the checks (0 unless a check errored).

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Honor the PROJECT_ROOT the caller (compile_*.sh) already resolved + exported;
# fall back to the install-relative root when run standalone.
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$THIS_DIR/../../.." && pwd)}"
PY="${SCITEX_WRITER_PYTHON:-python3}"

rc=0
for chk in check_paper_symlink check_media_provenance check_figure_media check_caption_footnote check_clew_verify check_citations check_version_freshness; do
    script="$THIS_DIR/../../python/${chk}.py"
    [ -f "$script" ] || continue
    "$PY" "$script" "$PROJECT_ROOT" || rc=$?
done

exit "$rc"
