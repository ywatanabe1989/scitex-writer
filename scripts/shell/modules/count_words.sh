#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 10:52:54 (ywatanabe)"
# File: ./paper/scripts/shell/modules/count_words.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

# Configurations
source ./config/load_config.sh $STXW_DOC_TYPE

# Source the shared command switching module
source "$(dirname ${BASH_SOURCE[0]})/command_switching.src"

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0 ..."

init() {
    rm -f $STXW_WORDCOUNT_DIR/*.txt
    mkdir -p $STXW_WORDCOUNT_DIR
}

_count_elements() {
    local dir="$1"
    local pattern="$2"
    local output_file="$3"

    if [[ -n $(find "$dir" -name "$pattern" 2>/dev/null) ]]; then
        # Count files matching pattern, excluding *_Header.tex and FINAL.tex
        count=$(ls "$dir"/$pattern 2>/dev/null | grep -v "_Header.tex" | grep -v "FINAL.tex" | wc -l)
        echo $count > "$output_file"
    else
        echo "0" > "$output_file"
    fi
}

_count_words() {
    local input_file="$1"
    local output_file="$2"
    
    # Get texcount command from shared module
    local texcount_cmd=$(get_cmd_texcount "$ORIG_DIR")
    
    if [ -z "$texcount_cmd" ]; then
        echo_error "    texcount not found"
        return 1
    fi

    eval "$texcount_cmd \"$input_file\" -inc -1 -sum 2> >(grep -v 'gocryptfs not found' >&2)" > "$output_file"
}

count_tables() {
    _count_elements "$STXW_TABLE_COMPILED_DIR" "[0-9]*.tex" "$STXW_WORDCOUNT_DIR/table_count.txt"
}

count_figures() {
    _count_elements "$STXW_FIGURE_COMPILED_DIR" "[0-9]*.tex" "$STXW_WORDCOUNT_DIR/figure_count.txt"
}

count_IMRaD() {
    for section in abstract introduction methods results discussion; do
        local section_tex="$STWX_ROOT_DIR/contents/$section.tex"
        if [ -e "$section_tex" ]; then
            _count_words "$section_tex" "$STXW_WORDCOUNT_DIR/${section}_count.txt"
        else
            echo 0 > "$STXW_WORDCOUNT_DIR/${section}_count.txt"
        fi
    done
    
    # Calculate IMRD total (only count sections that exist)
    local imrd_total=0
    for section in introduction methods results discussion; do
        if [ -f "$STXW_WORDCOUNT_DIR/${section}_count.txt" ]; then
            local count=$(cat "$STXW_WORDCOUNT_DIR/${section}_count.txt" 2>/dev/null || echo 0)
            imrd_total=$((imrd_total + count))
        fi
    done
    echo "$imrd_total" > "$STXW_WORDCOUNT_DIR/imrd_count.txt"
}

display_counts() {
    local fig_count=$(cat "$STXW_WORDCOUNT_DIR/figure_count.txt" 2>/dev/null || echo 0)
    local tab_count=$(cat "$STXW_WORDCOUNT_DIR/table_count.txt" 2>/dev/null || echo 0)
    local abs_count=$(cat "$STXW_WORDCOUNT_DIR/abstract_count.txt" 2>/dev/null || echo 0)
    local imrd_count=$(cat "$STXW_WORDCOUNT_DIR/imrd_count.txt" 2>/dev/null || echo 0)
    
    echo_success "    Word counts updated:"
    echo_success "      Figures: $fig_count"
    echo_success "      Tables: $tab_count"
    
    # For supplementary, don't show abstract if it doesn't exist
    if [ "$STXW_DOC_TYPE" = "supplementary" ]; then
        if [ "$abs_count" -gt 0 ]; then
            echo_success "      Abstract: $abs_count words"
        fi
        if [ "$imrd_count" -gt 0 ]; then
            echo_success "      Supplementary text: $imrd_count words"
        fi
    else
        echo_success "      Abstract: $abs_count words"
        echo_success "      Main text (IMRD): $imrd_count words"
    fi
}

main() {
    init
    count_tables
    count_figures
    count_IMRaD
    display_counts
}

main

# EOF