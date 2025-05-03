#!/bin/bash

set -e
set -o pipefail

LOG_FILE="./.logs/compile.log"

echo_splitter() {
    echo -e "\n----------------------------------------\n"
    }

parse_arguments() {
    do_insert_citations=false
    do_revise=false
    do_push=false
    do_term_check=false
    do_p2t=false
    no_figs=true
    do_verbose=false

    while [[ "$#" -gt 0 ]]; do
        case $1 in
            -h|--help) display_usage ;;
            -p|--push) do_push=true ;;
            -r|--revise) do_revise=true ;;
            -t|--terms) do_term_check=true ;;
            -p2t|--ppt2tif) do_p2t=true; no_figs=false ;;            
            -c|--citations) do_insert_citations=true ;;
            -f|--figs) no_figs=false ;;
            -v|--verbose) do_verbose=true ;;                        
        esac
        shift
    done
}

display_usage() {
    echo "Usage: $0 [options]"
    echo "Options:"
    echo "  -p,   --push          Enables push action"
    echo "  -r,   --revise        Enables revision process with GPT"
    echo "  -t,   --terms         Enables term checking with GPT"
    echo "  -p2t, --ppt2tif       Converts Power Point to TIF (on WSL on Windows)"
    echo "  -c,   --citations     Inserts citations with GPT"
    echo "  -f,   --figs          Includes figures"
    echo "  -v,   --verbose       Shows detailes logs for latex compilation"    
    exit 0
}

log_command() {
    echo_splitter
    echo "./compile.sh" \
         $(if $do_push; then echo "--push "; fi) \
         $(if $do_revise; then echo "--revise "; fi) \
         $(if $do_term_check; then echo "--terms "; fi) \
         $(if $do_p2t; then echo "--ppt2tif "; fi) \
         $(if $do_insert_citations; then echo "--citations "; fi) \
         $(if $no_figs; then echo "--no-figs"; fi) \
         $(if $do_verbose; then echo "--verbose"; fi) \         
    echo_splitter
}


clear_main_directory() {
    # Usage: clear_main_directory
    for f in main.pdf diff.pdf manuscript.pdf manuscript.tex diff.tex; do
        rm ./main/$f 2>/dev/null
    done
}

run_checks() {
    echo_splitter
    ./scripts/sh/modules/check.sh
    echo_splitter
}

revise_tex_files() {
    local do_revise="$1"
    if [ "$do_revise" = true ]; then
        echo_splitter
        ./scripts/sh/revise.sh
        echo_splitter
    fi
}

insert_citations() {
    if [ "$do_insert_citations" = true ]; then
        echo_splitter
        ./scripts/sh/insert_citations.sh
        echo_splitter
    fi
}

count_words_figures_tables() {
    echo_splitter
    ./scripts/sh/modules/count_words_figures_and_tables.sh
    echo_splitter
}

process_figures() {
    echo_splitter    
    ./scripts/sh/modules/process_figures.sh $no_figs $do_p2t
    echo_splitter    
    }

process_tables() {
    echo_splitter    
    ./scripts/sh/modules/process_tables.sh
    echo_splitter    
    }

generate_compiled_tex() {
    echo_splitter
    ./scripts/sh/modules/gather_tex.sh
    echo_splitter
}

compile_main_tex() {
    echo_splitter
    ./scripts/sh/modules/compile_main_tex.sh || { echo "Error in compile_main_tex"; exit 1; }
    echo_splitter
}

generate_diff_tex() {
    echo_splitter
    ./scripts/sh/modules/gen_diff_tex.sh
    echo_splitter
}

compile_diff_tex() {
    echo_splitter
    ./scripts/sh/modules/compile_diff_tex.sh
    echo_splitter
}

cleanup() {
    echo_splitter
    ./scripts/sh/modules/cleanup.sh
    echo_splitter
}

versioning() {
    echo_splitter
    ./scripts/sh/modules/versioning.sh
    echo_splitter
}

print_success() {
    echo_splitter
    ./scripts/sh/modules/print_success.sh
    echo_splitter
}

check_terms() {
    if [ "$do_term_check" = true ]; then
        echo_splitter
        ./scripts/sh/modules/check_terms.sh
        echo_splitter
    fi
}

custom_tree() {
    echo_splitter
    ./scripts/sh/modules/custom_tree.sh
    echo_splitter
}

git_push() {
    if [ "$do_push" = true ]; then
        echo_splitter
        ./scripts/sh/modules/git_push.sh
        echo_splitter
    fi

}


# main() {
#     set -e
#     parse_arguments "$@" || { echo "Error in parse_arguments"; exit 1; }
#     log_command || { echo "Error in log_command"; exit 1; }
#     run_checks || { echo "Error in run_checks"; exit 1; }
#     revise_tex_files || { echo "Error in revise_tex_files"; exit 1; }
#     insert_citations || { echo "Error in insert_citations"; exit 1; }
#     process_figures "$no_figs" "$do_p2t" || { echo "Error in process_figures"; exit 1; }
#     process_tables || { echo "Error in process_tables"; exit 1; }
#     count_words_figures_tables || { echo "Error in count_words_figures_tables"; exit 1; }
#     compile_main_tex || { echo "Error in compile_main_tex"; exit 1; }    
#     generate_compiled_tex || { echo "Error in generate_compiled_tex"; exit 1; }    
#     generate_diff_tex || { echo "Error in generate_diff_tex"; exit 1; }
#     compile_diff_tex || { echo "Error in compile_diff_tex"; exit 1; }
#     cleanup || { echo "Error in cleanup"; exit 1; }
#     versioning || { echo "Error in versioning"; exit 1; }
#     print_success || { echo "Error in print_success"; exit 1; }
#     check_terms || { echo "Error in check_terms"; exit 1; }
#     custom_tree || { echo "Error in custom_tree"; exit 1; }
#     echo -e "\nLog saved to $LOG_FILE\n" || { echo "Error in echo"; exit 1; }
#     git_push || { echo "Error in git_push"; exit 1; }
# }

# main() {
#     set -e
#     parse_arguments "$@" || { echo "Error in parse_arguments"; exit 1; }
#     log_command || { echo "Error in log_command"; exit 1; }
#     run_checks || { echo "Error in run_checks"; exit 1; }
#     revise_tex_files "$do_revise" || { echo "Error in revise_tex_files"; exit 1; }
#     insert_citations || { echo "Error in insert_citations"; exit 1; }
#     process_figures "$no_figs" "$do_p2t" || { echo "Error in process_figures"; exit 1; }
#     process_tables || { echo "Error in process_tables"; exit 1; }
#     count_words_figures_tables || { echo "Error in count_words_figures_tables"; exit 1; }
#     compile_main_tex "$do_verbose" || { echo "Error in compile_main_tex"; exit 1; }    
#     generate_compiled_tex || { echo "Error in generate_compiled_tex"; exit 1; }    
#     generate_diff_tex || { echo "Error in generate_diff_tex"; exit 1; }
#     compile_diff_tex "$do_verbose" || { echo "Error in compile_diff_tex"; exit 1; }
#     cleanup || { echo "Error in cleanup"; exit 1; }
#     versioning || { echo "Error in versioning"; exit 1; }
#     print_success || { echo "Error in print_success"; exit 1; }
#     check_terms || { echo "Error in check_terms"; exit 1; }
#     custom_tree || { echo "Error in custom_tree"; exit 1; }
#     echo -e "\nLog saved to $LOG_FILE\n" || { echo "Error in echo"; exit 1; }
#     git_push || { echo "Error in git_push"; exit 1; }
# }

main() {
    set -e
    parse_arguments "$@"
    log_command
    run_checks
    revise_tex_files "$do_revise"
    insert_citations
    process_figures "$no_figs" "$do_p2t" "$do_verbose"
    process_tables "$do_verbose"
    count_words_figures_tables
    compile_main_tex "$do_verbose"
    generate_compiled_tex
    # chktex -v0 ./main.tex # > ./.logs/syntax_warnings.log 2>&1    
    generate_diff_tex
    compile_diff_tex "$do_verbose"
    cleanup
    versioning
    # print_success
    check_terms
    custom_tree
    echo -e "\nLog saved to $LOG_FILE\n"
    git_push
}

main "$@" 2>&1 | tee "$LOG_FILE"
