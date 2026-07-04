#!/bin/bash
# -*- coding: utf-8 -*-
# Test file for: compilation_compiled_tex_to_compiled_pdf.sh

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$THIS_DIR/../../../.." && pwd)"
MODULE="$ROOT_DIR/scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh"

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

assert_eq() {
    local expected="$1"
    local actual="$2"
    local desc="${3:-}"
    ((TESTS_RUN++))
    if [ "$expected" = "$actual" ]; then
        echo -e "${GREEN}✓${NC} $desc"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $desc (expected '$expected', got '$actual')"
        ((TESTS_FAILED++))
    fi
}

# Source the module for its helper functions. The module guards main() behind a
# "run only when executed directly" check, so sourcing here does NOT trigger a
# compile. config/load_config.sh resolves from the repo root; its stderr is
# irrelevant to the function under test. We override LOG_DIR afterwards.
setup_module() {
    export SCITEX_WRITER_DOC_TYPE="${SCITEX_WRITER_DOC_TYPE:-manuscript}"
    cd "$ROOT_DIR" || return 1
    # shellcheck source=/dev/null
    source "$MODULE" >/dev/null 2>&1 || true
}

# pdf_produced_pagecount reads the engine .log "Output written on ... (N pages"
# line, which is the per-run source of truth for whether a valid PDF exists.
test_pagecount_from_log_multipage() {
    local tmp
    tmp="$(mktemp -d)"
    export LOG_DIR="$tmp"
    printf 'Output written on %s/manuscript.pdf (25 pages, 4602154 bytes).\n' "$tmp" >"$tmp/manuscript.log"
    local n
    n="$(pdf_produced_pagecount "$tmp/manuscript.pdf")"
    assert_eq "25" "$n" "pdf_produced_pagecount reads 25 pages from log"
    rm -rf "$tmp"
}

test_pagecount_from_log_single_page() {
    local tmp
    tmp="$(mktemp -d)"
    export LOG_DIR="$tmp"
    printf 'Output written on %s/manuscript.pdf (1 page, 1234 bytes).\n' "$tmp" >"$tmp/manuscript.log"
    local n
    n="$(pdf_produced_pagecount "$tmp/manuscript.pdf")"
    assert_eq "1" "$n" "pdf_produced_pagecount reads 1 page from log"
    rm -rf "$tmp"
}

test_pagecount_zero_when_no_output_line() {
    local tmp
    tmp="$(mktemp -d)"
    export LOG_DIR="$tmp"
    printf 'This is pdfTeX; a fatal error occurred, no PDF finalized.\n' >"$tmp/manuscript.log"
    local n
    n="$(pdf_produced_pagecount "$tmp/manuscript.pdf")"
    assert_eq "0" "$n" "pdf_produced_pagecount returns 0 when no Output-written line"
    rm -rf "$tmp"
}

test_pagecount_zero_when_no_log() {
    local tmp
    tmp="$(mktemp -d)"
    export LOG_DIR="$tmp"
    local n
    n="$(pdf_produced_pagecount "$tmp/manuscript.pdf")"
    assert_eq "0" "$n" "pdf_produced_pagecount returns 0 when log absent (no PDF, no pdfinfo target)"
    rm -rf "$tmp"
}

# Run tests
main() {
    echo "Testing: compilation_compiled_tex_to_compiled_pdf.sh"
    echo "========================================"

    setup_module

    if ! declare -F pdf_produced_pagecount >/dev/null; then
        echo -e "${RED}✗${NC} could not source module / pdf_produced_pagecount undefined"
        exit 1
    fi

    test_pagecount_from_log_multipage
    test_pagecount_from_log_single_page
    test_pagecount_zero_when_no_output_line
    test_pagecount_zero_when_no_log

    echo "========================================"
    echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
    [ $TESTS_FAILED -gt 0 ] && exit 1
    exit 0
}

main "$@"

# EOF
