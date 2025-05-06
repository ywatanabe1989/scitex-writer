#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-07 01:25:48 (ywatanabe)"
# File: ./manuscript/scripts/shell/compile.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


set -e
set -o pipefail

source ./config.src
mkdir -p $LOG_DIR && touch $GLOBAL_LOG_FILE

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
        export VERBOSE_PDFLATEX=$do_verbose
        export VERBOSE_BIBTEX=$do_verbose
    fi

    # Check dependencies
    ./scripts/shell/modules/check_dependancy_commands.sh

    # Process figures, tables, and count
    ./scripts/shell/modules/process_figures.sh "$no_figs" "$do_p2t" "$do_verbose" "$do_crop_tif"
    ./scripts/shell/modules/process_tables.sh
    ./scripts/shell/modules/count_words.sh

    # Compile documents
    ./scripts/shell/modules/compilation_structure_tex_to_compiled_tex.sh
    ./scripts/shell/modules/compilation_compiled_tex_to_compiled_pdf.sh

    # Diff
    ./scripts/shell/modules/process_diff.sh "$do_verbose"

    # Versioning
    ./scripts/shell/modules/process_versions.sh

    # Cleanup
    ./scripts/shell/modules/cleanup.sh

    # Final steps
    ./scripts/shell/modules/custom_tree.sh

    echo_success "See $GLOBAL_LOG_FILE"
}

main "$@" 2>&1 | tee "$GLOBAL_LOG_FILE"

# EOF