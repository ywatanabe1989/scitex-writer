#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-27 16:35:00 (ywatanabe)"
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
source ./config/load_config.sh $STXW_DOC_TYPE

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

    # Move files with these extensions to LOG_DIR
    for ext in log out bbl blg spl dvi toc bak stderr stdout aux fls fdb_latexmk synctex.gz cb cb2; do
        find "$STWX_ROOT_DIR" -maxdepth 1 -type f -name "*.$ext" -exec mv {} $LOG_DIR/ \; 2>/dev/null
    done
    
    # Remove progress.log files (from parallel commands)
    find "$STWX_ROOT_DIR" -name "progress.log" -type f -delete 2>/dev/null

    echo_info "    Removing versioned files from current directory..."
    rm -f *_v*.pdf *_v*.tex 2>/dev/null
}

# Main
cleanup

# EOF