#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 22:19:31 (ywatanabe)"
# File: ./manuscript/scripts/shell/compile.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


set -e
set -o pipefail

source ./scripts/shell/modules/config.src
mkdir -p $LOG_DIR && touch $GLOBAL_LOG_FILE

do_insert_citations=false
do_revise=false
do_push=false
do_term_check=false
do_p2t=false
no_figs=true
do_verbose=false

usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -p,   --push          Enables push action (default: $do_push)"
    echo "  -r,   --revise        Enables revision process with GPT (default: $do_revise)"
    echo "  -t,   --terms         Enables term checking with GPT (default: $do_term_check)"
    echo "  -p2t, --ppt2tif       Converts Power Point to TIF on WSL (default: $do_p2t)"
    echo "  -c,   --citations     Inserts citations with GPT (default: $do_insert_citations)"
    echo "  -f,   --figs          Includes figures (default: $(if $no_figs; then echo "false"; else echo "true"; fi))"
    echo "  -v,   --verbose       Shows detailed logs for latex compilation (default: $do_verbose)"
    echo "  -h,   --help          Display this help message"
    exit 0
}

parse_arguments() {
    while [[ "$#" -gt 0 ]]; do
        case $1 in
            -h|--help) usage ;;
            -p|--push) do_push=true ;;
            -r|--revise) do_revise=true ;;
            -t|--terms) do_term_check=true ;;
            -p2t|--ppt2tif) do_p2t=true; no_figs=false ;;
            -c|--citations) do_insert_citations=true ;;
            -f|--figs) no_figs=false ;;
            -v|--verbose) do_verbose=true ;;
            *) echo "Unknown option: $1"; usage ;;
        esac
        shift
    done
}

main() {
    parse_arguments "$@"

    # Log command options
    $do_push && echo -n " --push"
    $do_revise && echo -n " --revise"
    $do_term_check && echo -n " --terms"
    $do_p2t && echo -n " --ppt2tif"
    $do_insert_citations && echo -n " --citations"
    ! $no_figs && echo -n " --figs"
    $do_verbose && echo -n " --verbose"

    # Check dependencies
    ./scripts/shell/modules/check_dependancy_commands.sh

    # Revise tex files if needed
    if [ "$do_revise" = true ]; then ./scripts/shell/revise.sh; fi

    # Insert citations if needed
    if [ "$do_insert_citations" = true ]; then ./scripts/shell/insert_citations.sh; fi

    # Process figures, tables, and count
    ./scripts/shell/modules/process_figures.sh "$no_figs" "$do_p2t" "$do_verbose"
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

    # Check terms if needed
    if [ "$do_term_check" = true ]; then
        ./scripts/shell/modules/check_terms.sh
    fi

    # Final steps
    ./scripts/shell/modules/custom_tree.sh

    echo_success "See $GLOBAL_LOG_FILE"

    # Git push if needed
    if [ "$do_push" = true ]; then
        ./scripts/shell/modules/git_push.sh
    fi
}

main "$@" 2>&1 | tee "$GLOBAL_LOG_FILE"

# EOF