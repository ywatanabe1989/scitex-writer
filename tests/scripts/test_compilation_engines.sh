#!/bin/bash
# -*- coding: utf-8 -*-
# Test: Compilation Engines (latexmk, 3pass, tectonic)
# Timestamp: "$(date +"%Y-%m-%d %H:%M:%S") ($(whoami))"
# File: ./tests/scripts/test_compilation_engines.sh

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
        echo -e "${GREEN}✓ PASS: $test_name - File exists: $file_path${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL: $test_name - File not found: $file_path${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

assert_string_in_log() {
    local test_name="$1"
    local log_file="$2"
    local search_string="$3"

    if grep -q "$search_string" "$log_file" 2>/dev/null; then
        echo -e "${GREEN}✓ PASS: $test_name - Found: '$search_string'${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL: $test_name - Not found: '$search_string'${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Main tests
echo "========================================"
echo "Testing Compilation Engines"
echo "========================================"
echo ""

# Test 1: latexmk engine
print_test "latexmk compilation"
rm -f ./01_manuscript/manuscript.pdf
export SCITEX_WRITER_ENGINE=latexmk
./compile.sh manuscript >/tmp/test_latexmk.log 2>&1
assert_success "latexmk execution" $?
assert_file_exists "latexmk PDF output" "./01_manuscript/manuscript.pdf"
assert_string_in_log "latexmk engine selected" "/tmp/test_latexmk.log" "latexmk compilation:"
echo ""

# Test 2: 3pass engine
print_test "3pass compilation"
rm -f ./01_manuscript/manuscript.pdf
export SCITEX_WRITER_ENGINE=3pass
./compile.sh manuscript >/tmp/test_3pass.log 2>&1
assert_success "3pass execution" $?
assert_file_exists "3pass PDF output" "./01_manuscript/manuscript.pdf"
assert_string_in_log "3pass engine selected" "/tmp/test_3pass.log" "3-pass compilation:"
echo ""

# Test 3: tectonic engine
print_test "tectonic compilation"
rm -f ./01_manuscript/manuscript.pdf
export SCITEX_WRITER_ENGINE=tectonic
./compile.sh manuscript >/tmp/test_tectonic.log 2>&1
assert_success "tectonic execution" $?
assert_file_exists "tectonic PDF output" "./01_manuscript/manuscript.pdf"
assert_string_in_log "tectonic engine selected" "/tmp/test_tectonic.log" "Tectonic compilation:"
# Note: Check source for absolute paths feature (message printed during figure processing, not main log)
assert_string_in_log "tectonic absolute paths code" "./scripts/shell/modules/process_figures_modules/04_compilation.src" "Using absolute paths for tectonic engine"
echo ""

# Test 4: auto engine selection
print_test "auto engine selection"
rm -f ./01_manuscript/manuscript.pdf
unset SCITEX_WRITER_ENGINE
export SCITEX_WRITER_SELECTED_ENGINE=""
./compile.sh manuscript >/tmp/test_auto.log 2>&1
assert_success "auto selection execution" $?
assert_file_exists "auto selection PDF output" "./01_manuscript/manuscript.pdf"
assert_string_in_log "auto engine detection" "/tmp/test_auto.log" "Auto-detected engine:"
echo ""

# Test 5: Verify refactored process_figures works
print_test "refactored process_figures.sh"
assert_file_exists "process_figures exists" "./scripts/shell/modules/process_figures.sh"
assert_string_in_log "process_figures modular" "./scripts/shell/modules/process_figures.sh" "Refactored modular version"
assert_file_exists "caption module exists" "./scripts/shell/modules/process_figures_modules/01_caption_management.src"
assert_file_exists "compilation module exists" "./scripts/shell/modules/process_figures_modules/04_compilation.src"
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
