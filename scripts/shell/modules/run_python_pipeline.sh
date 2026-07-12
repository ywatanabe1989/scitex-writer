#!/bin/bash
# -*- coding: utf-8 -*-
# ROLE: engine-vendored — DO NOT edit here. `scitex-writer update-project`
# overwrites this file on every re-vendor; fix it upstream in the
# scitex-writer package instead (local edits are lost, and update-project
# may set it read-only in the consumer workspace after vendoring).
# File: ./scripts/shell/modules/run_python_pipeline.sh
# Description: Delegate a heavy compile stage to the INSTALLED scitex-writer
#              Python package.
#
# The four heavy stages (figures / tables / diff / archive) were ported to
# Python (scitex-writer 2.28.0). The shell stays the ORCHESTRATOR; this module
# is the single launcher every compile_*.sh uses to reach the Python engine, so
# the ported bug fixes (backend-independent math escaping, really-tiled
# multi-panel figures, real cropping, no diff-against-self) actually run on the
# real compile path.
#
# Contract (positional, mirrors the shell modules this replaces):
#     run_python_pipeline.sh figures  <no_figs> <p2t> <verbose> <crop>
#     run_python_pipeline.sh tables   <no_tables>
#     run_python_pipeline.sh diff
#     run_python_pipeline.sh archive
#
# Document type comes from $SCITEX_WRITER_DOC_TYPE (exported by every
# compile_*.sh); the project root from $PROJECT_ROOT or the script location.
#
# FAILS LOUD when the Python package is not importable. There is deliberately
# NO fallback to the old shell modules: falling back would silently reintroduce
# the four bugs the Python port fixed.

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$(cd "$THIS_DIR/../../.." && pwd)}"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }

usage() {
    echo "Usage: $(basename "${BASH_SOURCE[0]}") <figures|tables|diff|archive> [args...]"
}

SCITEX_WRITER_PYTHON="${SCITEX_WRITER_PYTHON:-python3}"

ensure_python_engine() {
    if ! command -v "$SCITEX_WRITER_PYTHON" >/dev/null 2>&1; then
        echo_error "Python interpreter not found: $SCITEX_WRITER_PYTHON"
        echo_error "  The compile engine's figure/table/diff/archive stages run in Python."
        echo_error "  Install Python 3, or point SCITEX_WRITER_PYTHON at your interpreter."
        return 1
    fi
    if ! "$SCITEX_WRITER_PYTHON" -c "import scitex_writer" >/dev/null 2>&1; then
        echo_error "The scitex-writer Python package is not importable by $SCITEX_WRITER_PYTHON"
        echo_error "  The compile engine's figure/table/diff/archive stages live in that package."
        echo_error "  Fix: pip install -U scitex-writer"
        echo_error "  (or: export SCITEX_WRITER_PYTHON=/path/to/venv/bin/python)"
        return 1
    fi
    return 0
}

run_stage() {
    local stage="$1"
    shift

    local doc_type="${SCITEX_WRITER_DOC_TYPE:-manuscript}"
    local -a cmd=("$SCITEX_WRITER_PYTHON" -m scitex_writer)

    case "$stage" in
    figures)
        local no_figs="${1:-false}"
        local p2t="${2:-false}"
        # ${3} is the shell module's `verbose` flag — the Python engine always
        # reports its per-stage counts, so it has no separate verbose switch.
        local crop="${4:-false}"
        cmd+=(figures render -p "$PROJECT_ROOT" -t "$doc_type")
        [ "$no_figs" = true ] && cmd+=(--no-figs)
        [ "$p2t" = true ] && cmd+=(--pptx)
        [ "$crop" = true ] && cmd+=(--crop)
        ;;
    tables)
        local no_tables="${1:-false}"
        cmd+=(tables render -p "$PROJECT_ROOT" -t "$doc_type")
        [ "$no_tables" = true ] && cmd+=(--no-tables)
        ;;
    diff)
        cmd+=(compile diff -p "$PROJECT_ROOT" -t "$doc_type")
        [ -n "${SCITEX_DIFF_FROM:-}" ] && cmd+=(--from "$SCITEX_DIFF_FROM")
        [ -n "${SCITEX_WRITER_DIFF_TIMEOUT:-}" ] && cmd+=(--timeout "$SCITEX_WRITER_DIFF_TIMEOUT")
        ;;
    archive)
        cmd+=(compile archive -p "$PROJECT_ROOT" -t "$doc_type" --yes)
        ;;
    *)
        echo_error "Unknown pipeline stage: $stage"
        usage
        return 2
        ;;
    esac

    echo_info "Python engine: ${cmd[*]}"
    "${cmd[@]}"
    local status=$?
    if [ $status -eq 0 ]; then
        echo_success "Python $stage pipeline finished"
    else
        echo_error "Python $stage pipeline failed (exit $status)"
    fi
    return $status
}

main() {
    if [ $# -lt 1 ]; then
        usage
        exit 2
    fi
    ensure_python_engine || exit 1
    run_stage "$@"
}

if [ "${BASH_SOURCE[0]}" == "${0}" ]; then
    main "$@"
fi

# EOF
