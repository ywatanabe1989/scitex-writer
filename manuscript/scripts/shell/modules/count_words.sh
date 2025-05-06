#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 21:21:52 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/count_words.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./scripts/shell/modules/config.src
echo_info "$0 ..."


init() {
    rm -f $WORDCOUNT_DIR/*.txt
    mkdir -p $WORDCOUNT_DIR
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
    _count_elements "$TABLE_COMPILED_DIR" "Table_ID_*.tex" "$WORDCOUNT_DIR/table_count.txt"
}

count_figures() {
    _count_elements "$FIGURE_COMPILED_DIR" "Figure_ID_*.tex" "$WORDCOUNT_DIR/figure_count.txt"
}

count_IMRaD() {
    for section in abstract introduction methods results discussion; do
        local section_tex="./src/$section.tex"
        if [ -e "$section_tex" ]; then
            _count_words "$section_tex" "$WORDCOUNT_DIR/${section}_count.txt"
        else
            echo 0 > "$WORDCOUNT_DIR/${section}_count.txt"
        fi
    done
    cat $WORDCOUNT_DIR/{introduction,methods,results,discussion}_count.txt | awk '{s+=$1} END {print s}' > $WORDCOUNT_DIR/imrd_count.txt
}

main() {
    init
    count_tables
    count_figures
    count_IMRaD
}

main

# EOF