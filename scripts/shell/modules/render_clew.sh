#!/bin/bash
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: scripts/shell/modules/render_clew.sh
#
# Prepare the clew presentation-layer inputs before the manuscript is flattened:
#   1. render_clew_toggles.py -> 00_shared/clew_presentation_toggles.tex: resolve
#      the WRITER opt-in (config/env `clew_presentation`) into the \clewpres*
#      \newif toggles (the ONE knob for the page-1 provenance set).
#   2. render_clew.py -> 00_shared/clew_rendered.tex: emit the clew DATA (palette
#      + per-claim val/hex/status) from scitex-clew's runtime export
#      (.scitex/clew/runtime/claims.json). clew is renderer-agnostic (exports
#      JSON, not TeX), so the JSON->TeX emit is writer's job.
# Both no-op gracefully when their input is absent (clew layer optional) and
# FAIL LOUD (non-zero) on a malformed config / claims.json.

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Honor the PROJECT_ROOT the caller (compile_*.sh) already resolved + exported;
# fall back to the install-relative root when run standalone.
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$THIS_DIR/../../.." && pwd)}"
PY="${SCITEX_WRITER_PYTHON:-python3}"

"$PY" "$PROJECT_ROOT/scripts/python/render_clew_toggles.py" "$PROJECT_ROOT" || exit $?

# Refresh the canonical unified claims.json from scitex-clew's ledgers
# (value + citation + figure claims -> ONE claims list, the frozen render
# schema) LAST, so it is last-write-wins right before render. scitex-clew >=
# 0.4.0 provides `export-claims --unified`. clew ABSENT -> skip (render_clew
# then no-ops or reads an existing file); clew present but export FAILS ->
# WARN + continue (a decorative-layer export must not abort the compile; the
# citation/undefined-ref GATES are the fail-loud path, not this render).
CLEW_BIN="${SCITEX_WRITER_CLEW_BIN:-clew}"
if command -v "$CLEW_BIN" >/dev/null 2>&1; then
    if ! (cd "$PROJECT_ROOT" && "$CLEW_BIN" export-claims --unified) >/dev/null 2>&1; then
        echo "WARN: clew export-claims --unified failed; using existing claims.json (if any)." >&2
    fi
    # Capture the clew TOOL version so render_clew can stamp the rendered
    # provenance attestation ("audited by SciTeX Clew vX.Y.Z"). The export's
    # own version stamp (if any) still wins inside render_clew.py; this is the
    # fallback source. First semver-looking token from `clew --version`.
    if [ -z "${SCITEX_WRITER_CLEW_VERSION:-}" ]; then
        SCITEX_WRITER_CLEW_VERSION="$("$CLEW_BIN" --version 2>/dev/null \
            | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)"
        export SCITEX_WRITER_CLEW_VERSION
    fi
fi

# Loud-but-graceful degrade for --clew-overlay: the overlay was REQUESTED
# (master switch on) but no clew feed exists to color from. The presentation
# layer is DECORATIVE -- it must never abort a compile -- so warn clearly and
# continue (exit 0, marks simply do not light up). This is distinct from the
# FAIL-LOUD path for a MALFORMED claims.json, which stays in render_clew.py.
_clew_pres="$(printf '%s' "${SCITEX_WRITER_CLEW_PRESENTATION:-}" | tr '[:upper:]' '[:lower:]')"
case "$_clew_pres" in
1 | true | yes | on)
    _clew_feed="$PROJECT_ROOT/.scitex/clew/runtime/claims.json"
    if [ ! -s "$_clew_feed" ]; then
        echo "WARN: --clew-overlay requested but no clew feed found at $_clew_feed;" >&2
        echo "      run \`clew export-claims --unified\` first -- compiling without provenance marks." >&2
    fi
    ;;
esac

exec "$PY" "$PROJECT_ROOT/scripts/python/render_clew.py" "$PROJECT_ROOT"
