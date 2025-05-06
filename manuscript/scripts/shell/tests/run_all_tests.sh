#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 12:58:22 (ywatanabe)"
# File: ./manuscript/scripts/shell/tests/run_all_tests.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


# Master test script to run all module tests
# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get directory of this script

# Make all test scripts executable
chmod +x "${THIS_DIR}"/*.sh

# Print header
echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}Running all SciTex module tests${NC}"
echo -e "${BLUE}===================================${NC}"
echo ""

# Track test results
PASS_COUNT=0
FAIL_COUNT=0
TOTAL_COUNT=0

# Function to run a test script and count results
run_test() {
    local test_script="$1"
    local script_name=$(basename "$test_script")
    echo -e "${YELLOW}Running $script_name...${NC}"

    # Run the test script directly
    bash "$test_script"

    # Check the exit code
    if [ $? -eq 0 ]; then
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    TOTAL_COUNT=$((TOTAL_COUNT + 1))

    echo -e "${YELLOW}$script_name completed${NC}"
    echo ""
}

# Run each test script
for test_script in "${THIS_DIR}"/test_*.sh; do
    # Skip running self
    if [[ "$test_script" != "${BASH_SOURCE[0]}" ]]; then
        run_test "$test_script"
    fi
done

# Print summary
echo -e "${BLUE}===================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}===================================${NC}"
echo -e "Total tests: ${TOTAL_COUNT}"
echo -e "${GREEN}Passed: ${PASS_COUNT}${NC}"
echo -e "${RED}Failed: ${FAIL_COUNT}${NC}"

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check the output above for details.${NC}"
    exit 1
fi

# EOF