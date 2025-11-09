#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-10 01:40:00 (ywatanabe)"
# File: ./tests/run_all_tests.sh
# Description: Master test runner for all tests (Python + Shell)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "SciTeX Writer - Master Test Suite"
echo -e "==========================================${NC}"
echo

TOTAL_FAILED=0

# Run Shell Script Tests
echo -e "${BLUE}[1/2] Running Shell Script Tests${NC}"
echo "--------------------------------------"
if ./tests/scripts/run_all_tests.sh; then
    echo -e "${GREEN}✓ All shell script tests passed${NC}"
else
    echo -e "${RED}✗ Some shell script tests failed${NC}"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi
echo

# Run Python Tests
echo -e "${BLUE}[2/2] Running Python Tests${NC}"
echo "--------------------------------------"
if python -m pytest tests/scitex/writer/ -v --tb=short; then
    echo -e "${GREEN}✓ All Python tests passed${NC}"
else
    echo -e "${RED}✗ Some Python tests failed${NC}"
    TOTAL_FAILED=$((TOTAL_FAILED + 1))
fi
echo

# Summary
echo -e "${BLUE}=========================================="
if [ $TOTAL_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All Test Suites Passed!${NC}"
    echo -e "${BLUE}==========================================${NC}"
    exit 0
else
    echo -e "${RED}✗ $TOTAL_FAILED Test Suite(s) Failed!${NC}"
    echo -e "${BLUE}==========================================${NC}"
    exit 1
fi

# EOF
