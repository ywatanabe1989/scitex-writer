#!/bin/bash
# -*- coding: utf-8 -*-
# Test: Parallel Compilation (All Engines × All Documents)
# Timestamp: "$(date +"%Y-%m-%d %H:%M:%S") ($(whoami))"
# File: ./tests/scripts/test_parallel_compilation.sh

# NOTE: Removed set -e because assert functions need to track failures without exiting

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

print_test() {
    echo -e "${YELLOW}TEST: $1${NC}"
}

print_info() {
    echo -e "${BLUE}INFO: $1${NC}"
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
        echo -e "${GREEN}✓ PASS: $test_name${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL: $test_name - File not found: $file_path${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Main tests
echo "========================================"
echo "Testing Parallel Compilation"
echo "All Engines × All Documents (Safe)"
echo "========================================"
echo ""
echo "NOTE: Engines run sequentially per document type"
echo "      to avoid file conflicts. Only document types"
echo "      are parallelized (safe because they write to"
echo "      different directories)."
echo ""

# Create temp dir for exit codes
temp_dir=$(mktemp -d)

# Start time
start_time=$(date +%s)

# Test each engine with all 3 documents in parallel
for engine in latexmk 3pass tectonic; do
    print_test "all document types with $engine (parallel)"

    # Clean all PDFs
    rm -f ./01_manuscript/manuscript.pdf
    rm -f ./02_supplementary/supplementary.pdf
    rm -f ./03_revision/revision.pdf

    # Run 3 documents in parallel (SAFE - different directories)
    (
        export SCITEX_WRITER_ENGINE=$engine
        ./compile.sh manuscript >/tmp/test_${engine}_manuscript.log 2>&1
        echo $? >"$temp_dir/${engine}_manuscript_exit"
    ) &
    manuscript_pid=$!

    (
        export SCITEX_WRITER_ENGINE=$engine
        ./compile.sh supplementary >/tmp/test_${engine}_supplementary.log 2>&1
        echo $? >"$temp_dir/${engine}_supplementary_exit"
    ) &
    supplementary_pid=$!

    (
        export SCITEX_WRITER_ENGINE=$engine
        ./compile.sh revision >/tmp/test_${engine}_revision.log 2>&1
        echo $? >"$temp_dir/${engine}_revision_exit"
    ) &
    revision_pid=$!

    # Wait for all 3 documents
    wait $manuscript_pid $supplementary_pid $revision_pid

    # Check results
    manuscript_exit=$(cat "$temp_dir/${engine}_manuscript_exit")
    supplementary_exit=$(cat "$temp_dir/${engine}_supplementary_exit")
    revision_exit=$(cat "$temp_dir/${engine}_revision_exit")

    assert_success "$engine: manuscript" "$manuscript_exit"
    assert_success "$engine: supplementary" "$supplementary_exit"
    assert_success "$engine: revision" "$revision_exit"

    # Verify PDFs exist
    assert_file_exists "$engine: manuscript PDF" "./01_manuscript/manuscript.pdf"
    assert_file_exists "$engine: supplementary PDF" "./02_supplementary/supplementary.pdf"
    assert_file_exists "$engine: revision PDF" "./03_revision/revision.pdf"

    echo ""
done

# End time
end_time=$(date +%s)
total_time=$((end_time - start_time))

# Cleanup
rm -rf "$temp_dir"

# Performance summary
echo "========================================"
echo "Performance Summary"
echo "========================================"
echo "Total compilations: 9 (3 engines × 3 documents)"
echo "Strategy:           Parallel by document type (3 at a time)"
echo "                    Sequential by engine (to avoid conflicts)"
echo "Total time:         ${total_time}s"
echo ""
echo "Expected sequential:  ~135s (9 × 15s)"
echo "Actual with parallel: ${total_time}s"
echo "Speedup:              ~$((135 / total_time))x"
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
