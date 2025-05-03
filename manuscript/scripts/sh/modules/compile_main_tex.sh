#!/bin/bash

echo -e "$0 ...\n"

compile_main_tex() {
    echo -e "\nCompiling ./main/main.tex..."

    # Main
    pdf_latex_command="pdflatex \
        -shell-escape \
        -interaction=nonstopmode \
        -file-line-error \
        ./main.tex"

    # > /dev/null    

    eval "$pdf_latex_command"
    bibtex main # > /dev/null
    eval "$pdf_latex_command"
    eval "$pdf_latex_command"
}

cleanup() {
    if [ -f ./main.pdf ]; then
        mv ./main.pdf ./main/main.pdf
        cp ./main/main.pdf ./main/manuscript.pdf
        echo -e "\n\033[1;33mCongratulations! ./main/manuscript.pdf is ready.\033[0m"
        sleep 3
    else
        echo -e "\n\033[1;33mUnfortunately, ./main/manuscript.pdf was not created.\033[0m"                
        # Extract errors from main.log
        cat main.log | grep error | grep -v -E "infwarerr|error style messages enabled"
        echo "Error: main.pdf not found. Stopping. Check main.log."
        return 1
    fi
}    

main() {
    local verbose="$1"
    if [ "$verbose" = true ]; then
       compile_main_tex
    else
       compile_main_tex > /dev/null
    fi
    cleanup
}

main "$@"

# ./scripts/sh/modules/compile_main.tex.sh

## EOF

