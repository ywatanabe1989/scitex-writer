#!/bin/bash
# -*- coding: utf-8 -*-
# File: scripts/shell/modules/render_clew.sh
#
# Emit 00_shared/clew_rendered.tex from scitex-clew's runtime export
# (.scitex/clew/runtime/claims.json) before the manuscript is flattened, so the
# clew presentation layer (\clewval / badge / legend) has its data. scitex-clew
# is renderer-agnostic (exports JSON, not TeX), so the JSON->TeX emit is writer's
# job. No-op when claims.json is absent (clew layer optional); FAILS LOUD
# (non-zero) when it exists but rendering errors. Delegates to
# scripts/python/render_clew.py.

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Honor the PROJECT_ROOT the caller (compile_*.sh) already resolved + exported;
# fall back to the install-relative root when run standalone.
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$THIS_DIR/../../.." && pwd)}"
PY="${SCITEX_WRITER_PYTHON:-python3}"

exec "$PY" "$PROJECT_ROOT/scripts/python/render_clew.py" "$PROJECT_ROOT"
