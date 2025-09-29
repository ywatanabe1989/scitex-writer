#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-27 00:28:29 (ywatanabe)"
# File: ./paper/scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh

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

# Source the shared LaTeX commands module
source "$(dirname ${BASH_SOURCE[0]})/command_switching.src"

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0 ..."

compiled_tex_to_pdf() {
    echo_info "    Converting $STXW_COMPILED_TEX to PDF..."

    # Setup paths
    local abs_dir=$(realpath "$ORIG_DIR")
    local tex_file="$STXW_COMPILED_TEX"
    local tex_base="${STXW_COMPILED_TEX%.tex}"
    local aux_file="${tex_base}.aux"

    # Get commands from shared module
    local pdf_cmd=$(get_cmd_pdflatex "$ORIG_DIR")
    local bib_cmd=$(get_cmd_bibtex "$ORIG_DIR")

    if [ -z "$pdf_cmd" ] || [ -z "$bib_cmd" ]; then
        echo_error "    No LaTeX installation found (native, module, or container)"
        return 1
    fi

    # Add compilation options to commands
    pdf_cmd="$pdf_cmd -output-directory=$(dirname $tex_file) -shell-escape -interaction=nonstopmode -file-line-error"

    # Function to run command with timing
    run_command() {
        local cmd="$1"
        local verbose="$2"
        local desc="$3"

        echo_info "    $desc"
        local start=$(date +%s)

        if [ "$verbose" == "true" ]; then
            eval "$cmd" 2>&1 | grep -v "gocryptfs not found"
            local ret=${PIPESTATUS[0]}
        else
            eval "$cmd" >/dev/null 2>&1
            local ret=$?
        fi

        local end=$(date +%s)
        echo_info "      ($(($end - $start))s)"

        return $ret
    }

    # Main compilation sequence
    local total_start=$(date +%s)

    # Pass 1: Generate aux files
    run_command "$pdf_cmd $tex_file" "$STXW_VERBOSE_PDFLATEX" "Pass 1/3: Initial"

    # Process bibliography if needed
    if [ -f "$aux_file" ]; then
        if grep -q "\\citation\|\\bibdata\|\\bibstyle" "$aux_file" 2>/dev/null; then
            run_command "$bib_cmd $tex_base" "$STXW_VERBOSE_BIBTEX" "Processing bibliography"
        fi
    fi

    # Pass 2: Include bibliography
    run_command "$pdf_cmd $tex_file" "$STXW_VERBOSE_PDFLATEX" "Pass 2/3: Bibliography"

    # Pass 3: Resolve all references
    run_command "$pdf_cmd $tex_file" "$STXW_VERBOSE_PDFLATEX" "Pass 3/3: Final"

    local total_end=$(date +%s)
    echo_success "    Total compilation: $(($total_end - $total_start))s"
}

cleanup() {
    # Use fallback if STXW_COMPILED_PDF is not set or empty
    local pdf_file="${STXW_COMPILED_PDF}"
    if [ -z "$pdf_file" ]; then
        pdf_file="./01_manuscript/manuscript.pdf"
    fi
    if [ -f "$pdf_file" ]; then
        local size=$(du -h "$pdf_file" | cut -f1)
        echo_success "    $pdf_file ready (${size})"
        
        # Create/update stable symlink to latest archive version (prevents corruption during compilation)
        local latest_path="${STWX_ROOT_DIR}/manuscript-latest.pdf"
        
        # Find the latest archived version (highest version number)
        local archive_dir="${STXW_VERSIONS_DIR}"
        local latest_archive=$(ls -1 "$archive_dir"/manuscript_v[0-9]*.pdf 2>/dev/null | grep -v "_diff.pdf" | sort -V | tail -1)
        
        if [ -n "$latest_archive" ]; then
            # Create relative symlink to archive
            ln -sf "archive/$(basename "$latest_archive")" "$latest_path"
            echo_success "    Symlink updated: $latest_path -> archive/$(basename "$latest_archive")"
        else
            # Fallback to current PDF if no archive exists
            ln -sf "$(basename "$pdf_file")" "$latest_path"
            echo_success "    Symlink updated: $latest_path -> $(basename "$pdf_file") (no archive yet)"
        fi
        # Note: For rsync, use -L flag to follow symlinks: rsync -avL ...
        
        sleep 1
    else
        echo_error "    $pdf_file was not created"

        local log_file="${pdf_file%.pdf}.log"
        if [ -f "$log_file" ]; then
            echo_error "    LaTeX errors:"
            grep "^!" "$log_file" 2>/dev/null | head -5
        fi

        return 1
    fi
}

main() {
    compiled_tex_to_pdf
    cleanup
}

main

# EOF