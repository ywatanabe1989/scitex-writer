#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 23:09:27 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/check_dependancy_commands.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config.src
echo_info "$0..."

check_dependency_commands() {
    for COMMAND in "$@"; do
        if ! command -v $COMMAND &> /dev/null; then
            echo_error "${COMMAND} not found. Please install the necessary package. (e.g., sudo apt-get install ${COMMAND} -y)"
            exit 1
        fi
    done
}

check_dependency_commands pdflatex bibtex xlsx2csv csv2latex parallel

# EOF