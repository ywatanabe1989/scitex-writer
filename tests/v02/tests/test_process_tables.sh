#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 23:53:40 (ywatanabe)"
# File: ./manuscript/scripts/shell/tests/test_process_tables.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


# Test script for process_tables.sh

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
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
TEST_TMP_DIR="${THIS_DIR}/tmp_test_process_tables"

# Create test environment
setup_test_env() {
    mkdir -p "${TEST_TMP_DIR}"
    mkdir -p "${TEST_TMP_DIR}/contents/tables/contents"
    mkdir -p "${TEST_TMP_DIR}/contents/tables/compiled"
    mkdir -p "${TEST_TMP_DIR}/contents/tables/.tex"
    mkdir -p "${TEST_TMP_DIR}/scripts/shell/modules"

    # Create a sample CSV file
    cat > "${TEST_TMP_DIR}/contents/tables/contents/.01_test.csv" << EOF
Column1,Column2,Column3
1,2,3
4,5,6
7,8,9
EOF

    # Create a sample caption file
    cat > "${TEST_TMP_DIR}/contents/tables/contents/.01_test.tex" << EOF
\caption{
\textbf{Test Table Title.}
\smallskip
\\
Test table caption.
}
% width=0.8\textwidth
EOF

    # Create a template file
    cat > "${TEST_TMP_DIR}/contents/tables/contents/_.XX.tex" << EOF
\caption{
\textbf{TITLE HERE.}
\smallskip
\\
CAPTION HERE.
}
% width=0.8\textwidth
EOF

    # Create a modified version of process_tables.sh for testing
    cp "${MODULES_DIR}/process_tables.sh" "${TEST_TMP_DIR}/scripts/shell/modules/process_tables_test.sh"

    # Create a modified version of load_config.sh for testing
    cat > "${TEST_TMP_DIR}/scripts/shell/modules/load_config.sh" << EOF
# Modified load_config.sh for testing

# Table
STXW_TABLE_CAPTION_MEDIA_DIR="${TEST_TMP_DIR}/contents/tables/contents"
STXW_TABLE_COMPILED_DIR="${TEST_TMP_DIR}/contents/tables/compiled"
TABLE_HIDDEN_DIR="${TEST_TMP_DIR}/contents/tables/.tex"
EOF

    # Modify paths in the test script
    sed -i "s|source \./scripts/shell/modules/load_config.sh|source ${TEST_TMP_DIR}/scripts/shell/modules/load_config.sh|g" "${TEST_TMP_DIR}/scripts/shell/modules/process_tables_test.sh"
}

# Clean up test environment
cleanup_test_env() {
    echo "Cleaning up test environment..."
    rm -rf "${TEST_TMP_DIR}"
}

# Main test function
run_tests() {
    echo "Testing process_tables.sh..."

    # Source the modified script to test its functions
    cd "${TEST_TMP_DIR}"
    source "${TEST_TMP_DIR}/scripts/shell/modules/process_tables_test.sh"

    # Test initialization
    test_function "init function creates required directories" "
        init
        [ -d \"$STXW_TABLE_CAPTION_MEDIA_DIR\" ] && [ -d \"$STXW_TABLE_COMPILED_DIR\" ] && [ -d \"$TABLE_HIDDEN_DIR\" ] && [ -f \"$TABLE_HIDDEN_DIR/.All_Tables.tex\" ]
    "

    # Test ensure_caption function
    test_function "ensure_caption creates captions when missing" "
        # Create a CSV file without caption
        echo 'A,B,C
1,2,3' > \"$STXW_TABLE_CAPTION_MEDIA_DIR/.02_no_caption.csv\"

        # Run function
        ensure_caption

        # Check if caption file was created
        [ -f \"$STXW_TABLE_CAPTION_MEDIA_DIR/.02_no_caption.tex\" ]
    "

    # Test ensure_lower_letters function
    test_function "ensure_lower_letters converts filenames to lowercase" "
        # Create a file with uppercase letters
        touch \"$STXW_TABLE_CAPTION_MEDIA_DIR/.03_TEST_UPPER.csv\"

        # Run function
        ensure_lower_letters

        # Check if file was renamed
        [ -f \"$STXW_TABLE_CAPTION_MEDIA_DIR/.03_test_upper.csv\" ] && [ ! -f \"$STXW_TABLE_CAPTION_MEDIA_DIR/.03_TEST_UPPER.csv\" ]
    "

    # Test csv2tex function
    test_function "csv2tex converts CSV files to LaTeX tables" "
        # Run function
        csv2tex

        # Check if TEX file was created
        [ -f \"$STXW_TABLE_COMPILED_DIR/.01_test.tex\" ] &&
        grep -q '\\\\begin{table}' \"$STXW_TABLE_COMPILED_DIR/.01_test.tex\" &&
        grep -q '\\\\begin{tabular}' \"$STXW_TABLE_COMPILED_DIR/.01_test.tex\" &&
        grep -q '\\\\input{' \"$STXW_TABLE_COMPILED_DIR/.01_test.tex\"
    "

    # Test gather_tex_files function
    test_function "gather_tex_files creates aggregate file" "
        # Clear the all tables file
        echo '' > \"$TABLE_HIDDEN_DIR/.All_Tables.tex\"

        # Run function
        gather_tex_files

        # Check if the file contains the reference to the compiled table
        grep -q '.01_test' \"$TABLE_HIDDEN_DIR/.All_Tables.tex\"
    "

    # Test main function
    test_function "main function runs without errors" "
        # Remove all generated files
        rm -f \"$STXW_TABLE_COMPILED_DIR\"/*.tex \"$TABLE_HIDDEN_DIR\"/.All_Tables.tex

        # Run main function
        main > /dev/null 2>&1

        # Check if all files were created
        [ -f \"$STXW_TABLE_COMPILED_DIR/.01_test.tex\" ] &&
        [ -f \"$TABLE_HIDDEN_DIR/.All_Tables.tex\" ] &&
        grep -q '.01_test' \"$TABLE_HIDDEN_DIR/.All_Tables.tex\"
    "
}

# Run the tests
setup_test_env
run_tests
cleanup_test_env

echo "Process tables tests completed."

# EOF