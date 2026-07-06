#!/bin/bash
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/shell/modules/run_overflow_check.sh
#
# POST-compile OVERFLOW gate. Runs scripts/python/check_overflow.py at its
# RESOLVED severity (off|warn|error via CLI/env/config, shared _severity
# resolver, default warn). It parses the LaTeX .log produced by the LAST
# compile for `Overfull \hbox`/`Overfull \vbox` — content that runs off the
# page (wide tables/figures, over-tall pages) — so overflow surfaces
# AUTOMATICALLY after every compile without a manual `scitex-writer
# check-overflow` call. It CANNOT run in the pre-compile validate gate
# (run_provenance_checks.sh): the .log does not exist until LaTeX has run.
#   off   -> no-op with a loud disabled note (exit 0)
#   warn  -> reports, exit 0 (does NOT block) — the default
#   error -> exit 1 (blocks, fail-loud) when content overflows the page
# ROBUST when the .log is MISSING (an earlier compile failure produced no
# .log): check_overflow.py reports "No .log found ... compile first, then
# overflow can be checked." and exits 0 — no crash, no silent swallow.
#
# Doc-type comes from SCITEX_WRITER_DOC_TYPE (exported by each compile_*.sh);
# defaults to manuscript when run standalone.

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$THIS_DIR/../../.." && pwd)}"
PY="${SCITEX_WRITER_PYTHON:-python3}"

script="$THIS_DIR/../../python/check_overflow.py"
[ -f "$script" ] || exit 0

"$PY" "$script" "$PROJECT_ROOT" --doc-type "${SCITEX_WRITER_DOC_TYPE:-manuscript}"
