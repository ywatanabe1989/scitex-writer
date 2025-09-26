#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 23:09:27 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config/config_manuscript.src
echo_info "$0 ..."

compile_compiled_tex() {
    local pdf_latex_command="pdflatex \
        -shell-escape \
        -interaction=nonstopmode \
        -file-line-error \
        $STXW_COMPILED_TEX"
    local bibtex_command="bibtex ${STXW_COMPILED_TEX%.tex}"

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
    if [ -f $STXW_COMPILED_PDF ]; then
        echo_success "$STXW_COMPILED_PDF ready"
        sleep 1
    else
        echo_error "$STXW_COMPILED_PDF was not created."
        # Extract errors from main.log
        local log_file={$STXW_COMPILED_PDF%.pdf}.log
        cat $log_file | grep error | grep -v -E "infwarerr|error style messages enabled"
        echo_error "$STXW_COMPILED_PDF not found. Stopping. Check $log_file"
        return 1
    fi
}

main() {
    compile_compiled_tex
    cleanup
}

main

# EOF