#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 02:20:59 (ywatanabe)"
# File: ./paper/manuscript/main.sh

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
source ./config.src

# Working directory
cd $THIS_DIR

# Log
touch $LOG_PATH >/dev/null 2>&1
mkdir -p "$LOG_DIR" && touch "$STXW_GLOBAL_LOG_FILE"

# Shell options
set -e
set -o pipefail

# Deafult values for arguments
do_p2t=false
no_figs=true
do_verbose=false
do_crop_tif=false

usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -f,   --figs          Includes figures (default: $(if $no_figs; then echo "false"; else echo "true"; fi))"
    echo "  -p2t, --ppt2tif       Converts Power Point to TIF on WSL (default: $do_p2t)"
    echo "  -c,   --crop_tif      Crop TIF images to remove excess whitespace (default: $do_crop_tif)"
    echo "  -v,   --verbose       Shows detailed logs for latex compilation (default: $do_verbose)"
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
            -v|--verbose) do_verbose=true ;;
            *) echo "Unknown option: $1"; usage ;;
        esac
        shift
    done
}

main() {
    parse_arguments "$@"

    # Log command options
    $do_p2t && echo -n " --ppt2tif"
    ! $no_figs && echo -n " --figs"
    $do_crop_tif && echo -n " --crop_tif"
    $do_verbose && echo -n " --verbose"

    if [ $do_verbose == true ]; then
        export STXW_VERBOSE_PDFLATEX=$do_verbose
        export STXW_VERBOSE_BIBTEX=$do_verbose
    fi

    # Check dependencies
    ./scripts/shell/modules/check_dependancy_commands.sh

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
    ./scripts/shell/modules/process_diff.sh "$do_verbose"

    # Versioning
    ./scripts/shell/modules/process_versions.sh

    # Cleanup
    ./scripts/shell/modules/cleanup.sh

    # Final steps
    ./scripts/shell/modules/custom_tree.sh

    # Logging
    echo_success "See $STXW_GLOBAL_LOG_FILE"
}

main "$@" 2>&1 | tee "$STXW_GLOBAL_LOG_FILE"

# EOF
