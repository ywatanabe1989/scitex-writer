#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-27 00:15:55 (ywatanabe)"
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
source ./config/load_config.sh $STXW_DOC_TYPE

# Source the shared LaTeX commands module
source "$(dirname ${BASH_SOURCE[0]})/command_switching.src"

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0 ..."


function determine_previous() {
    local base_tex=$(ls -v "$STXW_VERSIONS_DIR"/*_v*base.tex 2>/dev/null | tail -n 1)
    local latest_tex=$(ls -v "$STXW_VERSIONS_DIR"/*_v[0-9]*.tex 2>/dev/null | tail -n 1)
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

    echo_info "    Creating diff between archive..."

    if [ ! -f "$STXW_COMPILED_TEX" ]; then
        echo_warning "    $STXW_COMPILED_TEX not found."
        return 1
    fi

    # Get latexdiff command from shared module
    local latexdiff_cmd=$(get_cmd_latexdiff "$ORIG_DIR")

    if [ -z "$latexdiff_cmd" ]; then
        echo_error "    latexdiff not found (native, module, or container)"
        return 1
    fi

    # echo_info "    Using latexdiff command: $latexdiff_cmd"

    $latexdiff_cmd \
        --encoding=utf8 \
        --type=CULINECHBAR \
        --disable-citation-markup \
        --append-safecmd="cite,citep,citet" \
        "$previous" "$STXW_COMPILED_TEX" 2> >(grep -v 'gocryptfs not found' >&2) > "$STXW_DIFF_TEX"

    if [ -f "$STXW_DIFF_TEX" ] && [ -s "$STXW_DIFF_TEX" ]; then
        echo_success "    $STXW_DIFF_TEX created"
        return 0
    else
        echo_warn "    $STXW_DIFF_TEX not created or is empty"
        return 1
    fi
}

compile_diff_tex() {
    echo_info "    Compiling diff document..."

    local abs_dir=$(realpath "$ORIG_DIR")
    local tex_file="$STXW_DIFF_TEX"
    local tex_base="${STXW_DIFF_TEX%.tex}"

    # Get commands from shared module
    local pdf_cmd=$(get_cmd_pdflatex "$ORIG_DIR")
    local bib_cmd=$(get_cmd_bibtex "$ORIG_DIR")

    if [ -z "$pdf_cmd" ] || [ -z "$bib_cmd" ]; then
        echo_error "    No LaTeX installation found (native, module, or container)"
        return 1
    fi

    # echo_info "    Using pdflatex command: $pdf_cmd"

    # Add compilation options
    pdf_cmd="$pdf_cmd -output-directory=$(dirname $tex_file) -shell-escape -interaction=nonstopmode -file-line-error"

    # Compilation function
    run_pass() {
        local cmd="$1"
        local desc="$2"

        echo_info "    $desc"
        local start=$(date +%s)

        if [ "$STXW_VERBOSE_PDFLATEX" == "true" ]; then
            eval "$cmd" 2>&1 | grep -v "gocryptfs not found"
        else
            eval "$cmd" >/dev/null 2>&1
        fi

        echo_info "      ($(($(date +%s) - $start))s)"
    }

    # Compile
    run_pass "$pdf_cmd $tex_file" "Pass 1/3: Initial"

    if [ -f "${tex_base}.aux" ] && grep -q "\\citation" "${tex_base}.aux" \
                                        2>/dev/null; then
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
        echo_warn "    $STXW_DIFF_PDF not created"
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