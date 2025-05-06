#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-07 00:48:39 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/process_tables.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config.src
source ./scripts/shell/modules/validate_tex.src
echo_info "$0 ..."

init_tables() {
    # Cleanup and prepare directories
    rm -f "$TABLE_COMPILED_DIR"/*.tex
    mkdir -p "$TABLE_CAPTION_MEDIA_DIR" "$TABLE_COMPILED_DIR"
    echo > "$TABLE_COMPILED_FILE"
}

ensure_caption() {
    # Usage: ensure_caption
    for csv_file in "$TABLE_CAPTION_MEDIA_DIR"/Table_ID_*.csv; do
        [ -e "$csv_file" ] || continue
        local filename=$(basename "$csv_file")
        local caption_tex_file="$TABLE_CAPTION_MEDIA_DIR/${filename%.csv}.tex"
        if [ ! -f "$caption_tex_file" ] && [ ! -L "$caption_tex_file" ]; then
            cp "$TABLE_CAPTION_MEDIA_DIR/_Table_ID_XX.tex" "$caption_tex_file"
        fi
    done
}

ensure_lower_letter_id() {
    local ORIG_DIR="$(pwd)"
    cd "$TABLE_CAPTION_MEDIA_DIR"
    for file in Table_ID_*; do
        if [[ -f "$file" || -L "$file" ]]; then
            new_name=$(echo "$file" | sed -E 's/(Table_ID_)(.*)/\1\L\2/')
            if [[ "$file" != "$new_name" ]]; then
                mv "$file" "$new_name"
            fi
        fi
    done
    cd $ORIG_DIR
}

# Check CSV file for potential problematic characters
check_csv_for_special_chars() {
    local csv_file="$1"
    local problem_chars="[&%$#_{}^~\\|<>]"
    local problems=$(grep -n "$problem_chars" "$csv_file")

    if [ -n "$problems" ]; then
        echo_warn "Potential LaTeX special characters found in $csv_file:"
        echo "$problems" | head -5
        echo "These may need proper LaTeX escaping."
    fi
}

csv2tex() {
    # Compile "$csv_dir"Table*.csv, with combining their corresponding caption tex files, as complete tex files.
    ii=0
    for csv_file in "$TABLE_CAPTION_MEDIA_DIR"/Table_ID_*.csv; do
        [ -e "$csv_file" ] || continue
        base_name=$(basename "$csv_file" .csv)
        table_id=$(basename "$csv_file" .csv | grep -oP '(?<=Table_ID_)[^\.]+' | tr '[:upper:]' '[:lower:]')
        caption_file=${TABLE_CAPTION_MEDIA_DIR}/${base_name}.tex
        width=$(grep -oP '(?<=width=)[0-9.]+\\textwidth' "$caption_file")
        compiled_file="$TABLE_COMPILED_DIR/${base_name}.tex"
        echo "" > "$compiled_file"
        # Pre-check CSV for problematic characters
        check_csv_for_special_chars "$csv_file"
        # Determine the number of columns in the CSV file
        num_columns=$(head -n 1 "$csv_file" | awk -F, '{print NF}')
        fontsize="\\tiny"
        # Create the LaTeX document
        {
            echo "\\pdfbookmark[2]{ID ${table_id}}{id_${table_id}}"
            echo "\\begin{table}[htbp]"
            echo "\\centering"
            echo "$fontsize"
            echo "\setlength{\tabcolsep}{4pt}"
            echo "\\begin{tabular}{*{$num_columns}{r}}"
            echo "\\toprule"
            # Header
            head -n 1 "$csv_file" | {
                IFS=',' read -ra headers
                for ii in "${!headers[@]}"; do
                    header=$(echo "${headers[$ii]}" | sed -e 's/±/\\pm/g' -e 's/%/\\%/g' -e 's/ /\\ /g' -e 's/#/\\#/g' -e 's/_/\\_/g' -e 's/&/\\&/g' -e 's/\$/\\$/g' -e 's/{/\\{/g' -e 's/}/\\}/g')
                    if [ $ii -eq $((${#headers[@]} - 1)) ]; then
                        echo -n "\\textbf{\\thead{\$\mathrm{$header}\$}}"
                    else
                        echo -n "\\textbf{\\thead{\$\mathrm{$header}\$}} & "
                    fi
                done
                echo "\\\\"
            }
            echo "\\midrule"
            # Replace Windows-style newlines first
            tr -d '\r' < "$csv_file" > "${csv_file}.unix"

            # Replace the awk processing in csv2tex with this simpler version
            sed '1d' "${csv_file}.unix" | while IFS=, read -r param value unit notes; do
                # Handle alternating row colors
                if [ $(( row_count % 2 )) -eq 1 ]; then
                    echo "\\rowcolor{lightgray}"
                fi

                # Escape special characters manually
                param=$(echo "$param" | sed -e 's/%/\\%/g' -e 's/&/\\&/g' -e 's/_/\\_/g' -e 's/#/\\#/g')
                value=$(echo "$value" | sed -e 's/%/\\%/g' -e 's/&/\\&/g' -e 's/_/\\_/g' -e 's/#/\\#/g')
                unit=$(echo "$unit" | sed -e 's/%/\\%/g' -e 's/&/\\&/g' -e 's/_/\\_/g' -e 's/#/\\#/g')
                notes=$(echo "$notes" | sed -e 's/%/\\%/g' -e 's/&/\\&/g' -e 's/_/\\_/g' -e 's/#/\\#/g')

                # Format as LaTeX table row
                echo "$\mathrm{$param}$ & $\mathrm{$value}$ & $\mathrm{$unit}$ & $\mathrm{$notes}$ \\\\"

                row_count=$((row_count+1))
            done

            # Optional: Remove the temporary file
            rm "${csv_file}.unix"
            echo "\\bottomrule"
            echo "\\end{tabular}"
            echo "\\captionsetup{width=\textwidth}"
            echo "\\input{${TABLE_CAPTION_MEDIA_DIR}/Table_ID_${table_id}}"
            echo "\\label{tab:${table_id}}"
            echo "\\end{table}"
            echo ""
            echo "\\restoregeometry"
        } >> $compiled_file

        # Validate with detailed error reporting and exit on failure
        validate_tex_file_and_exit "$compiled_file"

        echo_info "Successfully compiled $compiled_file"

    done
}

compile_table_tex_files() {
    # Gather ./src/tables/.tex/Table_*.tex files into ./src/tables/.tex/.All_Tables.tex
    echo "" > "$TABLE_COMPILED_FILE"
    for table_tex in "$TABLE_COMPILED_DIR"/Table_ID_*.tex; do
        if [ -f "$table_tex" ] || [ -L "$table_tex" ]; then
            fname="${table_tex%.tex}"
            echo "\input{${fname}}" >> "$TABLE_COMPILED_FILE"
        fi
    done

    # Validate the final compiled file if pdflatex is available
    if check_latex_available; then
        if ! validate_tex_file "$TABLE_COMPILED_FILE"; then
            echo_warn "The combined table file may have issues."
            echo_info "Please check $TABLE_COMPILED_FILE manually."
            show_latex_escape_reference
        else
            echo_info "TeX validation passed for combined table file."
        fi
    fi
}

main() {
    init_tables
    ensure_lower_letter_id
    ensure_caption
    csv2tex
    compile_table_tex_files

    export -f show_latex_escape_reference
    export -f latex_escape_reference
    echo "To view LaTeX escape character reference, run: show_latex_escape_reference"
}

main

# EOF