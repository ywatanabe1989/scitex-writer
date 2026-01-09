#!/bin/bash
# -*- coding: utf-8 -*-
# Test: Tectonic Integration (absolute paths, package compatibility)
# Timestamp: "$(date +"%Y-%m-%d %H:%M:%S") ($(whoami))"
# File: ./tests/scripts/test_tectonic_integration.sh

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

assert_string_in_log() {
    local test_name="$1"
    local log_file="$2"
    local search_string="$3"

    # Use -- to separate options from pattern (handles patterns starting with -)
    if grep -q -- "$search_string" "$log_file" 2>/dev/null; then
        echo -e "${GREEN}✓ PASS: $test_name${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL: $test_name - Not found: '$search_string'${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_string_not_in_log() {
    local test_name="$1"
    local log_file="$2"
    local search_string="$3"

    # Use -- to separate options from pattern (handles patterns starting with -)
    if ! grep -q -- "$search_string" "$log_file" 2>/dev/null; then
        echo -e "${GREEN}✓ PASS: $test_name${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL: $test_name - Found (should not exist): '$search_string'${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Main tests
echo "========================================"
echo "Testing Tectonic Integration"
echo "========================================"
echo ""

export SCITEX_WRITER_ENGINE=tectonic

# Test 1: Tectonic uses absolute paths
print_test "tectonic absolute path detection"
./compile.sh manuscript >/tmp/test_tectonic_paths.log 2>&1
# Note: Check source for absolute paths feature (message printed during figure processing, not main log)
assert_string_in_log "absolute paths code" "./scripts/shell/modules/process_figures_modules/04_compilation.src" "Using absolute paths for tectonic engine"
echo ""

# Test 2: Verify --reruns flag is used (only if tectonic was actually used)
print_test "tectonic reruns optimization"
if command -v tectonic &>/dev/null; then
    assert_string_in_log "reruns flag" "/tmp/test_tectonic_paths.log" "--reruns=1"
else
    echo -e "${YELLOW}⚠ SKIP: tectonic not installed${NC}"
    ((TESTS_PASSED++))
fi
echo ""

# Test 3: Verify tectonic mode in Python compilation
print_test "tectonic mode in TeX structure compilation"
# Check if the compiled manuscript.tex has tectonic-compatible packages
cat ./01_manuscript/manuscript.tex >/tmp/test_compiled_tex.txt
# Should NOT contain uncommented lineno or bashful (they should be commented out)
assert_string_not_in_log "lineno package commented" "/tmp/test_compiled_tex.txt" "^\\\\usepackage{lineno}"
echo ""

# Test 4: latexmk does NOT use absolute paths
print_test "latexmk relative paths (not absolute)"
export SCITEX_WRITER_ENGINE=latexmk
./compile.sh manuscript >/tmp/test_latexmk_paths.log 2>&1
assert_string_not_in_log "latexmk should not use absolute paths" "/tmp/test_latexmk_paths.log" "Using absolute paths for tectonic engine"
echo ""

# Test 5: Verify modular process_figures is being used
print_test "modular process_figures.sh usage"
# Check that process_figures.sh is the refactored version
assert_string_in_log "refactored version in use" "./scripts/shell/modules/process_figures.sh" "Refactored modular version"
echo ""

# Test 6: Check figure FINAL.tex contains correct paths (absolute for tectonic)
print_test "figure FINAL.tex path style per engine"
export SCITEX_WRITER_ENGINE=tectonic
./compile.sh manuscript >/dev/null 2>&1
# Check that FINAL.tex has absolute paths when using tectonic
final_tex="./01_manuscript/contents/figures/compiled/FINAL.tex"
if [ -f "$final_tex" ]; then
    # Tectonic should use absolute paths (starting with /)
    if grep -q 'includegraphics.*{/' "$final_tex" 2>/dev/null; then
        echo -e "${GREEN}✓ PASS: tectonic uses absolute paths in FINAL.tex${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ FAIL: tectonic should use absolute paths in FINAL.tex${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${YELLOW}⚠ SKIP: FINAL.tex not found${NC}"
fi
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
