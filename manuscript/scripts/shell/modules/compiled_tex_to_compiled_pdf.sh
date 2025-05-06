#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 12:50:54 (ywatanabe)"
# File: ./manuscript/scripts/sh/modules/compiled_tex_to_compiled_pdf.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


echo -e "$0 ..."

YELLOW="\033[1;33m"
NC="\033[0m"
RED="\033[1;31m"

compile_compiled_tex() {
    echo -e "Compiling ./compiled.tex..."

    # Main
    pdf_latex_command="pdflatex \
        -shell-escape \
        -interaction=nonstopmode \
        -file-line-error \
        ./compiled.tex"

    eval "$pdf_latex_command"
    bibtex compiled # > /dev/null
    eval "$pdf_latex_command"
    eval "$pdf_latex_command"
}

cleanup() {
    echo "======================================"
    if [ -f ./compiled.pdf ]; then
        echo -e "${YELLOW}Congratulations! ./compiled.pdf is ready.${NC}"
        sleep 3
    else
        echo -e "${RED}Unfortunately, ./compiled.pdf was not created.${NC}"
        # Extract errors from main.log
        cat main.log | grep error | grep -v -E "infwarerr|error style messages enabled"
        echo -e "${RED}Error: compiled.pdf not found. Stopping. Check main.log.${NC}"
        return 1
    fi
}

main() {
    local verbose="$1"
    if [ "$verbose" = true ]; then
       compile_compiled_tex
    else
       compile_compiled_tex # > /dev/null
    fi
    cleanup
}

main "$@"

# ./scripts/shell/modules/compiled_tex_to_compiled_pdf.sh

# EOF