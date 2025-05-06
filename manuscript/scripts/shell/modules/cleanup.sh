#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 23:09:26 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/cleanup.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config.src
echo_info "$0..."


function cleanup() {

    mkdir -p $LOG_DIR

    # Remove all bak files from the repository
    find . -type f -name "*bak*" -exec rm {} \;

    # Remove Emacs temporary files
    find . -type f -name "#*#" -exec rm {} \;

    # Move files with these extensions to LOGDIR
    for ext in log out bbl blg spl dvi toc bak stderr stdout; do
        find . -maxdepth 1 -type f -name "*.$ext" -exec mv {} $LOG_DIR/ \; 2>/dev/null
    done

    # Handle main.aux separately if needed
    # find . -maxdepth 1 -type f -name "main.aux" -exec mv {} ./main/ \; 2>/dev/null

    echo_info "Removing versioned files from current directory..."
    rm ./compiled_v* -f
    rm ./diff_v* -f
}

cleanup

# EOF