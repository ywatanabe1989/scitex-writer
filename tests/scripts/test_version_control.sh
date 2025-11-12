#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-12 (ywatanabe)"
# File: ./tests/scripts/test_version_control.sh
# Description: Test script for git auto-commit and archive cleanup modules

set -e

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

# Colors
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

# Change to project root
cd "$PROJECT_ROOT"

echo_header "Version Control Module Tests"
echo

# Test 1: Configuration Loading
echo_header "Test 1: Configuration Loading"
if source ./config/version_control.conf; then
    echo_success "Configuration loaded successfully"
    echo_info "  GIT_AUTO_COMMIT_ENABLED=$GIT_AUTO_COMMIT_ENABLED"
    echo_info "  ARCHIVE_CLEANUP_ENABLED=$ARCHIVE_CLEANUP_ENABLED"
    echo_info "  ARCHIVE_KEEP_LAST_N=$ARCHIVE_KEEP_LAST_N"
else
    echo_error "Failed to load configuration"
    exit 1
fi
echo

# Test 2: Module File Existence
echo_header "Test 2: Module Files"
for module in git_auto_commit.sh archive_cleanup.sh; do
    if [ -f "./scripts/shell/modules/$module" ]; then
        echo_success "$module exists"
    else
        echo_error "$module not found"
        exit 1
    fi
done
echo

# Test 3: Archive Directory Check
echo_header "Test 3: Archive Directory Status"
export SCITEX_WRITER_DOC_TYPE="manuscript"
source ./config/load_config.sh "$SCITEX_WRITER_DOC_TYPE" 2>/dev/null

if [ -d "$SCITEX_WRITER_VERSIONS_DIR" ]; then
    archive_count=$(find "$SCITEX_WRITER_VERSIONS_DIR" -maxdepth 1 \
        -name "manuscript_v[0-9][0-9][0-9].pdf" 2>/dev/null | wc -l)
    echo_success "Archive directory exists: $SCITEX_WRITER_VERSIONS_DIR"
    echo_info "  Current versions: $archive_count"
else
    echo_warning "Archive directory not found (will be created on first compile)"
fi
echo

# Test 4: Git Repository Check
echo_header "Test 4: Git Repository Status"
if git rev-parse --git-dir &>/dev/null; then
    echo_success "Git repository detected"
    echo_info "  Current branch: $(git branch --show-current)"
    echo_info "  User: $(git config user.name) <$(git config user.email)>"

    # Check for unstaged changes
    if git diff --quiet && git diff --cached --quiet; then
        echo_info "  Working tree: clean"
    else
        echo_warning "  Working tree: has changes (this is normal)"
    fi
else
    echo_error "Not a git repository"
    exit 1
fi
echo

# Test 5: Module Function Loading
echo_header "Test 5: Module Function Loading"

# Load git auto-commit module
if source ./scripts/shell/modules/git_auto_commit.sh; then
    if declare -f git_auto_commit &>/dev/null; then
        echo_success "git_auto_commit function loaded"
    else
        echo_error "git_auto_commit function not found"
        exit 1
    fi
else
    echo_error "Failed to load git_auto_commit.sh"
    exit 1
fi

# Load archive cleanup module
if source ./scripts/shell/modules/archive_cleanup.sh; then
    if declare -f cleanup_old_archives &>/dev/null; then
        echo_success "cleanup_old_archives function loaded"
    else
        echo_error "cleanup_old_archives function not found"
        exit 1
    fi
else
    echo_error "Failed to load archive_cleanup.sh"
    exit 1
fi
echo

# Test 6: Dry Run Test
echo_header "Test 6: Dry Run (Configuration Check)"
echo_info "Testing with current settings:"
echo_info "  GIT_AUTO_COMMIT_ENABLED: $GIT_AUTO_COMMIT_ENABLED"
echo_info "  GIT_TAG_ENABLED: $GIT_TAG_ENABLED"
echo_info "  ARCHIVE_CLEANUP_ENABLED: $ARCHIVE_CLEANUP_ENABLED"
echo_info "  ARCHIVE_KEEP_LAST_N: $ARCHIVE_KEEP_LAST_N"
echo_info "  ARCHIVE_MIN_KEEP: $ARCHIVE_MIN_KEEP"
echo

# Summary
echo_header "Test Summary"
echo_success "All tests passed!"
echo
echo_info "Next steps:"
echo_info "  1. Run a test compilation: ./scripts/shell/compile_manuscript.sh"
echo_info "  2. Check git log: git log -1 --oneline"
echo_info "  3. Check git tags: git tag -l"
echo_info "  4. Check archive count after cleanup"
echo
echo_info "To disable features for testing:"
echo_info "  export GIT_AUTO_COMMIT_ENABLED=false  # Disable git commits"
echo_info "  export ARCHIVE_CLEANUP_ENABLED=false  # Disable cleanup"
echo

# Return to original directory
cd "$ORIG_DIR"

# EOF
