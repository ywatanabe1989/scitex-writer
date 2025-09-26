#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 20:24:29 (ywatanabe)"
# File: ./paper/scripts/shell/modules/process_diff.sh

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

# Configuration
source ./config/load_config.sh $STXW_MANUSCRIPT_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0 ..."

# Setup container (same as main compilation)
setup_container() {
    if [ -n "$STXW_APPTAINER_TEXLIVE" ] && [ -f "$STXW_APPTAINER_TEXLIVE" ]; then
        TEXLIVE_CONTAINER="$STXW_APPTAINER_TEXLIVE"
        return 0
    fi

    local container_path="${HOME}/.cache/texlive.sif"

    if [ ! -f "$container_path" ]; then
        echo_info "    Setting up TeXLive container..."
        mkdir -p "$(dirname $container_path)"

        if command -v apptainer &> /dev/null; then
            apptainer pull "$container_path" docker://texlive/texlive:latest >/dev/null 2>&1
        elif command -v singularity &> /dev/null; then
            singularity pull "$container_path" docker://texlive/texlive:latest >/dev/null 2>&1
        else
            return 1
        fi

        [ -f "$container_path" ] && export STXW_APPTAINER_TEXLIVE="$container_path"
    fi

    TEXLIVE_CONTAINER="$container_path"
    return 0
}

function determine_previous() {
    local base_tex=$(ls -v "$STXW_VERSIONS_DIR"/compiled_v*base.tex 2>/dev/null | tail -n 1)
    local latest_tex=$(ls -v "$STXW_VERSIONS_DIR"/compiled_v[0-9]*.tex 2>/dev/null | tail -n 1)
    local current_tex="$STXW_COMPILED_TEX"

    if [[ -n "$base_tex" ]]; then
        echo "$base_tex"
    elif [[ -n "$latest_tex" ]]; then
        echo "$latest_tex"
    else
        echo "$current_tex"
    fi
}

function take_diff_tex() {
    local previous=$(determine_previous)

    echo_info "    Creating diff between versions..."

    if [ ! -f "$STXW_COMPILED_TEX" ]; then
        echo_warning "    $STXW_COMPILED_TEX not found."
        return 1
    fi

    if [ "$previous" == "$STXW_COMPILED_TEX" ]; then
        echo_warning "    No previous version found for comparison"
        return 1
    fi

    latexdiff \
        --encoding=utf8 \
        --type=CULINECHBAR \
        --disable-citation-markup \
        --append-safecmd="cite,citep,citet" \
        "$previous" "$STXW_COMPILED_TEX" > "$STXW_DIFF_TEX" 2>/dev/null

    if [ -s "$STXW_DIFF_TEX" ]; then
        echo_success "    $STXW_DIFF_TEX created"
        return 0
    else
        echo_warning "    $STXW_DIFF_TEX is empty - documents may be identical"
        return 1
    fi
}

compile_diff_tex() {
    echo_info "    Compiling diff document..."

    local abs_dir=$(realpath "$ORIG_DIR")
    local tex_file="$STXW_DIFF_TEX"
    local tex_base="${STXW_DIFF_TEX%.tex}"
    local compilation_method=""

    # Determine compilation method (same priority as main script)
    if command -v pdflatex &> /dev/null; then
        compilation_method="native"
    elif command -v apptainer &> /dev/null || command -v singularity &> /dev/null; then
        setup_container && compilation_method="container"
    elif command -v module &> /dev/null && module avail texlive &> /dev/null 2>&1; then
        module load texlive
        command -v pdflatex &> /dev/null && compilation_method="native"
    fi

    if [ -z "$compilation_method" ]; then
        echo_error "    No LaTeX installation found"
        return 1
    fi

    # Build commands
    if [ "$compilation_method" = "container" ]; then
        local runtime=$(command -v apptainer &> /dev/null && echo "apptainer" || echo "singularity")
        local container_base="$runtime exec --bind ${abs_dir}:${abs_dir} --pwd ${abs_dir} $TEXLIVE_CONTAINER"
        local pdf_cmd="$container_base pdflatex -output-directory=$(dirname $tex_file) -shell-escape -interaction=nonstopmode -file-line-error"
        local bib_cmd="$container_base bibtex"
    else
        local pdf_cmd="pdflatex -output-directory=$(dirname $tex_file) -shell-escape -interaction=nonstopmode -file-line-error"
        local bib_cmd="bibtex"
    fi

    # Compilation function
    run_pass() {
        local cmd="$1"
        local desc="$2"

        echo_info "    $desc"
        local start=$(date +%s)

        if [ "$STXW_VERBOSE_PDFLATEX" == "true" ]; then
            $cmd 2>&1 | grep -v "gocryptfs not found"
        else
            $cmd >/dev/null 2>&1
        fi

        echo_info "      ($(($(date +%s) - $start))s)"
    }

    # Compile
    run_pass "$pdf_cmd $tex_file" "Pass 1/3: Initial"

    if [ -f "${tex_base}.aux" ] && grep -q "\\citation" "${tex_base}.aux" 2>/dev/null; then
        run_pass "$bib_cmd $tex_base" "Processing bibliography"
    fi

    run_pass "$pdf_cmd $tex_file" "Pass 2/3: Bibliography"
    run_pass "$pdf_cmd $tex_file" "Pass 3/3: Final"
}

cleanup() {
    if [ -f "$STXW_DIFF_PDF" ]; then
        local size=$(du -h "$STXW_DIFF_PDF" | cut -f1)
        echo_success "    $STXW_DIFF_PDF ready (${size})"
        sleep 1
    else
        echo_warning "    $STXW_DIFF_PDF not created"
    fi
}

main() {
    local start_time=$(date +%s)

    if take_diff_tex; then
        compile_diff_tex
    fi

    cleanup
    echo_info "    Total time: $(($(date +%s) - start_time))s"
}

main "$@"

# EOF