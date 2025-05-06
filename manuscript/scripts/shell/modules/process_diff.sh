#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-07 00:14:31 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/process_diff.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config.src
echo_info "$0 ..."


function determine_previous() {
    # Determines the base TeX file for diff comparison
    # Usage: previous=$(determine_previous)

    local base_tex=$(ls -v "$VERSIONS_DIR"/compiled_v*base.tex 2>/dev/null | tail -n 1)
    local latest_tex=$(ls -v "$VERSIONS_DIR"/compiled_v[0-9]*.tex 2>/dev/null | tail -n 1)
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

    # echo -e "Taking diff between $previous & $COMPILED_TEX"
    if [ -f "$COMPILED_TEX" ]; then
        latexdiff "$previous" "$COMPILED_TEX" > "$DIFF_TEX" 2>/dev/null
        if [ -s "$DIFF_TEX" ]; then
            echo_success "$DIFF_TEX created"
        else
            echo_warn "$$DIFF_TEX is empty. $previous and $COMPILED_TEX may be identical.${NC}"
        fi
    else
        echo_error "$COMPILED_TEX not found."
    fi

    # cleanup_if_fake_previous "$previous"
}

compile_diff_tex() {
    local pdf_latex_command="pdflatex \
        -shell-escape \
        -interaction=nonstopmode \
        -file-line-error \
        $DIFF_TEX"
    local bibtex_command="bibtex ${DIFF_TEX%.tex}"

    if [ "$VERBOSE_PDFLATEX" != "true" ]; then
        pdf_latex_command="$pdf_latex_command >/dev/null 2>&1"
    fi

    if [ "$VERBOSE_BIBTEX" != "true" ]; then
        bibtex_command="$bibtex_command >/dev/null 2>&1"
    fi

    eval "$pdf_latex_command"
    eval "$bibtex_command"
    eval "$pdf_latex_command"
    eval "$pdf_latex_command"
}

cleanup() {
    local log_file={$COMPILED_TEX%.tex}.log
    if [ -f ./diff.pdf ]; then
        echo_success "$DIFF_PDF ready"
        sleep 3
    else
        echo_error "$DIFF_PDF not created."
        # Extract errors from main.log
        cat main.log | grep error | grep -v -E "infwarerr|error style messages enabled"
        echo_error "$DIFF_PDF not found. Stopping. Check $log_file."
        exit 1
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