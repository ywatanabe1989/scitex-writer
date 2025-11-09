#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-27 00:05:04 (ywatanabe)"
# File: ./paper/scripts/shell/modules/check_dependancy_commands.sh

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

# Configurations
source ./config/load_config.sh $SCITEX_WRITER_DOC_TYPE

# Source the 00_shared LaTeX commands module
source "$(dirname ${BASH_SOURCE[0]})/command_switching.src"

# To override echo_xxx functions
source ./config/load_config.sh $SCITEX_WRITER_DOC_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0..."


# Detect package manager
detect_package_manager() {
    if command -v apt &> /dev/null; then
        echo "apt"
    elif command -v yum &> /dev/null; then
        echo "yum"
    else
        echo "unknown"
    fi
}

# Check if sudo is available
has_sudo() {
    if command -v sudo &> /dev/null; then
        return 0
    else
        return 1
    fi
}

PKG_MANAGER=$(detect_package_manager)
SUDO_PREFIX=""
if has_sudo; then
    SUDO_PREFIX="sudo "
fi

# Standalone checker for each tool
check_pdflatex() {
    local cmd=$(get_cmd_pdflatex "$ORIG_DIR")
    if [ -z "$cmd" ]; then
        echo "- pdflatex"
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "    - ${SUDO_PREFIX}apt install texlive-latex-base"
        elif [ "$PKG_MANAGER" = "yum" ]; then
            echo "    - ${SUDO_PREFIX}yum install texlive-latex"
        fi
        echo "    - Or use: module load texlive"
        echo "    - Or use: apptainer/singularity with texlive container"
        return 1
    fi
    return 0
}

check_bibtex() {
    local cmd=$(get_cmd_bibtex "$ORIG_DIR")
    if [ -z "$cmd" ]; then
        echo "- bibtex"
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "    - ${SUDO_PREFIX}apt install texlive-bibtex-extra"
        elif [ "$PKG_MANAGER" = "yum" ]; then
            echo "    - ${SUDO_PREFIX}yum install texlive-bibtex"
        fi
        echo "    - Or use: module load texlive"
        echo "    - Or use: apptainer/singularity with texlive container"
        return 1
    fi
    return 0
}

check_latexdiff() {
    local cmd=$(get_cmd_latexdiff "$ORIG_DIR")
    if [ -z "$cmd" ]; then
        echo "- latexdiff"
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "    - ${SUDO_PREFIX}apt install latexdiff"
        elif [ "$PKG_MANAGER" = "yum" ]; then
            echo "    - ${SUDO_PREFIX}yum install texlive-latexdiff"
        fi
        echo "    - Or use: module load texlive"
        echo "    - Or use: apptainer/singularity with texlive container"
        return 1
    fi
    return 0
}

check_texcount() {
    local cmd=$(get_cmd_texcount "$ORIG_DIR")
    if [ -z "$cmd" ]; then
        echo "- texcount"
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "    - ${SUDO_PREFIX}apt install texlive-extra-utils"
        elif [ "$PKG_MANAGER" = "yum" ]; then
            echo "    - ${SUDO_PREFIX}yum install texlive-texcount"
        fi
        echo "    - Or use: module load texlive"
        echo "    - Or use: apptainer/singularity with texlive container"
        return 1
    fi
    return 0
}

check_xlsx2csv() {
    if ! command -v xlsx2csv &> /dev/null && ! python3 -c "import xlsx2csv" &> /dev/null 2>&1; then
        echo "- xlsx2csv"
        echo "    - pip install xlsx2csv"
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "    - Or: ${SUDO_PREFIX}apt install xlsx2csv"
        fi
        return 1
    fi
    return 0
}

check_csv2latex() {
    if ! command -v csv2latex &> /dev/null && ! python3 -c "import csv2latex" &> /dev/null 2>&1; then
        echo "- csv2latex"
        echo "    - pip install csv2latex"
        return 1
    fi
    return 0
}

check_parallel() {
    if ! command -v parallel &> /dev/null; then
        echo "- parallel"
        if [ "$PKG_MANAGER" = "apt" ]; then
            echo "    - ${SUDO_PREFIX}apt install parallel"
        elif [ "$PKG_MANAGER" = "yum" ]; then
            echo "    - ${SUDO_PREFIX}yum install parallel"
        fi
        return 1
    fi
    return 0
}

check_opencv() {
    if command -v python3 &> /dev/null; then
        if ! python3 -c "import cv2" &> /dev/null 2>&1; then
            echo "- opencv-python (optional, for --crop_tif)"
            echo "    - pip install opencv-python"
            return 1
        fi
    fi
    return 0
}

check_numpy() {
    if command -v python3 &> /dev/null; then
        if ! python3 -c "import numpy" &> /dev/null 2>&1; then
            echo "- numpy (optional, for --crop_tif)"
            echo "    - pip install numpy"
            return 1
        fi
    fi
    return 0
}

check_mmdc() {
    local cmd=$(get_cmd_mmdc "$ORIG_DIR")
    if [ -z "$cmd" ]; then
        echo "- mmdc (optional, for Mermaid diagrams)"
        if ! command -v npm &> /dev/null; then
            echo "    - First install npm/nodejs"
        fi
        echo "    - npm install -g @mermaid-js/mermaid-cli"
        echo "    - Or use: apptainer/singularity with mermaid container"
        return 1
    fi
    return 0
}

check_bibtexparser() {
    if command -v python3 &> /dev/null; then
        if ! python3 -c "import bibtexparser" &> /dev/null 2>&1; then
            echo "- bibtexparser (for bibliography analysis tools)"
            echo "    - pip install bibtexparser"
            return 1
        fi
    fi
    return 0
}

# Check all required commands (parallelized for speed)
check_all_dependencies() {
    local has_missing_required=false
    local has_missing_optional=false
    local required_output=""
    local optional_output=""

    # Temp directory for parallel results
    local temp_dir=$(mktemp -d)

    # Run all required checks in parallel
    check_pdflatex > "$temp_dir/req_pdflatex" 2>&1 &
    check_bibtex > "$temp_dir/req_bibtex" 2>&1 &
    check_latexdiff > "$temp_dir/req_latexdiff" 2>&1 &
    check_texcount > "$temp_dir/req_texcount" 2>&1 &
    check_xlsx2csv > "$temp_dir/req_xlsx2csv" 2>&1 &
    check_csv2latex > "$temp_dir/req_csv2latex" 2>&1 &
    check_parallel > "$temp_dir/req_parallel" 2>&1 &

    # Run all optional checks in parallel
    check_opencv > "$temp_dir/opt_opencv" 2>&1 &
    check_numpy > "$temp_dir/opt_numpy" 2>&1 &
    check_mmdc > "$temp_dir/opt_mmdc" 2>&1 &
    check_bibtexparser > "$temp_dir/opt_bibtexparser" 2>&1 &

    # Wait for all background jobs
    wait

    # Collect required results
    for result_file in "$temp_dir"/req_*; do
        if [ -s "$result_file" ]; then
            output=$(cat "$result_file")
            has_missing_required=true
            required_output="${required_output}${output}\n"
        fi
    done

    # Collect optional results
    for result_file in "$temp_dir"/opt_*; do
        if [ -s "$result_file" ]; then
            output=$(cat "$result_file")
            has_missing_optional=true
            optional_output="${optional_output}${output}\n"
        fi
    done

    # Cleanup
    rm -rf "$temp_dir"

    # Display results
    if [ "$has_missing_required" = true ]; then
        echo_error "    Missing required tools:"
        echo -e "$required_output"
        return 1
    else
        if [ -n "$SCITEX_WRITER_TEXLIVE_APPTAINER_SIF" ] && [ -f "$SCITEX_WRITER_TEXLIVE_APPTAINER_SIF" ]; then
            echo_success "    All required tools available (using container for LaTeX)"
        else
            echo_success "    All required tools available (native installation)"
        fi
    fi

    if [ "$has_missing_optional" = true ]; then
        echo_warning "    Missing optional tools:"
        echo -e "$optional_output"
    fi

    return 0
}

# Run checks
check_all_dependencies
exit_code=$?

exit $exit_code

# EOF