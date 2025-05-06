#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 23:09:28 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/compilation_structure_tex_to_compiled_tex.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config.src
echo_info "$0 ..."

gather_tex_contents() {
    # First, create initial compiled.tex from structure.tex
    cp "$BASE_TEX" "$COMPILED_TEX"

    process_input() {
        local file_path="$1"
        local temp_file=$(mktemp)

        while IFS= read -r line; do
            if [[ "$line" =~ \\input\{(.+)\} ]]; then
                local input_path="${BASH_REMATCH[1]}"
                # Add .tex extension if not present
                [[ "$input_path" != *.tex ]] && input_path="${input_path}.tex"

                if [[ -f "$input_path" ]]; then
                    echo_info "Processing $input_path"
                    cat "$input_path" >> "$temp_file"
                    echo "\n" >> "$temp_file"
                else
                    echo_warn "$input_path not found."
                    echo "$line" >> "$temp_file"
                fi
            else
                echo "$line" >> "$temp_file"
            fi
        done < "$file_path"

        mv "$temp_file" "$COMPILED_TEX"
    }

    # Process until no more \input commands remain
    while grep -q '\\input{' "$COMPILED_TEX"; do
        process_input "$COMPILED_TEX"
    done

    echo_success "$COMPILED_TEX compiled"
}

gather_tex_contents

# EOF