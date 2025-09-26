#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-07 01:33:45 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/process_tables.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config/config_manuscript.src
echo_info "$0 ..."

function init_tables() {
    # Cleanup and prepare directories
    rm -f "$STXW_TABLE_COMPILED_DIR"/*.tex
    mkdir -p "$STXW_TABLE_DIR" "$STXW_TABLE_CAPTION_MEDIA_DIR" "$STXW_TABLE_COMPILED_DIR" > /dev/null
    echo > "$STXW_TABLE_COMPILED_FILE"
}

function ensure_caption() {
    # Create default captions for any table without one
    for csv_file in "$STXW_TABLE_CAPTION_MEDIA_DIR"/Table_ID_*.csv; do
        [ -e "$csv_file" ] || continue
        local base_name=$(basename "$csv_file" .csv)
        local table_id=$(echo "$base_name" | grep -oP '(?<=Table_ID_)[^\.]+' | tr '[:upper:]' '[:lower:]')
        local caption_file="${STXW_TABLE_CAPTION_MEDIA_DIR}/${base_name}.tex"

        if [ ! -f "$caption_file" ] && [ ! -L "$caption_file" ]; then
            echo_warn "Caption file $caption_file not found. Creating a default one."
            mkdir -p $(dirname "$caption_file")
            cat > "$caption_file" << EOF
\\caption{Table $table_id: Default caption. Please edit $caption_file to customize.}
EOF
        fi
    done
}

function ensure_lower_letter_id() {
    # Ensure all table IDs use lowercase
    local ORIG_DIR="$(pwd)"
    cd "$STXW_TABLE_CAPTION_MEDIA_DIR"
    for file in Table_ID_*; do
        [ -e "$file" ] || continue
        new_name=$(echo "$file" | sed -E 's/(Table_ID_)(.*)/\1\L\2/')
        if [[ "$file" != "$new_name" ]]; then
            mv "$file" "$new_name"
        fi
    done
    cd "$ORIG_DIR"
}

function check_csv_for_special_chars() {
    # Check CSV file for potential problematic characters
    local csv_file="$1"
    local problem_chars="[&%$#_{}^~\\|<>]"
    local problems=$(grep -n "$problem_chars" "$csv_file" 2>/dev/null || echo "")
    if [ -n "$problems" ]; then
        echo_warn "Potential LaTeX special characters found in $csv_file:"
        echo -e ${YELLOW}
        echo "$problems" | head -5
        echo "These may need proper LaTeX escaping."
        echo -e ${NC}
    fi
}

function csv2tex() {
    # Compile CSV tables into LaTeX files
    for csv_file in "$STXW_TABLE_CAPTION_MEDIA_DIR"/Table_*.csv; do
        [ -e "$csv_file" ] || continue

        base_name=$(basename "$csv_file" .csv)
        table_id=$(basename "$csv_file" .csv | grep -oP '(?<=Table_ID_)[^\.]+' | tr '[:upper:]' '[:lower:]')
        caption_file="${STXW_TABLE_CAPTION_MEDIA_DIR}/${base_name}.tex"
        compiled_file="$STXW_TABLE_COMPILED_DIR/${base_name}.tex"

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
            echo "\\setlength{\\tabcolsep}{4pt}"
            echo "\\begin{tabular}{*{$num_columns}{r}}"
            echo "\\toprule"

            # Process header row with proper escaping
            head -n 1 "$csv_file" | awk -F, '{
                for (ii=1; ii<=NF; ii++) {
                    val = $ii
                    gsub(/%/, "\\\\%", val)
                    gsub(/&/, "\\\\&", val)
                    gsub(/_/, "\\\\_", val)
                    gsub(/\$/, "\\\\$", val)
                    gsub(/\{/, "\\\\{", val)
                    gsub(/\}/, "\\\\}", val)
                    gsub(/#/, "\\\\#", val)
                    printf("\\textbf{\\thead{$\\mathrm{%s}$}}", val)
                    if (ii < NF) printf(" & ")
                }
                print "\\\\"
            }'

            echo "\\midrule"

            awk 'BEGIN {FPAT = "([^,]+)|(\"[^\"]+\")"; OFS=" & "; row_count=0}
            NR>1 {
                if (row_count % 2 == 1) {print "\\rowcolor{lightgray}"}
                for (i=1; i<=NF; i++) {
                    gsub(/\-/, "$-$", $i)
                    gsub(/\*+/, "$&$", $i)
                    gsub(/\+/, "$+$", $i)
                    gsub(/_/, "\\_", $i)
                    gsub(/%/, "\\%", $i)
                }
                $1=$1
                print $0"\\\\"
                row_count++
            }' "$csv_file"

            echo "\\bottomrule"
            echo "\\end{tabular}"
            echo "\\captionsetup{width=\\textwidth}"

            # Use the caption file if it exists, otherwise create a default caption
            if [ -f "$caption_file" ] || [ -L "$caption_file" ]; then
                echo "\\input{$caption_file}"
            else
                echo "\\caption{Table $table_id}"
            fi

            echo "\\label{tab:${table_id}}"
            echo "\\end{table}"
            echo ""
            echo "\\restoregeometry"
        } > "$compiled_file"

        echo_info "$compiled_file compiled"
    done
}

function gather_table_tex_files() {
    # Gather all table tex files into the final compiled file
    output_file="${STXW_TABLE_COMPILED_FILE}"
    rm -f "$output_file" > /dev/null 2>&1
    echo "% Auto-generated file containing all table inputs" > "$output_file"

    # Count available tables
    table_count=0
    for table_tex in "$STXW_TABLE_COMPILED_DIR"/Table_*.tex; do
        if [ -f "$table_tex" ] || [ -L "$table_tex" ]; then
            echo "\\input{$table_tex}" >> "$output_file"
            table_count=$((table_count + 1))
        fi
    done

    if [ $table_count -eq 0 ]; then
        echo_warn "No tables were found to compile."
    else
        echo_success "$table_count tables compiled"
    fi
}

# Main execution
init_tables
ensure_lower_letter_id
ensure_caption
csv2tex
gather_table_tex_files

# EOF