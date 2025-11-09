#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-09 19:30:00 (ywatanabe)"
# File: ./tests/scitex/writer/run_test.sh

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

echo_header "Running scitex.writer tests" | tee -a $LOG_PATH
echo_info "Test directory: $THIS_DIR" | tee -a $LOG_PATH
echo_info "Project root: $GIT_ROOT" | tee -a $LOG_PATH
echo

cd $GIT_ROOT

# Run pytest with verbose output
pytest "$THIS_DIR" -v --tb=short 2>&1 | tee -a $LOG_PATH

exit_code=${PIPESTATUS[0]}

echo
if [ $exit_code -eq 0 ]; then
    echo_success "All tests passed!" | tee -a $LOG_PATH
else
    echo_error "Some tests failed. Check log: $LOG_PATH" | tee -a $LOG_PATH
fi

echo_info "Full log: $LOG_PATH"

exit $exit_code

# EOF
