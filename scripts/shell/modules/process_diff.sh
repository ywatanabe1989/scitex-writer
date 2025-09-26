#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 11:08:00 (ywatanabe)"
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
source ./config/load_config.sh $MANUSCRIPT_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0 ..."


function determine_previous() {
    # Determines the base TeX file for diff comparison
    # Usage: previous=$(determine_previous)

    local base_tex=$(ls -v "$STXW_VERSIONS_DIR"/compiled_v*base.tex 2>/dev/null | tail -n 1)
    local latest_tex=$(ls -v "$STXW_VERSIONS_DIR"/compiled_v[0-9]*.tex 2>/dev/null | tail -n 1)
    local current_tex="./manuscript.tex"

    if [[ -n "$base_tex" ]]; then echo "$base_tex"
    elif [[ -n "$latest_tex" ]]; then echo "$latest_tex"
    else echo "$current_tex"; fi
}

function cleanup_if_fake_previous() {
    local previous=$1
    [[ "$previous" == /tmp/* ]] && rm -f "$previous"
}

function take_diff_tex() {
    # Generates LaTeX diff between base and current manuscript
    # Usage: take_diff_tex
    local previous=$(determine_previous)

    # echo -e "Taking diff between $previous & $STXW_COMPILED_TEX"
    if [ -f "$STXW_COMPILED_TEX" ]; then
        latexdiff "$previous" "$STXW_COMPILED_TEX" > "$STXW_DIFF_TEX" 2>/dev/null
        if [ -s "$STXW_DIFF_TEX" ]; then
            echo_success "    $STXW_DIFF_TEX created"
        else
            echo_warn "    $STXW_DIFF_TEX is empty.${NC}"
            echo_warn "    $previous and $STXW_COMPILED_TEX may be identical.${NC}"

        fi
    else
        echo_warn "    $STXW_COMPILED_TEX not found."
    fi

    # cleanup_if_fake_previous "$previous"
}

compile_diff_tex() {
    local pdf_latex_command="pdflatex \
        -shell-escape \
        -interaction=nonstopmode \
        -file-line-error \
        $STXW_DIFF_TEX"
    local bibtex_command="bibtex ${STXW_DIFF_TEX%.tex}"

    if [ "$STXW_VERBOSE_PDFLATEX" != "true" ]; then
        pdf_latex_command="$pdf_latex_command >/dev/null 2>&1"
    fi

    if [ "$STXW_VERBOSE_BIBTEX" != "true" ]; then
        bibtex_command="$bibtex_command >/dev/null 2>&1"
    fi

    eval "$pdf_latex_command"
    eval "$bibtex_command"
    eval "$pdf_latex_command"
    eval "$pdf_latex_command"
}

cleanup() {
    local log_file=${STXW_COMPILED_TEX%.tex}.log
    if [ -f ./diff.pdf ]; then
        echo_success "    $STXW_DIFF_PDF ready"
        sleep 3
    else
        echo_warn "    $STXW_DIFF_PDF not created."
        # Extract errors from main.log
        if [ -f $log_file ]; then
            cat $log_file | grep error | grep -v -E "infwarerr|error style messages enabled"
            echo_warn "    Check $log_file."
        fi
        # exit 1
    fi
}

main() {
    local verbose="$1"

    take_diff_tex
    compile_diff_tex
    # if [ "$verbose" = true ]; then
    #    compile_diff_tex
    # else
    #    compile_diff_tex > /dev/null
    # fi
    cleanup
}

main "$@"

# EOF