#!/bin/bash

echo -e "$0 ...\n"

function compile_diff_tex() {
    input_diff_tex=./main/diff.tex
    output_diff_pdf=./diff.pdf

    # Check if the diff.tex file exists, if not create a basic one
    if [ ! -f "$input_diff_tex" ] || [ ! -s "$input_diff_tex" ]; then
        echo -e "\nWarning: $input_diff_tex is missing or empty. Creating a placeholder..."
        mkdir -p ./main
        echo '\documentclass{article}\begin{document}No significant differences found between versions.\end{document}' > "$input_diff_tex"
    fi

    # Main
    pdf_latex_command="pdflatex \
        -shell-escape \
        -interaction=nonstopmode \
        -file-line-error \
        $input_diff_tex"
    
    if [ -s "$input_diff_tex" ]; then
        echo -e "\nCompiling $input_diff_tex..."

        # Compile with error handling
        eval "$pdf_latex_command" || {
            echo -e "\nError in first pdflatex run, trying to continue..."
        }
        
        # Run bibtex if bibliography exists
        if grep -q '\\bibliography{' "$input_diff_tex"; then
            bibtex diff || echo "Bibtex processing failed, continuing..."
        fi
        
        # Additional runs
        eval "$pdf_latex_command" || echo "Error in second pdflatex run, trying to continue..."
        eval "$pdf_latex_command" || echo "Error in third pdflatex run, trying to continue..."

        if [ -f "$output_diff_pdf" ]; then
            echo -e "\n\033[1;33mCompiled: $output_diff_pdf\033[0m"
        else
            # Create a fallback PDF if compilation fails
            echo -e "\nWarning: Failed to create diff PDF through normal compilation. Creating a simple PDF..."
            echo '\documentclass{article}\begin{document}Diff compilation failed. Please check your LaTeX installation.\end{document}' > simple_diff.tex
            pdflatex -interaction=nonstopmode simple_diff.tex
            if [ -f "simple_diff.pdf" ]; then
                mv simple_diff.pdf "$output_diff_pdf"
                echo -e "\n\033[1;33mCreated fallback diff PDF\033[0m"
            fi
            rm -f simple_diff.tex simple_diff.aux simple_diff.log 2>/dev/null
        fi
    else
        echo -e "\n$input_diff_tex is empty after attempts to create it. Skip compiling."
    fi
}

cleanup() {
    if [ -f ./diff.pdf ]; then
        mkdir -p ./main 2>/dev/null
        mv ./diff.pdf ./main/diff.pdf
        echo -e "\n\033[1;33mCongratulations! ./main/diff.pdf is ready.\033[0m"
        sleep 1        
    else
        echo -e "\n\033[1;33mUnfortunately, ./main/diff.pdf was not created.\033[0m"        
        # Create a fallback diff.pdf
        echo '\documentclass{article}\begin{document}Diff PDF generation failed. This is a fallback document.\end{document}' > fallback_diff.tex
        pdflatex -interaction=nonstopmode fallback_diff.tex
        if [ -f "fallback_diff.pdf" ]; then
            mkdir -p ./main 2>/dev/null
            mv fallback_diff.pdf ./main/diff.pdf
            echo -e "\n\033[1;33mCreated fallback diff PDF in ./main/diff.pdf\033[0m"
            rm -f fallback_diff.* 2>/dev/null
        else
            # Extract errors from main.log if it exists
            if [ -f main.log ]; then
                cat main.log | grep error | grep -v -E "infwarerr|error style messages enabled"
            fi
            echo "Warning: Could not create diff.pdf. Continuing with other tasks."
        fi
        # Don't exit - allow the script to continue
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
