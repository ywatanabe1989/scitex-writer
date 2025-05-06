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

# Check for Python dependencies if available
check_python_dependencies() {
    if command -v python3 &> /dev/null; then
        echo_info "Checking Python dependencies..."
        # Check if OpenCV and NumPy are installed (required for crop_tif.py)
        if ! python3 -c "import cv2, numpy" &> /dev/null; then
            echo_warn "Python packages cv2 (OpenCV) and/or numpy not found."
            echo_warn "To use the --crop_tif feature, install them with: pip install opencv-python numpy"
            echo_warn "Crop TIF functionality will be disabled."
        else
            echo_info "Required Python packages for crop_tif are available."
        fi
        
        # Check for Mermaid CLI if we need to process .mmd files
        if ! command -v mmdc &> /dev/null; then
            echo_warn "Mermaid CLI (mmdc) not found. Mermaid diagram processing will be disabled."
            echo_warn "To use Mermaid diagrams, install with: npm install -g @mermaid-js/mermaid-cli"
        else
            echo_info "Mermaid CLI found. Mermaid diagrams can be processed."
        fi
    fi
}

check_python_dependencies

# EOF