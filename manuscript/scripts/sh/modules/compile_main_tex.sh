#!/bin/bash

echo -e "$0 ...\n"

compile_main_tex() {
    # Ensure the main directory exists
    mkdir -p ./main
    
    echo -e "\nCompiling ./main.tex..."

    # Main
    pdf_latex_command="pdflatex \
        -shell-escape \
        -interaction=nonstopmode \
        -file-line-error \
        ./main.tex"

    # > /dev/null    

    # Make the compilation more robust
    eval "$pdf_latex_command" || true
    [ -f main.aux ] && bibtex main || true
    eval "$pdf_latex_command" || true
    eval "$pdf_latex_command" || true
}

cleanup() {
    if [ -f ./main.pdf ]; then
        # Ensure main directory exists
        mkdir -p ./main
        
        # Move files to main directory
        mv ./main.pdf ./main/main.pdf
        cp ./main/main.pdf ./main/manuscript.pdf
        
        # Move log files if they exist
        [ -f ./main.log ] && mv ./main.log ./main/main.log
        [ -f ./main.aux ] && mv ./main.aux ./main/main.aux
        [ -f ./main.bbl ] && mv ./main.bbl ./main/main.bbl
        [ -f ./main.blg ] && mv ./main.blg ./main/main.blg
        
        echo -e "\n\033[1;33mCongratulations! ./main/manuscript.pdf is ready.\033[0m"
        sleep 1
    else
        echo -e "\n\033[1;33mUnfortunately, ./main/manuscript.pdf was not created.\033[0m"                
        # Extract errors from main.log
        [ -f main.log ] && (mkdir -p ./main && mv main.log ./main/main.log)
        [ -f ./main/main.log ] && cat ./main/main.log | grep -A 3 "Error:" | head -n 20
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

