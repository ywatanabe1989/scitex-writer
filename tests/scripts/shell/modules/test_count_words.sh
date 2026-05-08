#!/bin/bash
# -*- coding: utf-8 -*-
# Test file for: count_words.sh

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(realpath "$THIS_DIR/../..")"

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

assert_success() {
    local cmd="$1"
    local desc="${2:-$cmd}"
    ((TESTS_RUN++))
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $desc"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} $desc"
        ((TESTS_FAILED++))
    fi
}

assert_file_exists() {
    local file="$1"
    ((TESTS_RUN++))
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} File exists: $file"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗${NC} File missing: $file"
        ((TESTS_FAILED++))
    fi
}

# Add your tests here
test_placeholder() {
    echo "TODO: Add tests for count_words.sh"
}

# Run tests
main() {
    echo "Testing: count_words.sh"
    echo "========================================"

    test_placeholder

    echo "========================================"
    echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
    [ $TESTS_FAILED -gt 0 ] && exit 1
    exit 0
}

main "$@"

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/shell/modules/count_words.sh
# --------------------------------------------------------------------------------
# #!/bin/bash
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-09-26 10:52:54 (ywatanabe)"
# # File: ./paper/scripts/shell/modules/count_words.sh
# 
# ORIG_DIR="$(pwd)"
# THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
# LOG_PATH="$THIS_DIR/.$(basename $0).log"
# echo > "$LOG_PATH"
# 
# GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
# 
# GRAY='\033[0;90m'
# GREEN='\033[0;32m'
# YELLOW='\033[0;33m'
# RED='\033[0;31m'
# NC='\033[0m' # No Color
# 
# echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
# log_info() {
#     if [ "${SCITEX_LOG_LEVEL:-1}" -ge 2 ]; then
#         echo -e "  \033[0;90m→ $1\033[0m"
#     fi
# }
# echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
# echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
# echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
# echo_header() { echo_info "=== $1 ==="; }
# # ---------------------------------------
# 
# # Configurations
# source ./config/load_config.sh $SCITEX_WRITER_DOC_TYPE
# 
# # Source the 00_shared command switching module
# source "$(dirname ${BASH_SOURCE[0]})/command_switching.src"
# 
# # Logging
# touch "$LOG_PATH" >/dev/null 2>&1
# echo
# log_info "Running $0 ..."
# 
# init() {
#     rm -f $SCITEX_WRITER_WORDCOUNT_DIR/*.txt
#     mkdir -p $SCITEX_WRITER_WORDCOUNT_DIR
# }
# 
# _count_elements() {
#     local dir="$1"
#     local pattern="$2"
#     local output_file="$3"
# 
#     if [[ -n $(find "$dir" -name "$pattern" 2>/dev/null) ]]; then
#         # Count files matching pattern, excluding *_Header.tex and FINAL.tex
#         count=$(ls "$dir"/$pattern 2>/dev/null | grep -v "_Header.tex" | grep -v "FINAL.tex" | wc -l)
#         echo $count > "$output_file"
#     else
#         echo "0" > "$output_file"
#     fi
# }
# 
# # Cache texcount command (resolved once, used multiple times)
# TEXCOUNT_CMD=""
# 
# _count_words() {
#     local input_file="$1"
#     local output_file="$2"
# 
#     # Use cached command if available
#     if [ -z "$TEXCOUNT_CMD" ]; then
#         echo_error "    texcount not found"
#         return 1
#     fi
# 
#     eval "$TEXCOUNT_CMD \"$input_file\" -inc -1 -sum 2> >(grep -v 'gocryptfs not found' >&2)" > "$output_file"
# }
# 
# count_tables() {
#     _count_elements "$SCITEX_WRITER_TABLE_COMPILED_DIR" "[0-9]*.tex" "$SCITEX_WRITER_WORDCOUNT_DIR/table_count.txt"
# }
# 
# count_figures() {
#     _count_elements "$SCITEX_WRITER_FIGURE_COMPILED_DIR" "[0-9]*.tex" "$SCITEX_WRITER_WORDCOUNT_DIR/figure_count.txt"
# }
# 
# count_IMRaD() {
#     for section in abstract introduction methods results discussion; do
#         local section_tex="$SCITEX_WRITER_ROOT_DIR/contents/$section.tex"
#         if [ -e "$section_tex" ]; then
#             _count_words "$section_tex" "$SCITEX_WRITER_WORDCOUNT_DIR/${section}_count.txt"
#         else
#             echo 0 > "$SCITEX_WRITER_WORDCOUNT_DIR/${section}_count.txt"
#         fi
#     done
# 
#     # Calculate IMRD total (only count sections that exist)
#     local imrd_total=0
#     for section in introduction methods results discussion; do
#         if [ -f "$SCITEX_WRITER_WORDCOUNT_DIR/${section}_count.txt" ]; then
#             local count=$(cat "$SCITEX_WRITER_WORDCOUNT_DIR/${section}_count.txt" 2>/dev/null || echo 0)
#             imrd_total=$((imrd_total + count))
#         fi
#     done
#     echo "$imrd_total" > "$SCITEX_WRITER_WORDCOUNT_DIR/imrd_count.txt"
# }
# 
# display_counts() {
#     local fig_count=$(cat "$SCITEX_WRITER_WORDCOUNT_DIR/figure_count.txt" 2>/dev/null || echo 0)
#     local tab_count=$(cat "$SCITEX_WRITER_WORDCOUNT_DIR/table_count.txt" 2>/dev/null || echo 0)
#     local abs_count=$(cat "$SCITEX_WRITER_WORDCOUNT_DIR/abstract_count.txt" 2>/dev/null || echo 0)
#     local imrd_count=$(cat "$SCITEX_WRITER_WORDCOUNT_DIR/imrd_count.txt" 2>/dev/null || echo 0)
#     
#     echo_success "    Word counts updated:"
#     echo_success "      Figures: $fig_count"
#     echo_success "      Tables: $tab_count"
#     
#     # For supplementary, don't show abstract if it doesn't exist
#     if [ "$SCITEX_WRITER_DOC_TYPE" = "supplementary" ]; then
#         if [ "$abs_count" -gt 0 ]; then
#             echo_success "      Abstract: $abs_count words"
#         fi
#         if [ "$imrd_count" -gt 0 ]; then
#             echo_success "      Supplementary text: $imrd_count words"
#         fi
#     else
#         echo_success "      Abstract: $abs_count words"
#         echo_success "      Main text (IMRD): $imrd_count words"
#     fi
# }
# 
# main() {
#     # Resolve texcount command once at startup
#     TEXCOUNT_CMD=$(get_cmd_texcount "$ORIG_DIR")
# 
#     if [ -z "$TEXCOUNT_CMD" ]; then
#         echo_error "    texcount not found"
#         return 1
#     fi
# 
#     init
#     count_tables
#     count_figures
#     count_IMRaD
#     display_counts
# }
# 
# main
# 
# # EOF
# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/shell/modules/count_words.sh
# --------------------------------------------------------------------------------
