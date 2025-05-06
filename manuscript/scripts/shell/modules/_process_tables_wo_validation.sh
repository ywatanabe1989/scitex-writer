#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 23:53:40 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/process_tables.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config.src
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

        # Determine the number of columns in the CSV file
        num_columns=$(head -n 1 "$csv_file" | awk -F, '{print NF}')
        # num_columns=$(head -n 1 "$csv_file" | awk -F, '{print NF-1}')

        # fontsize="\\small"
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
                for header in "${headers[@]}"; do
                    header=$(echo "$header" | sed -e 's/±/\\pm/g' -e 's/%/\\%/g' -e 's/ /\\ /g' -e 's/#/\\#/g')
                    echo -n "\\textbf{\\thead{\$\mathrm{$header}\$}} & "
                done
                echo "\\\\"
            }
            echo "\\midrule"

            # Replace Windows-style newlines first
            tr -d '\r' < "$csv_file" > "${csv_file}.unix"

            awk 'BEGIN {FPAT = "([^,]*)|(\"[^\"]+\")"; OFS=" & "; row_count=0}
            NR>1 {
                if (row_count % 2 == 1) {print "\\rowcolor{lightgray}"}
                for (i=1; i<=NF; i++) {
                    if ($i != "") {
                        gsub(/^"|"$/, "", $i)  # Remove surrounding quotes for non-empty cells
                        gsub(/±/, "\\pm", $i)
                        # gsub(/%/, "\\%", $i)
                        gsub(/%/, "\\\\%", $i)
                        gsub(/ /, "\\ ", $i)
                        gsub(/#/, "\\#", $i)
                        gsub(/\r/, "", $i)  # Remove carriage return
                        $i = "$\\mathrm{" $i "}$"
                    } else {
                        $i = ""  # Output empty cells as {}
                    }
                }
                $1=$1
                print $0"\\\\"
                row_count++
            }' "${csv_file}.unix"

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
}


main() {
    init_tables
    ensure_lower_letter_id
    ensure_caption
    csv2tex
    compile_table_tex_files
    }

main

# EOF