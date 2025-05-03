#!/bin/bash

echo -e "$0 ...\n"

function determine_previous() {
    # Determines the base TeX file for diff comparison
    # Usage: previous=$(determine_previous)
    local base_tex=$(ls -v ./old/compiled_v*base.tex 2>/dev/null | tail -n 1)
    local latest_tex=$(ls -v ./old/compiled_v[0-9]*.tex 2>/dev/null | tail -n 1)
    local current_tex="./main/manuscript.tex"

    if [[ -n "$base_tex" ]]; then
        echo "$base_tex"
    elif [[ -n "$latest_tex" ]]; then
        echo "$latest_tex"
    else
        echo "$current_tex"
    fi
}

function cleanup_if_fake_previous() {
    # Removes temporary file if it was used as diff base
    # Usage: cleanup_if_fake_previous "$previous"
    local previous=$1
    [[ "$previous" == /tmp/* ]] && rm -f "$previous"
}

function gen_diff_tex() {
    # Generates LaTeX diff between base and current manuscript
    # Usage: gen_diff_tex
    local previous=$(determine_previous)
    local current_tex="./main/manuscript.tex"    
    local diff_tex="./main/diff.tex"

    echo -e "\nTaking diff between $previous & $current_tex"    
    if [ -f "$current_tex" ]; then
        latexdiff "$previous" "$current_tex" > "$diff_tex" 2>/dev/null
        if [ -s "$diff_tex" ]; then
            echo -e "\n$diff_tex was created."
        else
            echo -e "\n$diff_tex is empty."
        fi
    else
        echo -e "\nError: $current_tex not found."
    fi

    # cleanup_if_fake_previous "$previous"
}

gen_diff_tex

## EOF

# function determine_previous() {
#     local base_tex=$(ls -v ./old/compiled_v*base.tex 2>/dev/null | tail -n 1)
#     local base_fake_tex=$(mktemp)
#     local latest_tex=$(ls -v ./old/compiled_v[0-9]*.tex 2>/dev/null | tail -n 1)

#     if [[ -n "$base_tex" ]]; then
#         echo "$base_tex"
#     elif [[ -n "$latest_tex" ]]; then
#         echo "$latest_tex"
#     else
#         echo "$base_fake_tex"
#     fi
# }

# function cleanup_if_fake_previous() {
#     local previous=$1
#     [[ "$previous" == /tmp/* ]] && rm -f "$previous"
#     }

# function gen_diff_tex() {
#     local previous=$(determine_previous)
#     local current_tex="./main/manuscript.tex"    
#     local diff_tex="./main/diff.tex"

#     echo -e "\nTaking diff between $base_tex & $current_tex"    
#     if [ -n "$base_tex" ] && [ -f "$current_tex" ]; then
#         echo -e "\nTaking diff between $base_tex & $current_tex"
#         latexdiff "$base_tex" "$current_tex" > $diff_tex 2> /dev/null
#     fi

#     if [ -s $diff_tex ]; then
#         echo -e "\n$diff_tex was created."
#     else
#         echo -e "\n$diff_tex is empty."
#     fi

#     cleanup_if_fake_previous "$previous"
# }

# gen_diff_tex

# ## EOF
