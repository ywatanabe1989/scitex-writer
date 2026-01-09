#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-10 01:37:00 (ywatanabe)"
# File: ./tests/scripts/test_dark_mode.sh
# Description: Test dark mode functionality

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

TESTS_RUN=0
TESTS_PASSED=0

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    TESTS_RUN=$((TESTS_RUN + 1))
}

echo "Dark Mode Functionality Tests"
echo "=============================="

# Test 1: Dark mode style file exists
echo
echo "Test 1: Dark mode LaTeX style file"
if [ -f "./00_shared/latex_styles/dark_mode.tex" ]; then
    test_pass "Dark mode style file exists"
else
    test_fail "Dark mode style file not found"
    exit 1
fi

# Test 2: Style file contains pagecolor
echo
echo "Test 2: Background color settings"
if grep -q "\\\\pagecolor{black" "./00_shared/latex_styles/dark_mode.tex"; then
    test_pass "Background color (pagecolor) defined"
else
    test_fail "Missing background color"
fi

# Test 3: Style file contains text color
echo
echo "Test 3: Text color settings"
if grep -q "\\\\color{white}" "./00_shared/latex_styles/dark_mode.tex"; then
    test_pass "Text color defined"
else
    test_fail "Missing text color"
fi

# Test 4: Hyperlink colors adjusted
echo
echo "Test 4: Hyperlink colors for dark mode"
if grep -q "hypersetup" "./00_shared/latex_styles/dark_mode.tex" &&
    grep -q "linkcolor" "./00_shared/latex_styles/dark_mode.tex"; then
    test_pass "Hyperlink colors adjusted for dark mode"
else
    test_fail "Missing hyperlink color adjustments"
fi

# Test 5: Section title colors adjusted
echo
echo "Test 5: Section title colors"
if grep -q "\\\\titleformat" "./00_shared/latex_styles/dark_mode.tex"; then
    test_pass "Section title colors adjusted"
else
    test_fail "Missing section title color adjustments"
fi

# Test 6: Python script supports dark mode
echo
echo "Test 6: Python compile script dark mode support"
if grep -q "dark_mode" "./scripts/python/compile_tex_structure.py"; then
    test_pass "Python script supports dark_mode parameter"
else
    test_fail "Python script missing dark_mode support"
fi

# Test 7: Dark mode injection logic exists
echo
echo "Test 7: Dark mode style injection"
if grep -q "dark_mode.tex" "./scripts/python/compile_tex_structure.py"; then
    test_pass "Dark mode style injection implemented"
else
    test_fail "Dark mode injection missing"
fi

# Test 8: Environment variable support
echo
echo "Test 8: Environment variable support"
if grep -q "SCITEX_WRITER_DARK_MODE" "./scripts/python/compile_tex_structure.py"; then
    test_pass "Supports SCITEX_WRITER_DARK_MODE env variable"
else
    test_fail "Missing env variable support"
fi

# Test 9: All compile scripts export DARK_MODE
echo
echo "Test 9: Compile scripts export dark mode variable"
EXPORT_COUNT=0
for script in ./scripts/shell/compile_{manuscript,supplementary,revision}.sh; do
    if grep -q "export SCITEX_WRITER_DARK_MODE" "$script"; then
        EXPORT_COUNT=$((EXPORT_COUNT + 1))
    fi
done

if [ $EXPORT_COUNT -eq 3 ]; then
    test_pass "All 3 compile scripts export DARK_MODE variable"
else
    test_fail "Only $EXPORT_COUNT/3 scripts export DARK_MODE"
fi

# Test 10: Option parsing supports both formats
echo
echo "Test 10: Dark mode option parsing"
PARSE_COUNT=0
for script in ./scripts/shell/compile_{manuscript,supplementary,revision}.sh; do
    # Check for the actual pattern: -dm | --dark-mode (with spaces)
    if grep -q "\-dm.*--dark-mode" "$script"; then
        PARSE_COUNT=$((PARSE_COUNT + 1))
    fi
done

if [ $PARSE_COUNT -eq 3 ]; then
    test_pass "All 3 scripts parse -dm and --dark-mode"
else
    test_fail "Only $PARSE_COUNT/3 scripts parse dark mode option"
fi

echo
echo "=============================="
echo "Test Results:"
echo "  Total:  $TESTS_RUN"
echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "  Failed: $((TESTS_RUN - TESTS_PASSED))"
echo "=============================="

if [ $TESTS_PASSED -eq $TESTS_RUN ]; then
    echo -e "${GREEN}All dark mode tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi

# EOF
