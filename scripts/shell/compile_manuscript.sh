#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-28 17:50:40 (ywatanabe)"
# File: ./paper/scripts/shell/compile_manuscript.sh

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

# Timestamp tracking functions
STAGE_START_TIME=0
COMPILATION_START_TIME=$(date +%s)

log_stage_start() {
    local stage_name="$1"
    STAGE_START_TIME=$(date +%s)
    local timestamp=$(date '+%H:%M:%S')
    echo_info "[$timestamp] Starting: $stage_name"
}

log_stage_end() {
    local stage_name="$1"
    local end_time=$(date +%s)
    local elapsed=$((end_time - STAGE_START_TIME))
    local total_elapsed=$((end_time - COMPILATION_START_TIME))
    local timestamp=$(date '+%H:%M:%S')
    echo_success "[$timestamp] Completed: $stage_name (${elapsed}s elapsed, ${total_elapsed}s total)"
}
# ---------------------------------------

# Configurations
export STXW_DOC_TYPE="manuscript"
source ./config/load_config.sh "$STXW_DOC_TYPE"
echo

# Log
touch $LOG_PATH >/dev/null 2>&1
mkdir -p "$LOG_DIR" && touch "$STXW_GLOBAL_LOG_FILE"

# Shell options
set -e
set -o pipefail

# Deafult values for arguments
do_p2t=false
no_figs=false
do_verbose=false
do_crop_tif=false
do_force=false

usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -nf,  --no_figs       Exclude figures for quick compilation (default: false)"
    echo "  -p2t, --ppt2tif       Converts Power Point to TIF on WSL (default: $do_p2t)"
    echo "  -c,   --crop_tif      Crop TIF images to remove excess whitespace (default: $do_crop_tif)"
    echo "  -q,   --quiet         Do not shows detailed logs for latex compilation (default: $do_verbose)"
    echo "  --force               Force full recompilation (ignore cache) (default: $do_force)"
    echo "  -h,   --help          Display this help message"
    exit 0
}

parse_arguments() {
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            -h|--help) usage ;;
            -p2t|--ppt2tif) do_p2t=true ;;
            -nf|--no_figs) no_figs=true ;;
            -c|--crop_tif) do_crop_tif=true ;;
            -v|--verbose) do_verbose=true ;;
            -q|--quiet) do_verbose=false ;;
            --force) do_force=true ;;
            *) echo "Unknown option: $1"; usage ;;
        esac
        shift
    done
}

main() {
    parse_arguments "$@"

    # Log command options
    options_display=""
    $do_p2t && options_display="${options_display} --ppt2tif"
    $no_figs && options_display="${options_display} --no_figs"
    $do_crop_tif && options_display="${options_display} --crop_tif"
    $do_verbose && options_display="${options_display} --verbose"
    echo_info "Running $0${options_display}..."

    # Verbosity
    export STXW_VERBOSE_PDFLATEX=$do_verbose
    export STXW_VERBOSE_BIBTEX=$do_verbose
    # if [ "$do_verbose" == "true" ]; then
    #     export STXW_VERBOSE_PDFLATEX="true"
    #     export STXW_VERBOSE_BIBTEX="true"
    # else
    #     export STXW_VERBOSE_PDFLATEX="false"
    #     export STXW_VERBOSE_BIBTEX="false"
    # fi

    # Check dependencies
    log_stage_start "Dependency Check"
    ./scripts/shell/modules/check_dependancy_commands.sh
    log_stage_end "Dependency Check"

    # Apply citation style from config
    log_stage_start "Citation Style"
    ./scripts/shell/modules/apply_citation_style.sh
    log_stage_end "Citation Style"

    # Process figures, tables, and count
    log_stage_start "Figure Processing"
    ./scripts/shell/modules/process_figures.sh \
        "$no_figs" \
        "$do_p2t" \
        "$do_verbose" \
        "$do_crop_tif"
    log_stage_end "Figure Processing"

    # Process tables
    log_stage_start "Table Processing"
    ./scripts/shell/modules/process_tables.sh
    log_stage_end "Table Processing"

    # Count words
    log_stage_start "Word Count"
    ./scripts/shell/modules/count_words.sh
    log_stage_end "Word Count"

    # Compile documents
    log_stage_start "TeX Compilation (Structure)"
    ./scripts/shell/modules/compilation_structure_tex_to_compiled_tex.sh
    log_stage_end "TeX Compilation (Structure)"

    # TeX to PDF
    log_stage_start "PDF Generation"
    ./scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh
    log_stage_end "PDF Generation"

    # Diff
    log_stage_start "Diff Generation"
    ./scripts/shell/modules/process_diff.sh
    log_stage_end "Diff Generation"

    # Versioning
    log_stage_start "Archive/Versioning"
    ./scripts/shell/modules/process_archive.sh
    log_stage_end "Archive/Versioning"

    # Cleanup
    log_stage_start "Cleanup"
    ./scripts/shell/modules/cleanup.sh
    log_stage_end "Cleanup"

    # Final steps
    log_stage_start "Directory Tree"
    ./scripts/shell/modules/custom_tree.sh
    log_stage_end "Directory Tree"

    # Logging
    echo
    local final_time=$(date +%s)
    local total_compilation_time=$((final_time - COMPILATION_START_TIME))
    echo_success "===================================================="
    echo_success "TOTAL COMPILATION TIME: ${total_compilation_time}s"
    echo_success "===================================================="
    echo_success "See $STXW_GLOBAL_LOG_FILE"
}

main "$@" 2>&1 | tee "$STXW_GLOBAL_LOG_FILE"

# EOF