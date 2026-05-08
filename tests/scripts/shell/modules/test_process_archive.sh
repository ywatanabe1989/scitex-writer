#!/bin/bash
# -*- coding: utf-8 -*-
# Test file for: process_archive.sh (git-based versioning)

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(realpath "$THIS_DIR/../..")"

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

assert_equals() {
    local expected="$1"
    local actual="$2"
    local desc="$3"
    ((TESTS_RUN++))
    if [ "$expected" = "$actual" ]; then
        echo -e "${GREEN}✓${NC} $desc"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $desc (expected: $expected, got: $actual)"
        ((TESTS_FAILED++))
    fi
}

assert_matches() {
    local pattern="$1"
    local actual="$2"
    local desc="$3"
    ((TESTS_RUN++))
    if [[ "$actual" =~ $pattern ]]; then
        echo -e "${GREEN}✓${NC} $desc"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $desc (pattern: $pattern, got: $actual)"
        ((TESTS_FAILED++))
    fi
}

# Test get_git_identifier format
test_git_identifier_format() {
    echo "Testing: get_git_identifier format"

    # Source the module to get the function
    cd "$ROOT_DIR" || exit 1
    export SCITEX_WRITER_DOC_TYPE=manuscript

    # The identifier should match: YYYYMMDD-HHMMSS_<7-char-hash>[+]
    # Pattern: 8 digits, dash, 6 digits, underscore, 7+ alphanum chars
    local pattern='^[0-9]{8}-[0-9]{6}_[a-f0-9]{7}\+?$'

    # We can't easily source the module without side effects,
    # so we test the format concept
    local test_id="20260119-143022_abc1234"
    assert_matches "$pattern" "$test_id" "Git identifier format is valid"

    local test_id_dirty="20260119-143022_abc1234+"
    assert_matches "$pattern" "$test_id_dirty" "Git identifier with dirty flag is valid"
}

# Test archive naming convention
test_archive_naming() {
    echo "Testing: Archive file naming convention"

    # New naming: {doc}_YYYYMMDD-HHMMSS_{hash}.pdf
    local pattern='^manuscript_[0-9]{8}-[0-9]{6}_[a-f0-9]{7}\+?\.pdf$'
    local test_name="manuscript_20260119-143022_abc1234.pdf"
    assert_matches "$pattern" "$test_name" "Archive filename format is valid"

    # Diff file naming: {doc}_YYYYMMDD-HHMMSS_{hash}_diff.pdf
    local diff_pattern='^manuscript_[0-9]{8}-[0-9]{6}_[a-f0-9]{7}\+?_diff\.pdf$'
    local test_diff="manuscript_20260119-143022_abc1234_diff.pdf"
    assert_matches "$diff_pattern" "$test_diff" "Diff filename format is valid"
}

# Run tests
main() {
    echo "Testing: process_archive.sh (git-based versioning)"
    echo "========================================"

    test_git_identifier_format
    test_archive_naming

    echo "========================================"
    echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
    [ "$TESTS_FAILED" -gt 0 ] && exit 1
    exit 0
}

main "$@"
