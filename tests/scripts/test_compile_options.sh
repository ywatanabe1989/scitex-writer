#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-10 01:35:00 (ywatanabe)"
# File: ./tests/scripts/test_compile_options.sh
# Description: Test compilation options for all document types

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    TESTS_RUN=$((TESTS_RUN + 1))
}

echo "Testing compilation options..."
echo "=============================="

# Test 1: Help option works
echo
echo "Test 1: Help option"
if ./compile.sh -h &>/dev/null; then
    test_pass "Help option works"
else
    test_fail "Help option failed"
fi

# Test 2: Manuscript help shows all options
echo
echo "Test 2: Manuscript help includes new options"
HELP_OUTPUT=$(./compile.sh manuscript -h 2>&1)
if echo "$HELP_OUTPUT" | grep -q "no_figs" &&
    echo "$HELP_OUTPUT" | grep -q "no_tables" &&
    echo "$HELP_OUTPUT" | grep -q "no_diff" &&
    echo "$HELP_OUTPUT" | grep -q "draft" &&
    echo "$HELP_OUTPUT" | grep -q "dark_mode"; then
    test_pass "All new options documented"
else
    test_fail "Missing options in help"
fi

# Test 3: Option name flexibility (hyphens vs underscores)
echo
echo "Test 3: Option name flexibility"
# Just check that both formats are accepted (we won't run full compilation in tests)
HELP_OUTPUT=$(./compile.sh -h 2>&1)
if echo "$HELP_OUTPUT" | grep -q "hyphens and underscores"; then
    test_pass "Documentation mentions flexible naming"
else
    test_fail "Missing flexible naming documentation"
fi

# Test 4: Supplementary script has options
echo
echo "Test 4: Supplementary compilation options"
SUPP_HELP=$(./compile.sh supplementary -h 2>&1)
if echo "$SUPP_HELP" | grep -q "no_figs" &&
    echo "$SUPP_HELP" | grep -q "no_tables" &&
    echo "$SUPP_HELP" | grep -q "draft" &&
    echo "$SUPP_HELP" | grep -q "dark_mode"; then
    test_pass "Supplementary has all speed options"
else
    test_fail "Supplementary missing options"
fi

# Test 5: Revision script has options
echo
echo "Test 5: Revision compilation options"
REV_HELP=$(./compile.sh revision -h 2>&1)
if echo "$REV_HELP" | grep -q "no_figs" &&
    echo "$REV_HELP" | grep -q "no_tables" &&
    echo "$REV_HELP" | grep -q "draft" &&
    echo "$REV_HELP" | grep -q "dark_mode"; then
    test_pass "Revision has speed options"
else
    test_fail "Revision missing options"
fi

# Test 6: Dark mode style file exists
echo
echo "Test 6: Dark mode style file exists"
if [ -f "./00_shared/latex_styles/dark_mode.tex" ]; then
    test_pass "Dark mode style file exists"
else
    test_fail "Dark mode style file missing"
fi

# Test 7: Dark mode style file contains required commands
echo
echo "Test 7: Dark mode style file content"
if grep -q "\\\\pagecolor{black" "./00_shared/latex_styles/dark_mode.tex" &&
    grep -q "\\\\color{white}" "./00_shared/latex_styles/dark_mode.tex"; then
    test_pass "Dark mode has pagecolor and text color settings"
else
    test_fail "Dark mode missing color settings"
fi

# Test 8: Config loading guard exists
echo
echo "Test 8: Config loading optimization"
if grep -q "Skip if already loaded" "./config/load_config.sh" &&
    grep -q "CONFIG_LOADED" "./config/load_config.sh"; then
    test_pass "Config loading guard implemented"
else
    test_fail "Config loading guard missing"
fi

# Test 9: Command caching exists
echo
echo "Test 9: Command caching optimization"
if grep -q "_CACHED_CONTAINER_RUNTIME" "./scripts/shell/modules/command_switching.src" &&
    grep -q "_CACHED_MODULE_AVAILABLE" "./scripts/shell/modules/command_switching.src"; then
    test_pass "Command caching implemented"
else
    test_fail "Command caching missing"
fi

# Test 10: Parallel processing in compile scripts
echo
echo "Test 10: Parallel processing"
# Check for background jobs (&) and wait command - the actual implementation
# Note: Use single quotes to ensure \$ is passed literally to grep
if grep -q ") &" "./scripts/shell/compile_manuscript.sh" &&
    grep -q 'wait \$' "./scripts/shell/compile_manuscript.sh"; then
    test_pass "Parallel processing implemented in manuscript"
else
    test_fail "Parallel processing missing in manuscript"
fi

# Summary
echo
echo "=============================="
echo "Test Results:"
echo "  Total:  $TESTS_RUN"
echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
fi
echo "=============================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi

# EOF
