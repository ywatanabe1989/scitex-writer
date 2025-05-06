#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 12:50:50 (ywatanabe)"
# File: ./manuscript/scripts/sh/modules/compile_diff_tex.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


YELLOW="\033[1;33m"
NC="\033[0m"
RED="\033[1;31m"

echo -e "$0 ..."

compile_diff_tex() {
    input_diff_tex=./diff.tex
    output_diff_pdf=./diff.pdf

    if [ ! -f $input_diff_tex ]; then echo "${RED}Not found: $input_diff_tex${NC}"; fi

    # Main
    pdf_latex_command="pdflatex \
        -shell-escape \
        -interaction=nonstopmode \
        -file-line-error \
        $input_diff_tex"

    if [ -f $input_diff_tex ]; then
        echo -e "Compiling $input_diff_tex..."
        eval "$pdf_latex_command"
        bibtex diff
        eval "$pdf_latex_command"
        eval "$pdf_latex_command"
        if [ -f $output_diff_pdf ]; then echo -e "${YELLOW}Compiled: $output_diff_pdf${NC}"; fi
    else
        echo -e "$input_diff_tex is empty. Skip compiling $input_diff_tex"
    fi
}

cleanup() {
    if [ -f ./diff.pdf ]; then
        echo -e "${YELLOW}Congratulations! ./diff.pdf is ready.${NC}"
        sleep 3
    else
        echo -e "${RED}Unfortunately, ./diff.pdf was not created.${NC}"
        # Extract errors from main.log
        cat main.log | grep error | grep -v -E "infwarerr|error style messages enabled"
        echo "Error: diff.pdf not found. Stopping. Check main.log."
        exit 1
    fi
}

main() {
    local verbose="$1"
    if [ "$verbose" = true ]; then
       compile_diff_tex
    else
       compile_diff_tex > /dev/null
    fi
    cleanup
}

main "$@"



## EOF

# EOF