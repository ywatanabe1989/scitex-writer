#!/bin/bash
# ripple-wm/paper/scripts/compile-all.sh
# Author: ywatanabe (ywatanabe@alumni.u-tokyo.ac.jp)
# Date: 2023-10-04-11-01

LOG_FILE="${0%.sh}.log"

compile_supplementary() {
    (cd supplementary && ./compile "$@" && cd ..)
}

compile_manuscript() {
    (cd manuscript && ./compile "$@" && cd ..)
}

compile_revision() {
    (cd revision && ./compile "$@" && cd ..)
}

usage() {
    echo "Usage: $0 [options] [-- additional_args]"
    echo "Options:"
    echo "  -m, --manuscript     Compile manuscript"
    echo "  -s, --supplementary  Compile supplementary"
    echo "  -r, --revision       Compile revision"
    echo "  -h, --help           Display this help message"
    echo "  --                   Pass additional arguments to compile scripts"
    echo
    echo "Example:"
    echo "  $0 --manuscript --supplementary -- arg1 arg2  # Compile supplementary first and manuscript afterward with additional args"
    echo "  $0 -- arg1 arg2                              # Compile all sections with additional args"
    exit 1
}

main() {
    local compile_m=false
    local compile_s=false
    local compile_r=false
    local additional_args=()

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                usage
                ;;
            -m|--manuscript)
                compile_m=true
                shift
                ;;
            -s|--supplementary)
                compile_s=true
                shift
                ;;
            -r|--revision)
                compile_r=true
                shift
                ;;
            --)
                shift
                additional_args=("$@")
                break
                ;;
            *)
                echo "Invalid option: $1" >&2
                usage
                ;;
        esac
    done

    if [ "$compile_m" = false ] && [ "$compile_s" = false ] && [ "$compile_r" = false ]; then
        compile_m=true
        compile_s=true
        compile_r=true
    fi

    $compile_s && compile_supplementary "${additional_args[@]}"
    $compile_m && compile_manuscript "${additional_args[@]}"
    $compile_r && compile_revision "${additional_args[@]}"

    wait
}

main "$@" 2>&1 | tee "$LOG_FILE"
