#!/bin/bash
# Test script for versioning.sh

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test directory setup
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
MODULES_DIR="${THIS_DIR}/../modules"
TEST_TMP_DIR="${THIS_DIR}/tmp_test_versioning"
mkdir -p "${TEST_TMP_DIR}"
mkdir -p "${TEST_TMP_DIR}/old"

# Create test files
echo "Test content" > "${TEST_TMP_DIR}/main/manuscript.pdf"
echo "Test content" > "${TEST_TMP_DIR}/main/manuscript.tex"
echo "Test content" > "${TEST_TMP_DIR}/diff.pdf"
echo "Test content" > "${TEST_TMP_DIR}/diff.tex"

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

# Before we source the script, we need to modify it for testing
# Make a temporary copy and modify variables for testing
cp "${MODULES_DIR}/versioning.sh" "${TEST_TMP_DIR}/versioning_test.sh"

# Replace the paths with our test paths
sed -i "s|OLD_DIR=\./old/|OLD_DIR=${TEST_TMP_DIR}/old/|g" "${TEST_TMP_DIR}/versioning_test.sh"
sed -i "s|STXW_COMPILED_PDF=\./main/manuscript.pdf|STXW_COMPILED_PDF=${TEST_TMP_DIR}/main/manuscript.pdf|g" "${TEST_TMP_DIR}/versioning_test.sh"
sed -i "s|STXW_COMPILED_TEX=\./main/manuscript.tex|STXW_COMPILED_TEX=${TEST_TMP_DIR}/main/manuscript.tex|g" "${TEST_TMP_DIR}/versioning_test.sh"
sed -i "s|STXW_DIFF_TEX=\./diff.tex|STXW_DIFF_TEX=${TEST_TMP_DIR}/diff.tex|g" "${TEST_TMP_DIR}/versioning_test.sh"
sed -i "s|STXW_DIFF_PDF=\./diff.pdf|STXW_DIFF_PDF=${TEST_TMP_DIR}/diff.pdf|g" "${TEST_TMP_DIR}/versioning_test.sh"

# Comment out the actual versioning call at the end so we can test functions individually
sed -i "s|versioning|# versioning|g" "${TEST_TMP_DIR}/versioning_test.sh"

# Source the modified script
source "${TEST_TMP_DIR}/versioning_test.sh"

echo "Testing versioning.sh..."

# Test the count_version function
test_function "count_version initializes version counter" "
    rm -f ${TEST_TMP_DIR}/old/.version_counter.txt
    STXW_VERSION_COUNTER_TXT=${TEST_TMP_DIR}/old/.version_counter.txt
    count_version
    [ -f ${TEST_TMP_DIR}/old/.version_counter.txt ] && [ \$(cat ${TEST_TMP_DIR}/old/.version_counter.txt) = '001' ]
"

test_function "count_version increments version counter" "
    echo '001' > ${TEST_TMP_DIR}/old/.version_counter.txt
    STXW_VERSION_COUNTER_TXT=${TEST_TMP_DIR}/old/.version_counter.txt
    count_version
    [ \$(cat ${TEST_TMP_DIR}/old/.version_counter.txt) = '002' ]
"

# Test store_files function
mkdir -p "${TEST_TMP_DIR}/main"
echo "Test content" > "${TEST_TMP_DIR}/main/test.pdf"

test_function "store_files copies file correctly" "
    STXW_VERSION_COUNTER_TXT=${TEST_TMP_DIR}/old/.version_counter.txt
    echo '003' > \$STXW_VERSION_COUNTER_TXT
    store_files ${TEST_TMP_DIR}/main/test.pdf pdf
    [ -f ${TEST_TMP_DIR}/old/test_v003.pdf ]
"

# Test remove_old_archive function
touch "${TEST_TMP_DIR}/compiled_v001.pdf"
touch "${TEST_TMP_DIR}/diff_v001.tex"

test_function "remove_old_archive removes old files" "
    cd ${TEST_TMP_DIR}
    remove_old_archive
    ! [ -f ${TEST_TMP_DIR}/compiled_v001.pdf ] && ! [ -f ${TEST_TMP_DIR}/diff_v001.tex ]
"

# Test full versioning function
test_function "full versioning process" "
    cd ${TEST_TMP_DIR}
    mkdir -p ${TEST_TMP_DIR}/main
    echo 'Test content' > ${TEST_TMP_DIR}/main/manuscript.pdf
    echo 'Test content' > ${TEST_TMP_DIR}/main/manuscript.tex
    echo 'Test content' > ${TEST_TMP_DIR}/diff.pdf
    echo 'Test content' > ${TEST_TMP_DIR}/diff.tex
    STXW_VERSION_COUNTER_TXT=${TEST_TMP_DIR}/old/.version_counter.txt
    echo '004' > \$STXW_VERSION_COUNTER_TXT
    versioning
    [ -f ${TEST_TMP_DIR}/old/manuscript_v005.pdf ] && 
    [ -f ${TEST_TMP_DIR}/old/manuscript_v005.tex ] && 
    [ -f ${TEST_TMP_DIR}/old/diff_v005.pdf ] && 
    [ -f ${TEST_TMP_DIR}/old/diff_v005.tex ]
"

# Clean up
echo "Cleaning up test directory..."
rm -rf "${TEST_TMP_DIR}"

echo "Versioning tests completed."