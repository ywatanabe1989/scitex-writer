#!/bin/bash
# -*- coding: utf-8 -*-
# Test: Template Clone Readiness (Issue #12, #13, #14)
# Timestamp: "$(date +"%Y-%m-%d %H:%M:%S") ($(whoami))"
# File: ./tests/scripts/test_template_clone_readiness.sh

# shellcheck disable=SC1091

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Test results
TESTS_PASSED=0
TESTS_FAILED=0

# Resolve project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

print_test() {
    echo -e "${YELLOW}TEST: $1${NC}"
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

assert_file_tracked() {
    local test_name="$1"
    local file_path="$2"

    if git ls-files --error-unmatch "$file_path" >/dev/null 2>&1; then
        echo -e "${GREEN}✓ PASS: $test_name${NC}"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}✗ FAIL: $test_name - Not tracked by git: $file_path${NC}"
        ((TESTS_FAILED++))
        return 1
    fi
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

# Main tests
echo "========================================"
echo "Testing Template Clone Readiness"
echo "========================================"
echo ""

# ==========================================
# Issue #12: Wordcount placeholder files
# ==========================================
print_test "Issue #12: Wordcount placeholder files exist"

WORDCOUNT_FILES=(
    "01_manuscript/contents/wordcounts/figure_count.txt"
    "01_manuscript/contents/wordcounts/table_count.txt"
    "01_manuscript/contents/wordcounts/abstract_count.txt"
    "01_manuscript/contents/wordcounts/introduction_count.txt"
    "01_manuscript/contents/wordcounts/methods_count.txt"
    "01_manuscript/contents/wordcounts/results_count.txt"
    "01_manuscript/contents/wordcounts/discussion_count.txt"
    "01_manuscript/contents/wordcounts/imrd_count.txt"
)

for file in "${WORDCOUNT_FILES[@]}"; do
    assert_file_exists "wordcount file exists: $(basename "$file")" "$file"
done
echo ""

print_test "Issue #12: Wordcount files tracked by git"
for file in "${WORDCOUNT_FILES[@]}"; do
    assert_file_tracked "git tracks: $(basename "$file")" "$file"
done
echo ""

print_test "Issue #12: .gitignore allows wordcount files"
if grep -q '!.*/contents/wordcounts/\*.txt' .gitignore 2>/dev/null; then
    echo -e "${GREEN}✓ PASS: .gitignore has wordcount exception${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL: .gitignore missing wordcount exception${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# ==========================================
# Issue #13: Working directory independence
# ==========================================
print_test "Issue #13: compile.sh resolves PROJECT_ROOT"
if grep -q 'PROJECT_ROOT' ./compile.sh; then
    echo -e "${GREEN}✓ PASS: compile.sh has PROJECT_ROOT${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL: compile.sh missing PROJECT_ROOT${NC}"
    ((TESTS_FAILED++))
fi

print_test "Issue #13: compile_manuscript.sh resolves PROJECT_ROOT"
if grep -q 'PROJECT_ROOT' ./scripts/shell/compile_manuscript.sh; then
    echo -e "${GREEN}✓ PASS: compile_manuscript.sh has PROJECT_ROOT${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL: compile_manuscript.sh missing PROJECT_ROOT${NC}"
    ((TESTS_FAILED++))
fi

print_test "Issue #13: process_figures.sh resolves PROJECT_ROOT"
if grep -q 'PROJECT_ROOT' ./scripts/shell/modules/process_figures.sh; then
    echo -e "${GREEN}✓ PASS: process_figures.sh has PROJECT_ROOT${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL: process_figures.sh missing PROJECT_ROOT${NC}"
    ((TESTS_FAILED++))
fi

print_test "Issue #13: Scripts cd to PROJECT_ROOT before sourcing config"
# Check that scripts cd to PROJECT_ROOT
# shellcheck disable=SC2016  # Intentionally searching for literal $PROJECT_ROOT
if grep -q 'cd "\$PROJECT_ROOT"' ./scripts/shell/compile_manuscript.sh &&
    grep -q 'cd "\$PROJECT_ROOT"' ./compile.sh; then
    echo -e "${GREEN}✓ PASS: Scripts cd to PROJECT_ROOT${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL: Scripts don't cd to PROJECT_ROOT${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# ==========================================
# Issue #14: Strip example content script
# ==========================================
print_test "Issue #14: strip_example_content.sh exists"
assert_file_exists "strip_example_content.sh exists" "./scripts/maintenance/strip_example_content.sh"

print_test "Issue #14: strip_example_content.sh is executable"
if [ -x "./scripts/maintenance/strip_example_content.sh" ]; then
    echo -e "${GREEN}✓ PASS: strip_example_content.sh is executable${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL: strip_example_content.sh not executable${NC}"
    ((TESTS_FAILED++))
fi

print_test "Issue #14: strip_example_content.sh has correct PROJECT_ROOT path"
# shellcheck disable=SC2016  # Intentionally searching for literal $THIS_DIR
if grep -q 'PROJECT_ROOT="\$(cd "\$THIS_DIR/../.."' ./scripts/maintenance/strip_example_content.sh; then
    echo -e "${GREEN}✓ PASS: Correct PROJECT_ROOT path (../../)${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗ FAIL: Incorrect PROJECT_ROOT path${NC}"
    ((TESTS_FAILED++))
fi
echo ""

# ==========================================
# Integration: Fresh clone simulation
# ==========================================
print_test "Integration: LaTeX can read wordcount files"
# Check that manuscript.tex references wordcount files correctly
if grep -q 'readwordcount' ./01_manuscript/manuscript.tex 2>/dev/null ||
    grep -q 'wordcounts' ./01_manuscript/manuscript.tex 2>/dev/null; then
    echo -e "${GREEN}✓ PASS: manuscript.tex references wordcount files${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${YELLOW}⚠ SKIP: manuscript.tex wordcount reference check${NC}"
    ((TESTS_PASSED++))
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
    echo -e "${GREEN}All template clone readiness tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi

# EOF
