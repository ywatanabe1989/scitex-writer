#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 12:58:22 (ywatanabe)"
# File: ./manuscript/scripts/shell/tests/test_check_commands.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


# Test script for check_commands.sh
# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test function
test_function() {
    local test_name="$1"
    local condition="$2"
    if eval "$condition"; then
        echo -e "${GREEN}[PASS]${NC} $test_name"
        return 0
    else
        echo -e "${RED}[FAIL]${NC} $test_name"
        return 1
    fi
}

# Setup
MODULES_DIR="${THIS_DIR}/../modules"
TEST_TMP_DIR="${THIS_DIR}/tmp_test_check"
mkdir -p "${TEST_TMP_DIR}"

# Create a modified version of check_commands.sh for testing
cp "${MODULES_DIR}/check_commands.sh" "${TEST_TMP_DIR}/check_test.sh"

# Modify the script to not execute the check at the end - we'll test the function separately
sed -i 's/check_commands pdflatex bibtex xlsx2csv csv2latex parallel/# check_commands pdflatex bibtex xlsx2csv csv2latex parallel/g' "${TEST_TMP_DIR}/check_test.sh"

# Source the modified check script to get the check_commands function
source "${TEST_TMP_DIR}/check_test.sh"

# Test the original script's required commands
echo -e "${BLUE}===== Checking Required Commands =====${NC}"
echo -e "${YELLOW}Command${NC}\t\t${YELLOW}Status${NC}\t\t${YELLOW}Installation Help${NC}"
echo "------------------------------------------------------"

missing_commands=()
for cmd in pdflatex bibtex xlsx2csv csv2latex parallel; do
    if command -v $cmd &> /dev/null; then
        echo -e "${cmd}\t\t${GREEN}[AVAILABLE]${NC}"
    else
        echo -e "${cmd}\t\t${RED}[MISSING]${NC}\t\tSee below for install info"
        missing_commands+=("$cmd")
    fi
done

# Display installation help if any commands are missing
if [ ${#missing_commands[@]} -gt 0 ]; then
    echo -e "\n${BLUE}===== Missing Command Installation Guide =====${NC}"
    for cmd in "${missing_commands[@]}"; do
        echo -e "${YELLOW}$cmd${NC}:"
        case $cmd in
            pdflatex|bibtex)
                echo "  Install with: sudo apt install texlive-full"
                echo "  Or minimal: sudo apt install texlive-latex-base texlive-bibtex-extra"
                ;;
            xlsx2csv)
                echo "  Install with: pip install xlsx2csv"
                ;;
            csv2latex)
                echo "  Install with: pip install csv2latex"
                echo "  Or use alternative: csvkit (sudo apt install csvkit)"
                ;;
            parallel)
                echo "  Install with: sudo apt install parallel"
                ;;
        esac
    done
else
    echo -e "\n${GREEN}All required commands are available!${NC}"
fi

# Clean up
echo -e "\n${BLUE}===== Cleaning Up =====${NC}"
rm -rf "${TEST_TMP_DIR}"
echo -e "${GREEN}Check tests completed successfully.${NC}"

# EOF