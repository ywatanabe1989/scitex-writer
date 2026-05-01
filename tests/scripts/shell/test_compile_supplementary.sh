#!/bin/bash
# -*- coding: utf-8 -*-
# Test file for: compile_supplementary.sh

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
    echo "TODO: Add tests for compile_supplementary.sh"
}

# Run tests
main() {
    echo "Testing: compile_supplementary.sh"
    echo "========================================"

    test_placeholder

    echo "========================================"
    echo "Results: $TESTS_PASSED/$TESTS_RUN passed"
    [ $TESTS_FAILED -gt 0 ] && exit 1
    exit 0
}

main "$@"

# --------------------------------------------------------------------------------
# Start of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/shell/compile_supplementary.sh
# --------------------------------------------------------------------------------
# #!/bin/bash
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-09-27 15:20:00 (ywatanabe)"
# # File: ./paper/scripts/shell/compile_supplementary.sh
# 
# # shellcheck disable=SC1091  # Don't follow sourced files
# 
# export ORIG_DIR
# ORIG_DIR="$(pwd)"
# THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# LOG_PATH="$THIS_DIR/.$(basename "$0").log"
# 
# # Resolve project root - critical for working directory independence (Issue #13)
# GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
# if [ -z "$GIT_ROOT" ]; then
#     GIT_ROOT="$(cd "$THIS_DIR/../.." && pwd)"
# fi
# export PROJECT_ROOT="$GIT_ROOT"
# 
# # Change to project root to ensure relative paths work
# cd "$PROJECT_ROOT" || exit 1
# 
# GRAY='\033[0;90m'
# GREEN='\033[0;32m'
# YELLOW='\033[0;33m'
# RED='\033[0;31m'
# NC='\033[0m' # No Color
# 
# echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
# echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
# echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
# echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
# echo_header() { echo_info "=== $1 ==="; }
# # ---------------------------------------
# 
# # Timestamp tracking functions
# STAGE_START_TIME=0
# COMPILATION_START_TIME=$(date +%s)
# 
# log_stage_start() {
#     local stage_name="$1"
#     STAGE_START_TIME=$(date +%s)
#     local timestamp=$(date '+%H:%M:%S')
#     echo_info "[$timestamp] Starting: $stage_name"
# }
# 
# log_stage_end() {
#     local stage_name="$1"
#     local end_time=$(date +%s)
#     local elapsed=$((end_time - STAGE_START_TIME))
#     local total_elapsed=$((end_time - COMPILATION_START_TIME))
#     local timestamp=$(date '+%H:%M:%S')
#     echo_success "[$timestamp] Completed: $stage_name (${elapsed}s elapsed, ${total_elapsed}s total)"
# }
# 
# # Configurations
# export SCITEX_WRITER_DOC_TYPE="supplementary"
# source ./config/load_config.sh "$SCITEX_WRITER_DOC_TYPE"
# echo
# 
# # Log
# touch $LOG_PATH >/dev/null 2>&1
# mkdir -p "$LOG_DIR" && touch "$SCITEX_WRITER_GLOBAL_LOG_FILE"
# 
# # Shell options
# set -e
# set -o pipefail
# 
# # Default values for arguments
# do_p2t=false
# no_figs=false
# no_tables=false
# do_verbose=false
# do_crop_tif=false
# do_force=false
# no_diff=false
# draft_mode=false
# dark_mode=false
# 
# usage() {
#     echo "Usage: $0 [options]"
#     echo "Options:"
#     echo "  -nf,  --no_figs       Exclude figures for quick compilation (default: false)"
#     echo "  -nt,  --no_tables     Exclude tables for quick compilation (default: false)"
#     echo "  -nd,  --no_diff       Skip diff generation (saves ~10s) (default: false)"
#     echo "  -d,   --draft         Draft mode: single-pass compilation (saves ~5s) (default: false)"
#     echo "  -dm,  --dark_mode     Dark mode: black background, white text (default: false)"
#     echo "  -p2t, --ppt2tif       Converts Power Point to TIF on WSL (default: $do_p2t)"
#     echo "  -c,   --crop_tif      Crop TIF images to remove excess whitespace (default: $do_crop_tif)"
#     echo "  -q,   --quiet         Do not shows detailed logs for latex compilation (default: $do_verbose)"
#     echo "  --force               Force full recompilation (ignore cache) (default: $do_force)"
#     echo "  -h,   --help          Display this help message"
#     echo ""
#     echo "Note: All options accept both hyphens and underscores (e.g., --no-figs or --no_figs)"
#     exit 0
# }
# 
# parse_arguments() {
#     while [[ "$#" -gt 0 ]]; do
#         # Normalize option: replace underscores with hyphens for matching
#         local normalized_opt=$(echo "$1" | tr '_' '-')
# 
#         case $normalized_opt in
#         -h | --help) usage ;;
#         -p2t | --ppt2tif) do_p2t=true ;;
#         -nf | --no-figs) no_figs=true ;;
#         -nt | --no-tables) no_tables=true ;;
#         -nd | --no-diff) no_diff=true ;;
#         -d | --draft) draft_mode=true ;;
#         -dm | --dark-mode) dark_mode=true ;;
#         -c | --crop-tif) do_crop_tif=true ;;
#         -v | --verbose) do_verbose=true ;;
#         -q | --quiet) do_verbose=false ;;
#         --force) do_force=true ;;
#         *)
#             echo "Unknown option: $1"
#             usage
#             ;;
#         esac
#         shift
#     done
# }
# 
# main() {
#     parse_arguments "$@"
# 
#     # Log command options
#     options_display=""
#     $do_p2t && options_display="${options_display} --ppt2tif"
#     $no_figs && options_display="${options_display} --no_figs"
#     $no_tables && options_display="${options_display} --no_tables"
#     $no_diff && options_display="${options_display} --no_diff"
#     $draft_mode && options_display="${options_display} --draft"
#     $dark_mode && options_display="${options_display} --dark_mode"
#     $do_crop_tif && options_display="${options_display} --crop_tif"
#     $do_verbose && options_display="${options_display} --verbose"
#     echo_info "Running $0${options_display}..."
# 
#     # Verbosity
#     export SCITEX_WRITER_VERBOSE_PDFLATEX=$do_verbose
#     export SCITEX_WRITER_VERBOSE_BIBTEX=$do_verbose
# 
#     # Draft mode (single-pass compilation)
#     export SCITEX_WRITER_DRAFT_MODE=$draft_mode
# 
#     # Dark mode (black background, white text)
#     export SCITEX_WRITER_DARK_MODE=$dark_mode
# 
#     # Check dependencies
#     log_stage_start "Dependency Check"
#     ./scripts/shell/modules/check_dependancy_commands.sh
#     log_stage_end "Dependency Check"
# 
#     # Merge bibliography files if multiple exist
#     log_stage_start "Bibliography Merge"
#     ./scripts/shell/modules/merge_bibliographies.sh
#     log_stage_end "Bibliography Merge"
# 
#     # Apply citation style from config
#     log_stage_start "Citation Style"
#     ./scripts/shell/modules/apply_citation_style.sh
#     log_stage_end "Citation Style"
# 
#     # Run independent processing in parallel for speed
#     local parallel_start=$(date +%s)
#     local timestamp=$(date '+%H:%M:%S')
#     echo_info "[$timestamp] Starting: Parallel Processing (Figures, Tables, Word Count)"
# 
#     # Create temp files for parallel job outputs
#     local temp_dir=$(mktemp -d)
#     local fig_log="$temp_dir/figures.log"
#     local tbl_log="$temp_dir/tables.log"
#     local wrd_log="$temp_dir/words.log"
# 
#     # Run all three in parallel
#     (
#         ./scripts/shell/modules/process_figures.sh "$no_figs" "$do_p2t" "$do_verbose" "$do_crop_tif" >"$fig_log" 2>&1
#         echo $? >"$temp_dir/fig_exit"
#     ) &
#     local fig_pid=$!
# 
#     (
#         ./scripts/shell/modules/process_tables.sh "$no_tables" >"$tbl_log" 2>&1
#         echo $? >"$temp_dir/tbl_exit"
#     ) &
#     local tbl_pid=$!
# 
#     (
#         ./scripts/shell/modules/count_words.sh >"$wrd_log" 2>&1
#         echo $? >"$temp_dir/wrd_exit"
#     ) &
#     local wrd_pid=$!
# 
#     # Wait for all parallel jobs
#     wait $fig_pid $tbl_pid $wrd_pid
# 
#     # Display outputs in order
#     echo_info "  Figure Processing:"
#     cat "$fig_log" | sed 's/^/    /'
# 
#     echo_info "  Table Processing:"
#     cat "$tbl_log" | sed 's/^/    /'
# 
#     echo_info "  Word Count:"
#     cat "$wrd_log" | sed 's/^/    /'
# 
#     # Check exit codes
#     local fig_exit=$(cat "$temp_dir/fig_exit")
#     local tbl_exit=$(cat "$temp_dir/tbl_exit")
#     local wrd_exit=$(cat "$temp_dir/wrd_exit")
# 
#     rm -rf "$temp_dir"
# 
#     # Fail if any job failed
#     if [ "$fig_exit" -ne 0 ] || [ "$tbl_exit" -ne 0 ] || [ "$wrd_exit" -ne 0 ]; then
#         echo_error "Parallel processing failed (fig=$fig_exit, tbl=$tbl_exit, wrd=$wrd_exit)"
#         exit 1
#     fi
# 
#     local parallel_end=$(date +%s)
#     local parallel_elapsed=$((parallel_end - parallel_start))
#     local total_elapsed=$((parallel_end - COMPILATION_START_TIME))
#     timestamp=$(date '+%H:%M:%S')
#     echo_success "[$timestamp] Completed: Parallel Processing (${parallel_elapsed}s elapsed, ${total_elapsed}s total)"
# 
#     # Compile documents
#     log_stage_start "TeX Compilation (Structure)"
#     ./scripts/shell/modules/compilation_structure_tex_to_compiled_tex.sh
#     log_stage_end "TeX Compilation (Structure)"
# 
#     # TeX to PDF
#     log_stage_start "PDF Generation"
#     ./scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh
#     log_stage_end "PDF Generation"
# 
#     # Diff (skip if --no_diff specified)
#     if [ "$no_diff" = false ]; then
#         log_stage_start "Diff Generation"
#         ./scripts/shell/modules/process_diff.sh
#         log_stage_end "Diff Generation"
#     else
#         echo_info "Skipping diff generation (--no_diff specified)"
#     fi
# 
#     # Versioning
#     log_stage_start "Archive/Versioning"
#     ./scripts/shell/modules/process_archive.sh
#     log_stage_end "Archive/Versioning"
# 
#     # Cleanup
#     log_stage_start "Cleanup"
#     ./scripts/shell/modules/cleanup.sh
#     log_stage_end "Cleanup"
# 
#     # Final steps
#     log_stage_start "Directory Tree"
#     ./scripts/shell/modules/custom_tree.sh
#     log_stage_end "Directory Tree"
# 
#     # Logging
#     echo
# 
#     local final_time=$(date +%s)
#     local total_compilation_time=$((final_time - COMPILATION_START_TIME))
#     echo_success "===================================================="
#     echo_success "TOTAL COMPILATION TIME: ${total_compilation_time}s"
#     echo_success "===================================================="
#     echo_success "See $SCITEX_WRITER_GLOBAL_LOG_FILE"
# }
# 
# main "$@" 2>&1 | tee -a "$LOG_PATH" "$SCITEX_WRITER_GLOBAL_LOG_FILE"
# 
# # EOF

# --------------------------------------------------------------------------------
# End of Source Code from: /home/ywatanabe/proj/scitex-writer/scripts/shell/compile_supplementary.sh
# --------------------------------------------------------------------------------
