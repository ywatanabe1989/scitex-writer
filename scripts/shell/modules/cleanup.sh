#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 10:52:38 (ywatanabe)"
# File: ./paper/scripts/shell/modules/cleanup.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

# Configurations
source ./config/load_config.sh $MANUSCRIPT_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0..."

function cleanup() {
    # Ensure logging directory
    mkdir -p $LOG_DIR

    # Remove all bak files from the repository
    find "$STWX_ROOT_DIR" -type f -name "*bak*" -exec rm {} \;

    # Remove Emacs temporary files
    find "$STWX_ROOT_DIR" -type f -name "#*#" -exec rm {} \;

    # Move files with these extensions to LOGDIR
    for ext in log out bbl blg spl dvi toc bak stderr stdout; do
        find "$STWX_ROOT_DIR" -maxdepth 1 -type f -name "*.$ext" -exec mv {} $LOG_DIR/ \; 2>/dev/null
    done

    echo_info "    Removing versioned files from current directory..."
    rm ./compiled_v* -f
    rm ./diff_v* -f
}

cleanup

# EOF