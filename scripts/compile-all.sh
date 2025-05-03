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
    echo "Usage: $0 [-m] [-s] [-r] [-h] [-- additional_args]"
    echo "Options:"
    echo "  -m  Compile manuscript"
    echo "  -s  Compile supplementary"
    echo "  -r  Compile revision"
    echo "  -h  Display this help message"
    echo "  --  Pass additional arguments to compile scripts"
    echo
    echo "Example:"
    echo "  $0 -m -s -- arg1 arg2  # Compile supplementary first and manuscript afterward with additional args"
    echo "  $0 -- arg1 arg2        # Compile all sections with additional args"
    exit 1
}

main() {
    local compile_m=false
    local compile_s=false
    local compile_r=false
    local additional_args=()

    while [[ $# -gt 0 ]]; do
        case $1 in
            -h)
                usage
                ;;
            -m)
                compile_m=true
                shift
                ;;
            -s)
                compile_s=true
                shift
                ;;
            -r)
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

# main() {
#     local compile_flags=""
#     local additional_args=()

#     while [[ $# -gt 0 ]]; do
#         case $1 in
#             -h)
#                 usage
#                 ;;
#             -m|-s|-r) 
#                 compile_flags+="${1#-}"
#                 shift
#                 ;;
#             --)
#                 shift
#                 additional_args=("$@")
#                 break
#                 ;;
#             *)
#                 echo "Invalid option: $1" >&2
#                 usage
#                 ;;
#         esac
#     done

#     if [ -z "$compile_flags" ]; then
#         compile_flags="msr"
#     fi

#     [[ $compile_flags == *"s"* ]] && compile_supplementary.sh "${additional_args[@]}" && \
#     [[ $compile_flags == *"m"* ]] && compile_manuscript.sh "${additional_args[@]}" && \
#     [[ $compile_flags == *"r"* ]] && compile_revision.sh "${additional_args[@]}"

#     wait
# }

main "$@" 2>&1 | tee "$LOG_FILE"

# EOF
