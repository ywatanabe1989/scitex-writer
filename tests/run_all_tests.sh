#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-11 06:33:49 (ywatanabe)"
# File: ./tests/run_all_tests.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------
# Description: Master test runner for all tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

# Colors
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo "SciTeX Writer - Master Test Suite"
echo -e "==========================================${NC}"
echo

TOTAL_FAILED=0

# Run Shell Script Tests
echo -e "${BLUE} Running Shell Script Tests${NC}"
echo "--------------------------------------"
if ./tests/scripts/run_all_tests.sh; then
    echo -e "${GREEN}✓ All shell script tests passed${NC}"
else
    echo -e "${RED}✗ Some shell script tests failed${NC}"
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