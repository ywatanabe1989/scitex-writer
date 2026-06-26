#!/bin/bash
# -*- coding: utf-8 -*-
# File: scripts/shell/modules/run_provenance_checks.sh
#
# Run the config-driven provenance/symlink checks at their RESOLVED severity
# (off|warn|error via CLI/env/config). Each underlying script
# (scripts/python/check_{paper_symlink,media_provenance}.py) resolves its own
# level and exits non-zero ONLY at error-level with a violation. So:
#   off   -> no-op (exit 0)
#   warn  -> reports, exit 0 (does NOT block the compile)
#   error -> exit 1 (blocks the compile, fail-loud)
# This is what makes `paper_symlink: error` / `media_provenance: error` actually
# enforce at compile time -- previously the compile ran neither check.
#
# Returns the worst exit code across the checks (0 unless a check errored).

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Honor the PROJECT_ROOT the caller (compile_*.sh) already resolved + exported;
# fall back to the install-relative root when run standalone.
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$THIS_DIR/../../.." && pwd)}"
PY="${SCITEX_WRITER_PYTHON:-python3}"

rc=0
for chk in check_paper_symlink check_media_provenance; do
    script="$THIS_DIR/../../python/${chk}.py"
    [ -f "$script" ] || continue
    "$PY" "$script" "$PROJECT_ROOT" || rc=$?
done

exit "$rc"
