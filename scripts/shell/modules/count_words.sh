#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 23:09:29 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/count_words.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config/config_manuscript.src
echo_info "$0 ..."


init() {
    rm -f $STXW_WORDCOUNT_DIR/*.txt
    mkdir -p $STXW_WORDCOUNT_DIR
}

_count_elements() {
    local dir="$1"
    local pattern="$2"
    local output_file="$3"

    if [[ -n $(find "$dir" -name "$pattern" 2>/dev/null) ]]; then
        count=$(ls "$dir"/$pattern | wc -l)
        echo $count > "$output_file"
    else
        echo "0" > "$output_file"
    fi
}

_count_words() {
    local input_file="$1"
    local output_file="$2"

    texcount "$input_file" -inc -1 -sum > "$output_file"
}

count_tables() {
    _count_elements "$STXW_TABLE_COMPILED_DIR" "Table_ID_*.tex" "$STXW_WORDCOUNT_DIR/table_count.txt"
}

count_figures() {
    _count_elements "$STXW_FIGURE_COMPILED_DIR" "Figure_ID_*.tex" "$STXW_WORDCOUNT_DIR/figure_count.txt"
}

count_IMRaD() {
    for section in abstract introduction methods results discussion; do
        local section_tex="./src/$section.tex"
        if [ -e "$section_tex" ]; then
            _count_words "$section_tex" "$STXW_WORDCOUNT_DIR/${section}_count.txt"
        else
            echo 0 > "$STXW_WORDCOUNT_DIR/${section}_count.txt"
        fi
    done
    cat $STXW_WORDCOUNT_DIR/{introduction,methods,results,discussion}_count.txt | awk '{s+=$1} END {print s}' > $STXW_WORDCOUNT_DIR/imrd_count.txt
}

main() {
    init
    count_tables
    count_figures
    count_IMRaD
}

main

# EOF