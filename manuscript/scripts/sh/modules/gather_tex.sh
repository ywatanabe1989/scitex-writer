#!/bin/bash

echo -e "$0 ...\n"

source ./scripts/sh/modules/config.sh

gather_tex() {
    # Ensure main directory exists
    mkdir -p ./main
    
    main_file="./main.tex"
    output_file="./main/manuscript.tex"
    
    # Check if main_file exists
    if [ ! -f "$main_file" ]; then
        if [ -f "./main/main.tex" ]; then
            main_file="./main/main.tex"
        else
            # Create a basic placeholder file if no main.tex exists
            echo '\documentclass{article}\begin{document}This is a placeholder document for diff generation.\end{document}' > "$output_file"
            # Also create a main.tex in the root directory for compilation
            echo '\documentclass{article}\begin{document}This is a placeholder document.\end{document}' > "$main_file"
            echo "Created placeholder $output_file and $main_file files"
            return
        fi
    fi
    
    # Create old directory for version comparison if it doesn't exist
    if [ ! -d "./old" ]; then
        mkdir -p ./old
    fi
    
    # Create initial version file if none exists
    if [ ! -f "./old/compiled_v1.tex" ] && [ -f "$output_file" ]; then
        cp "$output_file" "./old/compiled_v1.tex"
        echo "Created initial version file for diff comparison"
    fi
    
    # Create a backup of the main file
    mkdir -p ./main/debug
    cp "$main_file" "$output_file" -f
    cp "$main_file" "./main/debug/main_original.tex" -f

    echo

    process_input() {
        local file_path="$1"
        local stage="$2"
        local temp_file=$(mktemp)
        local debug_file="./main/debug/manuscript_stage_${stage}.tex"

        while IFS= read -r line; do
            if [[ "$line" =~ \\input\{(.+)\} ]]; then
                local input_path="${BASH_REMATCH[1]}.tex"
                if [[ -f "$input_path" ]]; then
                    echo "Processing $input_path"
                    # Add a comment to mark the included file for easier debugging
                    echo "% START OF INCLUDED FILE: $input_path" >> "$temp_file"
                    cat "$input_path" >> "$temp_file"
                    echo "% END OF INCLUDED FILE: $input_path" >> "$temp_file"
                else
                    echo "Warning: File $input_path not found."
                    echo "% WARNING: COULD NOT FIND FILE $input_path" >> "$temp_file"
                    echo "$line" >> "$temp_file"
                fi
            else
                echo "$line" >> "$temp_file"
            fi
        done < "$file_path"

        # Save a copy of this stage for debugging
        cp "$temp_file" "$debug_file"
        
        # Update the output file
        mv "$temp_file" "$output_file"
    }

    # Call process_input on the output file and repeat until no \input commands are left
    local stage=1
    while grep -q '\\input{' "$output_file"; do
        process_input "$output_file" "$stage"
        ((stage++))
    done
    
    # Create a final copy for debugging
    cp "$output_file" "./main/debug/manuscript_final.tex"

    echo -e "\n\033[1;33mCompiled: $output_file\033[0m"
}

gather_tex

## EOF
