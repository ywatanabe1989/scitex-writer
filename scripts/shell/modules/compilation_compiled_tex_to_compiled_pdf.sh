#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 20:26:39 (ywatanabe)"
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
source ./config/load_config.sh $STXW_MANUSCRIPT_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0 ..."

# Setup container path (Singularity/Apptainer)
setup_container() {
    # Check if container path is already set
    if [ -n "$STXW_TEXLIVE_APPTAINER_SIF" ] && [ -f "$STXW_TEXLIVE_APPTAINER_SIF" ]; then
        return 0
    fi

    if [ ! -f "$STXW_TEXLIVE_APPTAINER_SIF" ]; then
        echo_info "    Downloading TeXLive container (one-time setup)..."
        mkdir -p "$(dirname $STXW_TEXLIVE_APPTAINER_SIF)"

        # Try Apptainer first, then Singularity
        if command -v apptainer &> /dev/null; then
            apptainer pull "$STXW_TEXLIVE_APPTAINER_SIF" docker://texlive/texlive:latest >/dev/null 2>&1
        elif command -v singularity &> /dev/null; then
            singularity pull "$STXW_TEXLIVE_APPTAINER_SIF" docker://texlive/texlive:latest >/dev/null 2>&1
        else
            return 1
        fi

        if [ -f "$STXW_TEXLIVE_APPTAINER_SIF" ]; then
            echo_success "    Container downloaded to $STXW_TEXLIVE_APPTAINER_SIF"
            export STXW_TEXLIVE_APPTAINER_SIF="$STXW_TEXLIVE_APPTAINER_SIF"
        else
            return 1
        fi
    fi

    return 0
}

compiled_tex_to_pdf() {
    echo_info "    Converting $STXW_COMPILED_TEX to PDF..."

    # Setup paths
    local abs_dir=$(realpath "$ORIG_DIR")
    local tex_file="$STXW_COMPILED_TEX"
    local tex_base="${STXW_COMPILED_TEX%.tex}"
    local aux_file="${tex_base}.aux"

    local compilation_method=""

    # First choice: Native pdflatex
    if command -v pdflatex &> /dev/null; then
        compilation_method="native"
        echo_info "    Using native pdflatex"
    # Second choice: Container (Apptainer/Singularity)
    elif command -v apptainer &> /dev/null || command -v singularity &> /dev/null; then
        if setup_container; then
            compilation_method="container"
            echo_info "    Using containerized TeXLive"
        fi
    # Third choice: Module system
    elif command -v module &> /dev/null && module avail texlive &> /dev/null 2>&1; then
        echo_info "    Loading texlive module..."
        module load texlive
        if command -v pdflatex &> /dev/null; then
            compilation_method="native"
            echo_info "    Using module-loaded pdflatex"
        fi
    fi

    # Check if we have a working method
    if [ -z "$compilation_method" ]; then
        echo_error "    No LaTeX installation found (native, module, or container)"
        return 1
    fi

    # Build commands based on method
    if [ "$compilation_method" = "container" ]; then
        # Determine container runtime
        if command -v apptainer &> /dev/null; then
            local runtime="apptainer"
        else
            local runtime="singularity"
        fi

        local container_base="$runtime exec --bind ${abs_dir}:${abs_dir} --pwd ${abs_dir} $STXW_TEXLIVE_APPTAINER_SIF"
        local pdf_cmd="$container_base pdflatex -output-directory=$(dirname $tex_file) -shell-escape -interaction=nonstopmode -file-line-error"
        local bib_cmd="$container_base bibtex"
    else
        # Native commands
        local pdf_cmd="pdflatex -output-directory=$(dirname $tex_file) -shell-escape -interaction=nonstopmode -file-line-error"
        local bib_cmd="bibtex"
    fi

    # Function to run command with timing
    run_command() {
        local cmd="$1"
        local verbose="$2"
        local desc="$3"

        echo_info "    $desc"
        local start=$(date +%s)

        if [ "$verbose" == "true" ]; then
            $cmd 2>&1 | grep -v "gocryptfs not found"
            local ret=${PIPESTATUS[0]}
        else
            $cmd >/dev/null 2>&1
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
    if [ -f "$STXW_COMPILED_PDF" ]; then
        local size=$(du -h "$STXW_COMPILED_PDF" | cut -f1)
        echo_success "    $STXW_COMPILED_PDF ready (${size})"
        sleep 1
    else
        echo_error "    $STXW_COMPILED_PDF was not created"

        local log_file="${STXW_COMPILED_PDF%.pdf}.log"
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