#!/bin/bash

-my-pdflatex-compile() {
    # Usage: `my-pdflatex-compile input_file [output_file]`
    input_filename=$1
    output_filename=${2:-$1}  # Use second argument if provided, otherwise use input filename
    pdflatex -interaction=nonstopmode -jobname="$output_filename" "$input_filename.tex" 2>&1 > /dev/null
    bibtex "$output_filename" 2>&1 > /dev/null
    pdflatex -interaction=nonstopmode -jobname="$output_filename" "$input_filename.tex" 2>&1 > /dev/null
    pdflatex -interaction=nonstopmode -jobname="$output_filename" "$input_filename.tex" 2>&1 > /dev/null
}

# -my-pdflatex-compile() {
#     filename=$1
#     pdflatex -interaction=nonstopmode "$filename.tex"
#     bibtex "$filename"
#     pdflatex -interaction=nonstopmode "$filename.tex"
#     pdflatex -interaction=nonstopmode "$filename.tex"
# }


-my-pdflatex-countwords() {
    filename=$1
    local n_words=$(texcount "$filename.tex" -inc -1 -sum | grep -oE '[0-9]+' | sed ':a;s/\B[0-9]\{3\}\>/,&/;ta')
    sed -i "s/([0-9,]* words)/($n_words words)/" "$filename.tex"
}

-my-pdflatex-cleanup() {
    filename=$1
    mkdir -p .pdflatex_logs
    for ext in log aux blg bbl out spl; do
        [ -f "${filename}.${ext}" ] && mv "${filename}.${ext}" .pdflatex_logs/
    done
}

-my-pdflatex() {
    ORIG_DIR=$PWD
    local texfile="$1"
    local dir=$(dirname "$texfile")
    local filename=$(basename "${texfile%.*}")

    cd "$dir"

    -my-pdflatex-countwords $filename 2>&1 > /dev/null
    -my-pdflatex-compile $filename
    -my-pdflatex-cleanup $filename
    # if [[ -e "compile.sh" ]]; then
    #     echo -e "\ncompile.sh found. Running this script..."
    #     ./compile.sh
    # else
    #     -my-pdflatex-countwords $filename
    #     -my-pdflatex-compile $filename
    #     -my-pdflatex-cleanup $filename
    # fi

    cd "$ORIG_DIR"
}

-my-pdflatex ./main/revision.tex

# EOF
