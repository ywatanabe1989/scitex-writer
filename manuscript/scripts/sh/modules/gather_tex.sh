#!/bin/bash

echo -e "$0 ...\n"

source ./scripts/sh/modules/config.sh

gather_tex() {
    main_file="./main/main.tex"
    output_file="./main/manuscript.tex"
    cp "$main_file" "$output_file" -f

    echo

    process_input() {
        local file_path="$1"
        local temp_file=$(mktemp)

        while IFS= read -r line; do
            if [[ "$line" =~ \\input\{(.+)\} ]]; then
                local input_path="${BASH_REMATCH[1]}.tex"
                if [[ -f "$input_path" ]]; then
                    # echo "Processing $input_path"
                    cat "$input_path" >> "$temp_file"
                else
                    echo "Warning: File $input_path not found."
                    echo "$line" >> "$temp_file"
                fi
            else
                echo "$line" >> "$temp_file"
            fi
        done < "$file_path"

        mv "$temp_file" "$output_file"
    }

    # Call process_input on the output file and repeat until no \input commands are left
    while grep -q '\\input{' "$output_file"; do
        process_input "$output_file"
    done

    echo -e "\n\033[1;33mCompiled: $output_file\033[0m"
}

gather_tex

## EOF
