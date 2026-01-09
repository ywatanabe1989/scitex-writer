#!/bin/bash
# -*- coding: utf-8 -*-
# Test: All Document Types (manuscript, supplementary, revision)
# Timestamp: "$(date +"%Y-%m-%d %H:%M:%S") ($(whoami))"
# File: ./tests/scripts/test_document_types.sh

# NOTE: Removed set -e because assert functions need to track failures without exiting

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

print_test() {
    echo -e "${YELLOW}TEST: $1${NC}"
}

assert_success() {
    local test_name="$1"
    local exit_code="$2"

    if [ "$exit_code" -eq 0 ]; then
        echo -e "${GREEN}✓ PASS: $test_name${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL: $test_name (exit code: $exit_code)${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_file_exists() {
    local test_name="$1"
    local file_path="$2"

    if [ -f "$file_path" ]; then
        echo -e "${GREEN}✓ PASS: $test_name - File exists${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL: $test_name - File not found: $file_path${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Optional file check - doesn't count as failure if missing (for diff PDFs in fresh clones)
assert_file_exists_optional() {
    local test_name="$1"
    local file_path="$2"

    if [ -f "$file_path" ]; then
        echo -e "${GREEN}✓ PASS: $test_name - File exists${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${YELLOW}⚠ SKIP: $test_name - No previous version for diff${NC}"
        ((TESTS_PASSED++))
        return 0
    fi
}

# Main tests
echo "========================================"
echo "Testing All Document Types"
echo "========================================"
echo ""

# Use latexmk for fast testing
export SCITEX_WRITER_ENGINE=latexmk

# Test 1-3: All document types in parallel
print_test "all document types (parallel)"

# Clean PDFs
rm -f ./01_manuscript/manuscript.pdf
rm -f ./02_supplementary/supplementary.pdf
rm -f ./03_revision/revision.pdf

# Create temp dir for exit codes
temp_dir=$(mktemp -d)

# Run all three in parallel
(
    ./compile.sh manuscript >/tmp/test_manuscript.log 2>&1
    echo $? >"$temp_dir/manuscript_exit"
) &
manuscript_pid=$!

(
    ./compile.sh supplementary >/tmp/test_supplementary.log 2>&1
    echo $? >"$temp_dir/supplementary_exit"
) &
supplementary_pid=$!

(
    ./compile.sh revision >/tmp/test_revision.log 2>&1
    echo $? >"$temp_dir/revision_exit"
) &
revision_pid=$!

# Wait for all to complete
wait $manuscript_pid $supplementary_pid $revision_pid

# Check results
manuscript_exit=$(cat "$temp_dir/manuscript_exit")
supplementary_exit=$(cat "$temp_dir/supplementary_exit")
revision_exit=$(cat "$temp_dir/revision_exit")

rm -rf "$temp_dir"

# Assert success for each
assert_success "manuscript compilation" "$manuscript_exit"
assert_file_exists "manuscript PDF" "./01_manuscript/manuscript.pdf"
assert_file_exists_optional "manuscript diff PDF" "./01_manuscript/manuscript_diff.pdf"

assert_success "supplementary compilation" "$supplementary_exit"
assert_file_exists "supplementary PDF" "./02_supplementary/supplementary.pdf"
assert_file_exists_optional "supplementary diff PDF" "./02_supplementary/supplementary_diff.pdf"

assert_success "revision compilation" "$revision_exit"
assert_file_exists "revision PDF" "./03_revision/revision.pdf"
echo ""

# Test 4: All engines with manuscript
print_test "all engines (manuscript)"
for engine in latexmk 3pass tectonic; do
    rm -f ./01_manuscript/manuscript.pdf
    export SCITEX_WRITER_ENGINE=$engine
    ./compile.sh manuscript >/tmp/test_engine_$engine.log 2>&1
    assert_success "$engine engine (manuscript)" $?
done
echo ""

# Summary
echo "========================================"
echo "Test Summary"
echo "========================================"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi

# EOF
