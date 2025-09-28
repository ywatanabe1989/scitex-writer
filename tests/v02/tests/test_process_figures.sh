#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 23:43:42 (ywatanabe)"
# File: ./manuscript/scripts/shell/tests/test_process_figures.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


# Test script for process_figures.sh

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
TEST_TMP_DIR="${THIS_DIR}/tmp_test_process_figures"

# Create test environment
setup_test_env() {
    mkdir -p "${TEST_TMP_DIR}"
    mkdir -p "${TEST_TMP_DIR}/contents/figures/contents"
    mkdir -p "${TEST_TMP_DIR}/contents/figures/jpg"
    mkdir -p "${TEST_TMP_DIR}/contents/figures/compiled"
    mkdir -p "${TEST_TMP_DIR}/contents/figures/.tex"
    mkdir -p "${TEST_TMP_DIR}/scripts/shell/modules"

    # Create a sample image
    convert -size 100x100 canvas:white "${TEST_TMP_DIR}/contents/figures/contents/.01_test.jpg"

    # Create a sample caption file
    cat > "${TEST_TMP_DIR}/contents/figures/contents/.01_test.tex" << EOF
\caption{\textbf{
Test Figure Title
}
\smallskip
\\
Test figure caption.
}
% width=0.8\textwidth
EOF

    # Create a modified version of process_figures.sh for testing
    cp "${MODULES_DIR}/process_figures.sh" "${TEST_TMP_DIR}/scripts/shell/modules/process_figures_test.sh"

    # Create a modified version of load_config.sh for testing
    cat > "${TEST_TMP_DIR}/scripts/shell/modules/load_config.sh" << EOF
# Modified load_config.sh for testing

# Figure
STXW_FIGURE_CAPTION_MEDIA_DIR="${TEST_TMP_DIR}/contents/figures/contents"
STXW_FIGURE_JPG_DIR="${TEST_TMP_DIR}/contents/figures/jpg"
STXW_FIGURE_COMPILED_DIR="${TEST_TMP_DIR}/contents/figures/compiled"
FIGURE_HIDDEN_DIR="${TEST_TMP_DIR}/contents/figures/.tex"
EOF

    # Modify paths in the test script
    sed -i "s|source \./scripts/shell/modules/load_config.sh|source ${TEST_TMP_DIR}/scripts/shell/modules/load_config.sh|g" "${TEST_TMP_DIR}/scripts/shell/modules/process_figures_test.sh"
}

# Clean up test environment
cleanup_test_env() {
    echo "Cleaning up test environment..."
    rm -rf "${TEST_TMP_DIR}"
}

# Main test function
run_tests() {
    echo "Testing process_figures.sh..."

    # Source the modified script to test its functions
    cd "${TEST_TMP_DIR}"
    source "${TEST_TMP_DIR}/scripts/shell/modules/process_figures_test.sh"

    # Test initialization
    test_function "init function creates required directories" "
        init > /dev/null 2>&1
        [ -d \"$STXW_FIGURE_CAPTION_MEDIA_DIR\" ] && [ -d \"$STXW_FIGURE_COMPILED_DIR\" ] && [ -d \"$STXW_FIGURE_JPG_DIR\" ] && [ -d \"$FIGURE_HIDDEN_DIR\" ]
    "

    # Test ensure_caption function
    test_function "ensure_caption creates captions when missing" "
        rm -f \"$STXW_FIGURE_CAPTION_MEDIA_DIR/.02_test.tex\"
        touch \"$STXW_FIGURE_CAPTION_MEDIA_DIR/.02_test.jpg\"
        ensure_caption > /dev/null 2>&1
        [ -f \"$STXW_FIGURE_CAPTION_MEDIA_DIR/.02_test.tex\" ]
    "

    # Test ensure_lower_letters function
    test_function "ensure_lower_letters converts filenames to lowercase" "
        touch \"$STXW_FIGURE_CAPTION_MEDIA_DIR/.03_TEST_UPPER.jpg\"
        ensure_lower_letters
        [ -f \"$STXW_FIGURE_CAPTION_MEDIA_DIR/.03_test_upper.jpg\" ] && [ ! -f \"$STXW_FIGURE_CAPTION_MEDIA_DIR/.03_TEST_UPPER.jpg\" ]
    "

    # Test compile_legends function (simplified)
    test_function "compile_legends creates figure legend files" "
        compile_legends > /dev/null 2>&1
        [ -f \"$STXW_FIGURE_COMPILED_DIR/.01_test.tex\" ]
    "

    # Test gather_tex_files function
    test_function "gather_tex_files creates aggregate file" "
        gather_tex_files > /dev/null 2>&1
        [ -f \"$STXW_FIGURE_COMPILED_FILE\" ] && grep -q \".01_test\" \"$STXW_FIGURE_COMPILED_FILE\"
    "

    # Test tif2jpg function (basic check)
    test_function "tif2jpg handles jpg files correctly" "
        mkdir -p \"$STXW_FIGURE_JPG_DIR\"
        tif2jpg false > /dev/null 2>&1
        [ -f \"$STXW_FIGURE_JPG_DIR/.01_test.jpg\" ]
    "

    # Test _toggle_figures function
    test_function "_toggle_figures enable works correctly" "
        _toggle_figures enable > /dev/null 2>&1
        grep -q '\\\\includegraphics' \"$STXW_FIGURE_COMPILED_DIR/.01_test.tex\" &&
        ! grep -q '^%\\\\includegraphics' \"$STXW_FIGURE_COMPILED_DIR/.01_test.tex\"
    "

    test_function "_toggle_figures disable works correctly" "
        _toggle_figures disable > /dev/null 2>&1
        grep -q '^%\\\\includegraphics' \"$STXW_FIGURE_COMPILED_DIR/.01_test.tex\" ||
        ! grep -q '\\\\includegraphics' \"$STXW_FIGURE_COMPILED_DIR/.01_test.tex\"
    "

    # Test main function (simplified)
    test_function "main function runs without errors" "
        main true false false > /dev/null 2>&1
        [ \$? -eq 0 ]
    "
}

# Run the tests
setup_test_env
run_tests
cleanup_test_env

echo "Process figures tests completed."

# EOF