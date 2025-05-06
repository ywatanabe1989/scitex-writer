#!/bin/bash
# Test script for config.src

# Source the script to test
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
MODULES_DIR="${THIS_DIR}/../modules"
source "${MODULES_DIR}/config.src"

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

# Begin tests
echo "Testing config.src..."

# Test directory variables are set
test_function "FIGURE_SRC_DIR is set" "[ -n \"$FIGURE_SRC_DIR\" ]"
test_function "FIGURE_JPG_DIR is set" "[ -n \"$FIGURE_JPG_DIR\" ]"
test_function "FIGURE_COMPILED_DIR is set" "[ -n \"$FIGURE_COMPILED_DIR\" ]"
test_function "FIGURE_HIDDEN_DIR is set" "[ -n \"$FIGURE_HIDDEN_DIR\" ]"

test_function "TABLE_SRC_DIR is set" "[ -n \"$TABLE_SRC_DIR\" ]"
test_function "TABLE_COMPILED_DIR is set" "[ -n \"$TABLE_COMPILED_DIR\" ]"
test_function "TABLE_HIDDEN_DIR is set" "[ -n \"$TABLE_HIDDEN_DIR\" ]"

test_function "WORDCOUNT_DIR is set" "[ -n \"$WORDCOUNT_DIR\" ]"

# Check if directories exist or can be created
test_function "FIGURE_SRC_DIR exists or can be created" "mkdir -p \"$FIGURE_SRC_DIR\" && [ -d \"$FIGURE_SRC_DIR\" ]"
test_function "FIGURE_JPG_DIR exists or can be created" "mkdir -p \"$FIGURE_JPG_DIR\" && [ -d \"$FIGURE_JPG_DIR\" ]"
test_function "FIGURE_COMPILED_DIR exists or can be created" "mkdir -p \"$FIGURE_COMPILED_DIR\" && [ -d \"$FIGURE_COMPILED_DIR\" ]"
test_function "FIGURE_HIDDEN_DIR exists or can be created" "mkdir -p \"$FIGURE_HIDDEN_DIR\" && [ -d \"$FIGURE_HIDDEN_DIR\" ]"

test_function "TABLE_SRC_DIR exists or can be created" "mkdir -p \"$TABLE_SRC_DIR\" && [ -d \"$TABLE_SRC_DIR\" ]"
test_function "TABLE_COMPILED_DIR exists or can be created" "mkdir -p \"$TABLE_COMPILED_DIR\" && [ -d \"$TABLE_COMPILED_DIR\" ]"
test_function "TABLE_HIDDEN_DIR exists or can be created" "mkdir -p \"$TABLE_HIDDEN_DIR\" && [ -d \"$TABLE_HIDDEN_DIR\" ]"

test_function "WORDCOUNT_DIR exists or can be created" "mkdir -p \"$WORDCOUNT_DIR\" && [ -d \"$WORDCOUNT_DIR\" ]"

echo "Config tests completed."