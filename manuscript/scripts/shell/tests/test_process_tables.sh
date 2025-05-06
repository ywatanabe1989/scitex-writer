#!/bin/bash
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
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
MODULES_DIR="${THIS_DIR}/../modules"
TEST_TMP_DIR="${THIS_DIR}/tmp_test_process_tables"

# Create test environment
setup_test_env() {
    mkdir -p "${TEST_TMP_DIR}"
    mkdir -p "${TEST_TMP_DIR}/src/tables/src"
    mkdir -p "${TEST_TMP_DIR}/src/tables/compiled"
    mkdir -p "${TEST_TMP_DIR}/src/tables/.tex"
    mkdir -p "${TEST_TMP_DIR}/scripts/shell/modules"
    
    # Create a sample CSV file
    cat > "${TEST_TMP_DIR}/src/tables/src/Table_ID_01_test.csv" << EOF
Column1,Column2,Column3
1,2,3
4,5,6
7,8,9
EOF
    
    # Create a sample caption file
    cat > "${TEST_TMP_DIR}/src/tables/src/Table_ID_01_test.tex" << EOF
\caption{
\textbf{Test Table Title.}
\smallskip
\\
Test table caption.
}
% width=0.8\textwidth
EOF

    # Create a template file
    cat > "${TEST_TMP_DIR}/src/tables/src/_Table_ID_XX.tex" << EOF
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
    
    # Create a modified version of config.src for testing
    cat > "${TEST_TMP_DIR}/scripts/shell/modules/config.src" << EOF
#!/bin/bash
# Modified config.src for testing

# Table
TABLE_SRC_DIR="${TEST_TMP_DIR}/src/tables/src"
TABLE_COMPILED_DIR="${TEST_TMP_DIR}/src/tables/compiled"
TABLE_HIDDEN_DIR="${TEST_TMP_DIR}/src/tables/.tex"
EOF

    # Modify paths in the test script
    sed -i "s|source \./scripts/shell/modules/config.src|source ${TEST_TMP_DIR}/scripts/shell/modules/config.src|g" "${TEST_TMP_DIR}/scripts/shell/modules/process_tables_test.sh"
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
        [ -d \"$TABLE_SRC_DIR\" ] && [ -d \"$TABLE_COMPILED_DIR\" ] && [ -d \"$TABLE_HIDDEN_DIR\" ] && [ -f \"$TABLE_HIDDEN_DIR/.All_Tables.tex\" ]
    "
    
    # Test ensure_caption function
    test_function "ensure_caption creates captions when missing" "
        # Create a CSV file without caption
        echo 'A,B,C
1,2,3' > \"$TABLE_SRC_DIR/Table_ID_02_no_caption.csv\"
        
        # Run function
        ensure_caption
        
        # Check if caption file was created
        [ -f \"$TABLE_SRC_DIR/Table_ID_02_no_caption.tex\" ]
    "
    
    # Test ensure_lower_letters function
    test_function "ensure_lower_letters converts filenames to lowercase" "
        # Create a file with uppercase letters
        touch \"$TABLE_SRC_DIR/Table_ID_03_TEST_UPPER.csv\"
        
        # Run function
        ensure_lower_letters
        
        # Check if file was renamed
        [ -f \"$TABLE_SRC_DIR/Table_ID_03_test_upper.csv\" ] && [ ! -f \"$TABLE_SRC_DIR/Table_ID_03_TEST_UPPER.csv\" ]
    "
    
    # Test csv2tex function
    test_function "csv2tex converts CSV files to LaTeX tables" "
        # Run function
        csv2tex
        
        # Check if TEX file was created
        [ -f \"$TABLE_COMPILED_DIR/Table_ID_01_test.tex\" ] && 
        grep -q '\\\\begin{table}' \"$TABLE_COMPILED_DIR/Table_ID_01_test.tex\" &&
        grep -q '\\\\begin{tabular}' \"$TABLE_COMPILED_DIR/Table_ID_01_test.tex\" &&
        grep -q '\\\\input{' \"$TABLE_COMPILED_DIR/Table_ID_01_test.tex\"
    "
    
    # Test gather_tex_files function
    test_function "gather_tex_files creates aggregate file" "
        # Clear the all tables file
        echo '' > \"$TABLE_HIDDEN_DIR/.All_Tables.tex\"
        
        # Run function
        gather_tex_files
        
        # Check if the file contains the reference to the compiled table
        grep -q 'Table_ID_01_test' \"$TABLE_HIDDEN_DIR/.All_Tables.tex\"
    "
    
    # Test main function
    test_function "main function runs without errors" "
        # Remove all generated files
        rm -f \"$TABLE_COMPILED_DIR\"/*.tex \"$TABLE_HIDDEN_DIR\"/.All_Tables.tex
        
        # Run main function
        main > /dev/null 2>&1
        
        # Check if all files were created
        [ -f \"$TABLE_COMPILED_DIR/Table_ID_01_test.tex\" ] && 
        [ -f \"$TABLE_HIDDEN_DIR/.All_Tables.tex\" ] && 
        grep -q 'Table_ID_01_test' \"$TABLE_HIDDEN_DIR/.All_Tables.tex\"
    "
}

# Run the tests
setup_test_env
run_tests
cleanup_test_env

echo "Process tables tests completed."