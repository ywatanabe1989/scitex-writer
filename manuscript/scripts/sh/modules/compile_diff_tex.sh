#!/bin/bash

echo -e "$0 ...\n"

function compile_diff_tex() {
    input_diff_tex=./main/diff.tex
    output_diff_pdf=./diff.pdf

    # Main
    pdf_latex_command="pdflatex \
        -shell-escape \
        -interaction=nonstopmode \
        -file-line-error \
        $input_diff_tex"
    
    if [ -s $input_diff_tex ]; then
        echo -e "\nCompiling $input_diff_tex..."

        eval "$pdf_latex_command"
        bibtex diff # 2>&1 > /dev/null
        eval "$pdf_latex_command"
        eval "$pdf_latex_command"        

        if [ -f $output_diff_pdf ]; then
            echo -e "\n\033[1;33mCompiled: $output_diff_pdf\033[0m"
        fi
    else
        echo -e "\n$input_diff_tex is empty. Skip compiling $input_diff_tex"
    fi
}

cleanup() {
    if [ -f ./diff.pdf ]; then
        mv ./diff.pdf ./main/diff.pdf
        echo -e "\n\033[1;33mCongratulations! ./main/diff.pdf is ready.\033[0m"
        sleep 3        
    else
        echo -e "\n\033[1;33mUnfortunately, ./main/diff.pdf was not created.\033[0m"        
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
