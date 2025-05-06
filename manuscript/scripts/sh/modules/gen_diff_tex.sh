#!/bin/bash

echo -e "$0 ...\n"

function determine_previous() {
    # Determines the base TeX file for diff comparison
    # Usage: previous=$(determine_previous)
    local base_tex=$(ls -v ./old/compiled_v*base.tex 2>/dev/null | tail -n 1)
    local latest_tex=$(ls -v ./old/compiled_v[0-9]*.tex 2>/dev/null | tail -n 1)
    local current_tex="./main/manuscript.tex"
    local base_fake_tex=""

    # If no previous version exists, create a basic template
    if [[ -z "$base_tex" ]] && [[ -z "$latest_tex" ]]; then
        base_fake_tex=$(mktemp)
        echo '\documentclass{article}\begin{document}This is the previous version.\end{document}' > "$base_fake_tex"
        echo "$base_fake_tex"
        return
    fi

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
    
    # Ensure current_tex exists
    if [ ! -f "$current_tex" ]; then
        echo -e "\nWarning: $current_tex not found. Creating a placeholder..."
        echo '\documentclass{article}\begin{document}This is the current version.\end{document}' > "$current_tex"
    fi
    
    # Generate diff
    if [ -f "$current_tex" ] && [ -f "$previous" ]; then
        # Create a temporary directory for diff output
        mkdir -p ./main
        
        # Run latexdiff with appropriate protection
        if command -v latexdiff >/dev/null 2>&1; then
            latexdiff --flatten "$previous" "$current_tex" > "$diff_tex" 2>/dev/null
            
            # Check if the diff was created, if not create a simple diff
            if [ ! -s "$diff_tex" ]; then
                echo '\documentclass{article}\begin{document}This is a placeholder diff document.\end{document}' > "$diff_tex"
                echo -e "\nWarning: Fallback diff created."
            else
                echo -e "\n$diff_tex was created."
            fi
        else
            echo '\documentclass{article}\begin{document}Latexdiff not available. This is a placeholder.\end{document}' > "$diff_tex"
            echo -e "\nWarning: latexdiff command not found. Created a placeholder."
        fi
    else
        echo -e "\nError: One of the files for diff comparison is missing."
        echo '\documentclass{article}\begin{document}Error: Files for diff comparison missing.\end{document}' > "$diff_tex"
    fi

    # Cleanup temporary files
    cleanup_if_fake_previous "$previous"
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
