#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-27 15:20:00 (ywatanabe)"
# File: ./paper/scripts/shell/compile_supplementary.sh

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
export STXW_DOC_TYPE="supplementary"
source ./config/load_config.sh "$STXW_DOC_TYPE"
echo

# Log
touch $LOG_PATH >/dev/null 2>&1
mkdir -p "$LOG_DIR" && touch "$STXW_GLOBAL_LOG_FILE"

# Shell options
set -e
set -o pipefail

# Default values for arguments
do_p2t=false
no_figs=false  # Supplementary typically includes figures
do_quiet=false
do_crop_tif=false

usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -f,   --figs          Includes figures (default: $(if $no_figs; then echo "false"; else echo "true"; fi))"
    echo "  -p2t, --ppt2tif       Converts Power Point to TIF on WSL (default: $do_p2t)"
    echo "  -c,   --crop_tif      Crop TIF images to remove excess whitespace (default: $do_crop_tif)"
    echo "  -q,   --quiet         Do not shows detailed logs for latex compilation (default: $do_quiet)"
    echo "  -h,   --help          Display this help message"
    exit 0
}

parse_arguments() {
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            -h|--help) usage ;;
            -p2t|--ppt2tif) do_p2t=true; no_figs=false ;;
            -f|--figs) no_figs=false ;;
            -c|--crop_tif) do_crop_tif=true; no_figs=false ;;
            -q|--quiet) do_quiet=true ;;
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
    ! $no_figs && options_display="${options_display} --figs"
    $do_crop_tif && options_display="${options_display} --crop_tif"
    $do_quiet && options_display="${options_display} --quiet"
    echo_info "Running $0${options_display}..."

    # Verbosity
    if [ "$do_quiet" == "true" ]; then
        export STXW_VERBOSE_PDFLATEX="false"
        export STXW_VERBOSE_BIBTEX="false"
    else
        export STXW_VERBOSE_PDFLATEX=${true:-"$STXW_VERBOSE_PDFLATEX"}
        export STXW_VERBOSE_BIBTEX=${true:-"$STXW_VERBOSE_BIBTEX"}
    fi

    # Check dependencies
    ./scripts/shell/modules/check_dependancy_commands.sh

    # Process figures, tables, and count
    ./scripts/shell/modules/process_figures.sh \
        "$no_figs" \
        "$do_p2t" \
        "$do_quiet" \
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