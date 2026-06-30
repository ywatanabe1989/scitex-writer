#!/bin/bash
# -*- coding: utf-8 -*-
# File: scripts/shell/modules/render_claims.sh
#
# Regenerate 00_shared/claims_rendered.tex from 00_shared/claims.json (the
# \vclaim value SSoT) before the manuscript is flattened, so the shell compile
# path can never ship a stale/hand-edited claims_rendered.tex. No-op when
# claims.json is absent; FAILS LOUD (non-zero) when claims.json exists but
# rendering errors. Delegates to scripts/python/render_claims.py.

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Honor the PROJECT_ROOT the caller (compile_*.sh) already resolved + exported;
# fall back to the install-relative root when run standalone.
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$THIS_DIR/../../.." && pwd)}"
PY="${SCITEX_WRITER_PYTHON:-python3}"

exec "$PY" "$PROJECT_ROOT/scripts/python/render_claims.py" "$PROJECT_ROOT"
