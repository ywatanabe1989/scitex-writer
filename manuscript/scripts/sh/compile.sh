#!/bin/bash
set -e
set -o pipefail

LOG_FILE="./.logs/compile.log"
mkdir -p .logs && touch $LOG_FILE

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
    echo -n "./compile.sh"
    $do_push && echo -n " --push"
    $do_revise && echo -n " --revise"
    $do_term_check && echo -n " --terms"
    $do_p2t && echo -n " --ppt2tif"
    $do_insert_citations && echo -n " --citations"
    ! $no_figs && echo -n " --figs"
    $do_verbose && echo -n " --verbose"
    echo  # Add a newline

    # # Clear main directory
    # for f in compiled.pdf diff.pdf manuscript.pdf manuscript.tex diff.tex; do
    #     rm .//$f 2>/dev/null || true
    # done

    # Check dependencies
    ./scripts/sh/modules/check_dependancy_commands.sh

    # Revise tex files if needed
    if [ "$do_revise" = true ]; then ./scripts/sh/revise.sh; fi

    # Insert citations if needed
    if [ "$do_insert_citations" = true ]; then ./scripts/sh/insert_citations.sh; fi

    # Process figures, tables, and count
    ./scripts/sh/modules/process_figures.sh "$no_figs" "$do_p2t" "$do_verbose"
    ./scripts/sh/modules/process_tables.sh "$do_verbose"
    ./scripts/sh/modules/count_words_figures_and_tables.sh

    # Compile documents
    ./scripts/sh/modules/compile_tex.sh
    ./scripts/sh/modules/compiled_tex_to_compiled_pdf.sh "$do_verbose" || { echo "Error in compile_main_tex"; exit 1; }
    ./scripts/sh/modules/take_diff_tex.sh
    ./scripts/sh/modules/compile_diff_tex.sh "$do_verbose"

    # Post-processing steps
    ./scripts/sh/modules/cleanup.sh
    ./scripts/sh/modules/versioning.sh

    # Check terms if needed
    if [ "$do_term_check" = true ]; then
        ./scripts/sh/modules/check_terms.sh
    fi

    # Final steps
    ./scripts/sh/modules/custom_tree.sh
    echo -e "\nLog saved to $LOG_FILE\n"

    # Git push if needed
    if [ "$do_push" = true ]; then
        ./scripts/sh/modules/git_push.sh
    fi
}

main "$@" 2>&1 | tee "$LOG_FILE"
