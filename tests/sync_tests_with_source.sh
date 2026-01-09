#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-09 14:00:00 (ywatanabe)"
# File: ./tests/sync_tests_with_source.sh

# =============================================================================
# Test Synchronization Script for scitex-writer
# =============================================================================
#
# PURPOSE:
#   Synchronizes test file structure with source code structure, ensuring
#   every source file has a corresponding test file with embedded source
#   code for reference.
#
# BEHAVIOR:
#   1. Mirrors scripts/ directory structure to tests/
#      - scripts/shell/ -> tests/shell/
#      - scripts/python/ -> tests/python/
#   2. For each source file:
#      - Shell: scripts/shell/foo.sh -> tests/shell/test_foo.sh
#      - Python: scripts/python/bar.py -> tests/python/test_bar.py
#   3. Preserves existing test code (before source block)
#   4. Updates commented source code block at file end
#   5. Identifies "stale" tests (tests without matching source files)
#   6. With -m flag: moves stale tests to .old-{timestamp}/ directories
#
# USAGE:
#   ./tests/sync_tests_with_source.sh          # Dry run - report stale & placeholder files
#   ./tests/sync_tests_with_source.sh -m       # Move stale files to .old/
#   ./tests/sync_tests_with_source.sh -j 16    # Use 16 parallel jobs
#
# =============================================================================

set -euo pipefail

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(realpath "$THIS_DIR/..")"
LOG_PATH="$THIS_DIR/.$(basename "$0").log"
echo "" >"$LOG_PATH"

# Color scheme
GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }

########################################
# Usage & Argument Parser
########################################
DO_MOVE=false
SCRIPTS_DIR="$ROOT_DIR/scripts"
TESTS_DIR="$ROOT_DIR/tests"
CPU_COUNT=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
PARALLEL_JOBS=$((CPU_COUNT / 2 > 0 ? CPU_COUNT / 2 : 1))

usage() {
    echo "Usage: $0 [options]"
    echo
    echo "Synchronizes test files with source files in scripts/, maintaining test code while updating source references."
    echo "Reports stale tests and placeholder-only tests by default."
    echo
    echo "Options:"
    echo "  -m, --move         Move stale test files to .old directory (default: $DO_MOVE)"
    echo "  -j, --jobs N       Number of parallel jobs (default: $PARALLEL_JOBS)"
    echo "  -h, --help         Display this help message"
    echo
    echo "Directory Mapping:"
    echo "  scripts/shell/     -> tests/shell/"
    echo "  scripts/python/    -> tests/python/"
    echo
    exit 1
}

while [[ $# -gt 0 ]]; do
    case $1 in
    -m | --move)
        DO_MOVE=true
        shift
        ;;
    -j | --jobs)
        PARALLEL_JOBS="$2"
        shift 2
        ;;
    -h | --help) usage ;;
    *)
        echo "Unknown option: $1"
        usage
        ;;
    esac
done

########################################
# Blacklist patterns
########################################
EXCLUDE_PATTERNS=(
    "*/.*"
    "*/__pycache__/*"
    "*/archive/*"
    "*/.old*"
    "*/deprecated/*"
)

construct_find_excludes() {
    FIND_EXCLUDES=()
    for pattern in "${EXCLUDE_PATTERNS[@]}"; do
        FIND_EXCLUDES+=(-not -path "$pattern")
    done
}

########################################
# Source Code Block Generators
########################################
get_shell_source_block() {
    local src_file=$1
    echo ""
    echo "# --------------------------------------------------------------------------------"
    echo "# Start of Source Code from: $src_file"
    echo "# --------------------------------------------------------------------------------"
    sed 's/^/# /' "$src_file"
    echo ""
    echo "# --------------------------------------------------------------------------------"
    echo "# End of Source Code from: $src_file"
    echo "# --------------------------------------------------------------------------------"
}

get_python_source_block() {
    local src_file=$1
    echo ""
    echo "# --------------------------------------------------------------------------------"
    echo "# Start of Source Code from: $src_file"
    echo "# --------------------------------------------------------------------------------"
    sed 's/^/# /' "$src_file"
    echo ""
    echo "# --------------------------------------------------------------------------------"
    echo "# End of Source Code from: $src_file"
    echo "# --------------------------------------------------------------------------------"
}

########################################
# Test File Templates
########################################
get_shell_test_template() {
    # shellcheck disable=SC2034
    local src_name=$1 # Used via sed substitution on SOURCE_NAME
    cat <<'TEMPLATE'
#!/bin/bash
# -*- coding: utf-8 -*-
# Test file for: SOURCE_NAME

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(realpath "$THIS_DIR/../..")"

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

assert_success() {
    local cmd="$1"
    local desc="${2:-$cmd}"
    ((TESTS_RUN++))
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $desc"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $desc"
        ((TESTS_FAILED++))
    fi
}

assert_file_exists() {
    local file="$1"
    ((TESTS_RUN++))
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} File exists: $file"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} File missing: $file"
        ((TESTS_FAILED++))
    fi
}

# Add your tests here
test_placeholder() {
    echo "TODO: Add tests for SOURCE_NAME"
}

# Run tests
main() {
    echo "Testing: SOURCE_NAME"
    echo "========================================"

    test_placeholder

    echo "========================================"
    echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
    [ $TESTS_FAILED -gt 0 ] && exit 1
    exit 0
}

main "$@"
TEMPLATE
}

get_python_test_template() {
    # shellcheck disable=SC2034
    local src_name=$1 # Used via sed substitution on SOURCE_NAME
    cat <<'TEMPLATE'
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test file for: SOURCE_NAME

import os
import sys
from pathlib import Path

# Add scripts/python to path for imports
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR / "scripts" / "python"))


# Add your tests here
def test_placeholder():
    """TODO: Add tests for SOURCE_NAME"""
    pass


if __name__ == "__main__":
    import pytest
    pytest.main([os.path.abspath(__file__), "-v"])
TEMPLATE
}

########################################
# Extract existing test code
########################################
extract_test_code() {
    local test_file=$1
    local temp_file
    temp_file=$(mktemp)

    if grep -q "# Start of Source Code from:" "$test_file"; then
        sed -n '/# Start of Source Code from:/q;p' "$test_file" >"$temp_file"
    else
        cat "$test_file" >"$temp_file"
    fi

    # Remove trailing blank lines
    if [ -s "$temp_file" ]; then
        sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$temp_file" 2>/dev/null || true
        cat "$temp_file"
    fi
    rm -f "$temp_file"
}

########################################
# Process Shell Scripts
########################################
process_shell_file() {
    local src_file="$1"
    local scripts_dir="$2"
    local tests_dir="$3"

    local rel="${src_file#"$scripts_dir"/shell/}"
    local rel_dir
    rel_dir=$(dirname "$rel")
    # Handle files in root of shell/ directory
    [ "$rel_dir" = "." ] && rel_dir=""
    local src_base
    src_base=$(basename "$rel" .sh)

    local test_subdir="$tests_dir/shell${rel_dir:+/$rel_dir}"
    mkdir -p "$test_subdir"
    local test_file="$test_subdir/test_${src_base}.sh"

    if [ ! -f "$test_file" ]; then
        echo_info "Creating: $test_file"
        get_shell_test_template "$src_base.sh" | sed "s/SOURCE_NAME/$src_base.sh/g" >"$test_file"
        get_shell_source_block "$src_file" >>"$test_file"
        chmod +x "$test_file"
    else
        local temp_file
        temp_file=$(mktemp)
        local test_code
        test_code=$(extract_test_code "$test_file")

        if [ -n "$test_code" ]; then
            echo "$test_code" >"$temp_file"
        else
            get_shell_test_template "$src_base.sh" | sed "s/SOURCE_NAME/$src_base.sh/g" >"$temp_file"
        fi

        get_shell_source_block "$src_file" >>"$temp_file"
        mv "$temp_file" "$test_file"
        chmod +x "$test_file"
    fi
}
export -f process_shell_file get_shell_source_block get_shell_test_template extract_test_code echo_info
export GRAY GREEN YELLOW RED NC

########################################
# Process Python Scripts
########################################
process_python_file() {
    local src_file="$1"
    local scripts_dir="$2"
    local tests_dir="$3"

    # Skip __init__.py and private modules
    local file_basename
    file_basename=$(basename "$src_file")
    [[ "$file_basename" == "__init__.py" ]] && return
    [[ "$file_basename" == _*.py ]] && return

    local rel="${src_file#"$scripts_dir"/python/}"
    local rel_dir
    rel_dir=$(dirname "$rel")
    # Handle files in root of python/ directory
    [ "$rel_dir" = "." ] && rel_dir=""
    local src_base
    src_base=$(basename "$rel" .py)

    local test_subdir="$tests_dir/python${rel_dir:+/$rel_dir}"
    mkdir -p "$test_subdir"
    local test_file="$test_subdir/test_${src_base}.py"

    if [ ! -f "$test_file" ]; then
        echo_info "Creating: $test_file"
        get_python_test_template "$src_base.py" | sed "s/SOURCE_NAME/$src_base.py/g" >"$test_file"
        get_python_source_block "$src_file" >>"$test_file"
        chmod +x "$test_file"
    else
        local temp_file
        temp_file=$(mktemp)
        local test_code
        test_code=$(extract_test_code "$test_file")

        if [ -n "$test_code" ]; then
            echo "$test_code" >"$temp_file"
        else
            get_python_test_template "$src_base.py" | sed "s/SOURCE_NAME/$src_base.py/g" >"$temp_file"
        fi

        get_python_source_block "$src_file" >>"$temp_file"
        mv "$temp_file" "$test_file"
        chmod +x "$test_file"
    fi
}
export -f process_python_file get_python_source_block get_python_test_template

########################################
# Stale Test Detection
########################################
find_stale_tests() {
    local tests_dir="$1"
    local scripts_dir="$2"
    local stale_files=()

    # Check shell tests
    if [ -d "$tests_dir/shell" ]; then
        while IFS= read -r test_file; do
            [[ "$test_file" =~ \.old ]] && continue
            local rel="${test_file#"$tests_dir"/shell/}"
            local test_base
            test_base=$(basename "$rel")
            local src_base="${test_base#test_}"
            local src_dir
            src_dir=$(dirname "$rel")
            [ "$src_dir" = "." ] && src_dir=""
            local src_file="$scripts_dir/shell${src_dir:+/$src_dir}/$src_base"

            [ ! -f "$src_file" ] && stale_files+=("$test_file")
        done < <(find "$tests_dir/shell" -name "test_*.sh" 2>/dev/null)
    fi

    # Check python tests
    if [ -d "$tests_dir/python" ]; then
        while IFS= read -r test_file; do
            [[ "$test_file" =~ \.old ]] && continue
            local rel="${test_file#"$tests_dir"/python/}"
            local test_base
            test_base=$(basename "$rel")
            local src_base="${test_base#test_}"
            local src_dir
            src_dir=$(dirname "$rel")
            [ "$src_dir" = "." ] && src_dir=""
            local src_file="$scripts_dir/python${src_dir:+/$src_dir}/$src_base"

            [ ! -f "$src_file" ] && stale_files+=("$test_file")
        done < <(find "$tests_dir/python" -name "test_*.py" 2>/dev/null)
    fi

    printf '%s\n' "${stale_files[@]}"
}

move_stale_tests() {
    local timestamp
    timestamp=$(date +%Y%m%d_%H%M%S)
    local stale_count=0
    local moved_count=0

    while IFS= read -r stale_file; do
        [ -z "$stale_file" ] && continue
        ((stale_count++)) || true

        local rel_path="${stale_file#"$TESTS_DIR"/}"
        if [ "$DO_MOVE" = "true" ]; then
            local stale_dir
            stale_dir=$(dirname "$stale_file")
            local old_dir="$stale_dir/.old-$timestamp"
            mkdir -p "$old_dir"
            mv "$stale_file" "$old_dir/"
            echo_success "  [MOVED] $rel_path"
            ((moved_count++)) || true
        else
            echo_warning "  [STALE] $rel_path"
        fi
    done < <(find_stale_tests "$TESTS_DIR" "$SCRIPTS_DIR")

    if [ "$stale_count" -gt 0 ]; then
        echo ""
        if [ "$DO_MOVE" = "false" ]; then
            echo_info "To move stale files, run: $0 -m"
        else
            echo_success "Moved $moved_count stale test files"
        fi
    fi
}

########################################
# Placeholder Detection
########################################
is_placeholder_only() {
    local test_file="$1"
    local ext="${test_file##*.}"

    local content
    if grep -q "# Start of Source Code from:" "$test_file"; then
        content=$(sed -n '/# Start of Source Code from:/q;p' "$test_file")
    else
        content=$(cat "$test_file")
    fi

    if [ "$ext" = "sh" ]; then
        # Check for actual test functions (not just test_placeholder)
        if echo "$content" | grep -qE "^test_[a-z]" | grep -v "test_placeholder"; then
            return 1
        fi
    elif [ "$ext" = "py" ]; then
        # Check for actual test functions
        if echo "$content" | grep -qE "^\s*def test_" | grep -v "test_placeholder"; then
            return 1
        fi
    fi

    return 0
}

report_placeholder_tests() {
    local placeholder_count=0

    echo ""
    echo_header "Placeholder Test Files"
    echo ""

    # Check shell tests
    if [ -d "$TESTS_DIR/shell" ]; then
        while IFS= read -r test_file; do
            [[ "$test_file" =~ \.old ]] && continue
            if is_placeholder_only "$test_file"; then
                local rel="${test_file#"$TESTS_DIR"/}"
                echo_warning "  [PLACEHOLDER] $rel"
                ((placeholder_count++)) || true
            fi
        done < <(find "$TESTS_DIR/shell" -name "test_*.sh" 2>/dev/null)
    fi

    # Check python tests
    if [ -d "$TESTS_DIR/python" ]; then
        while IFS= read -r test_file; do
            [[ "$test_file" =~ \.old ]] && continue
            if is_placeholder_only "$test_file"; then
                local rel="${test_file#"$TESTS_DIR"/}"
                echo_warning "  [PLACEHOLDER] $rel"
                ((placeholder_count++)) || true
            fi
        done < <(find "$TESTS_DIR/python" -name "test_*.py" 2>/dev/null)
    fi

    echo ""
    if [ "$placeholder_count" -eq 0 ]; then
        echo_success "No placeholder-only test files found"
    else
        echo_info "Found $placeholder_count placeholder test files needing implementation"
    fi
}

########################################
# Main
########################################
main() {
    local start_time
    start_time=$(date +%s)

    echo ""
    echo_header "Test Synchronization for scitex-writer"
    echo ""
    echo_info "Scripts:   $SCRIPTS_DIR"
    echo_info "Tests:     $TESTS_DIR"
    echo_info "Jobs:      $PARALLEL_JOBS"
    echo ""

    construct_find_excludes

    # Create test directories mirroring scripts structure
    echo_info "Preparing test structure..."
    mkdir -p "$TESTS_DIR/shell"
    mkdir -p "$TESTS_DIR/python"

    # Process shell scripts
    echo_info "Synchronizing shell script tests..."
    local shell_count=0
    if [ -d "$SCRIPTS_DIR/shell" ]; then
        while IFS= read -r src_file; do
            process_shell_file "$src_file" "$SCRIPTS_DIR" "$TESTS_DIR"
            ((shell_count++)) || true
        done < <(find "$SCRIPTS_DIR/shell" -name "*.sh" "${FIND_EXCLUDES[@]}" -type f 2>/dev/null)
    fi
    echo_success "Processed $shell_count shell scripts"

    # Process Python scripts
    echo_info "Synchronizing Python script tests..."
    local python_count=0
    if [ -d "$SCRIPTS_DIR/python" ]; then
        while IFS= read -r src_file; do
            process_python_file "$src_file" "$SCRIPTS_DIR" "$TESTS_DIR"
            ((python_count++)) || true
        done < <(find "$SCRIPTS_DIR/python" -name "*.py" "${FIND_EXCLUDES[@]}" -type f 2>/dev/null)
    fi
    echo_success "Processed $python_count Python scripts"

    # Handle stale tests
    echo ""
    echo_header "Stale Test Files"
    echo ""
    move_stale_tests

    # Report placeholder tests
    report_placeholder_tests

    local end_time
    end_time=$(date +%s)
    local elapsed=$((end_time - start_time))

    echo ""
    echo_header "Summary"
    echo_success "Completed in ${elapsed}s"
    echo ""

    # Log tree structure
    { tree "$TESTS_DIR" || ls -laR "$TESTS_DIR"; } >>"$LOG_PATH" 2>&1
}

main "$@"
cd "$ORIG_DIR"

# EOF
