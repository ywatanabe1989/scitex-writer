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
    ./scripts/shell/modules/check_dependancy_commands.sh

    # Apply citation style from config
    ./scripts/shell/modules/apply_citation_style.sh

    # Process figures, tables, and count
    ./scripts/shell/modules/process_figures.sh \
        "$no_figs" \
        "$do_p2t" \
        "$do_verbose" \
        "$do_crop_tif"

    # Process tables
    ./scripts/shell/modules/process_tables.sh

    # Count words
    ./scripts/shell/modules/count_words.sh

    # Compile documents
    ./scripts/shell/modules/compilation_structure_tex_to_compiled_tex.sh

    # TeX to PDF
    ./scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh

    # Diff
    ./scripts/shell/modules/process_diff.sh

    # Versioning
    ./scripts/shell/modules/process_archive.sh

    # Cleanup
    ./scripts/shell/modules/cleanup.sh

    # Final steps
    ./scripts/shell/modules/custom_tree.sh

    # Logging
    echo
    echo_success "See $STXW_GLOBAL_LOG_FILE"
}

main "$@" 2>&1 | tee "$STXW_GLOBAL_LOG_FILE"

# EOF