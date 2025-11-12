#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-10 01:38:00 (ywatanabe)"
# File: ./tests/scripts/run_all_tests.sh
# Description: Run all shell script tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}======================================"
echo "Running All Shell Script Tests"
echo -e "======================================${NC}"
echo

TOTAL_FAILED=0

# Find all test scripts
for test_script in "$SCRIPT_DIR"/test_*.sh; do
    if [ -f "$test_script" ] && [ -x "$test_script" ]; then
        echo -e "${BLUE}Running: $(basename $test_script)${NC}"
        echo "--------------------------------------"

        if bash "$test_script"; then
            echo -e "${GREEN}✓ $(basename $test_script) passed${NC}"
        else
            echo -e "${RED}✗ $(basename $test_script) failed${NC}"
            TOTAL_FAILED=$((TOTAL_FAILED + 1))
        fi
        echo
    fi
done

echo -e "${BLUE}======================================"
if [ $TOTAL_FAILED -eq 0 ]; then
    echo -e "${GREEN}All test suites passed!${NC}"
    echo -e "${BLUE}======================================${NC}"
    exit 0
else
    echo -e "${RED}$TOTAL_FAILED test suite(s) failed!${NC}"
    echo -e "${BLUE}======================================${NC}"
    exit 1
fi

# EOF
