#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 10:52:43 (ywatanabe)"
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
source ./config/load_config.sh $MANUSCRIPT_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0 ..."

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
        echo_success "    $STXW_COMPILED_PDF ready"
        sleep 1
    else
        echo_error "    $STXW_COMPILED_PDF was not created."
        # Extract errors from main.log
        local log_file={$STXW_COMPILED_PDF%.pdf}.log
        cat $log_file | grep error | grep -v -E "infwarerr|error style messages enabled"
        echo_error "    $STXW_COMPILED_PDF not found. Stopping. Check $log_file"
        return 1
    fi
}

main() {
    compile_compiled_tex
    cleanup
}

main

# EOF