#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 12:33:46 (ywatanabe)"
# File: ./manuscript/scripts/sh/modules/compile_tex.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


YELLOW="\033[1;33m"
NC="\033[0m"
echo -e "$0 ..."
source ./scripts/sh/modules/config.sh

compile_tex() {
    structure_tex="./structure.tex"
    compiled_tex="./compiled.tex"

    # First, create initial compiled.tex from structure.tex
    cp "$structure_tex" "$compiled_tex"

    process_input() {
        local file_path="$1"
        local temp_file=$(mktemp)

        while IFS= read -r line; do
            if [[ "$line" =~ \\input\{(.+)\} ]]; then
                local input_path="${BASH_REMATCH[1]}"
                # Add .tex extension if not present
                [[ "$input_path" != *.tex ]] && input_path="${input_path}.tex"

                if [[ -f "$input_path" ]]; then
                    echo "Processing $input_path"
                    cat "$input_path" >> "$temp_file"
                else
                    echo "Warning: File $input_path not found."
                    echo "$line" >> "$temp_file"
                fi
            else
                echo "$line" >> "$temp_file"
            fi
        done < "$file_path"

        mv "$temp_file" "$compiled_tex"
    }

    # Process until no more \input commands remain
    while grep -q '\\input{' "$compiled_tex"; do
        process_input "$compiled_tex"
    done

    echo -e "${YELLOW}Compiled: $compiled_tex${NC}"
}

compile_tex

# #!/bin/bash
# # -*- coding: utf-8 -*-
# # Timestamp: "2025-05-06 12:32:05 (ywatanabe)"
# # File: ./manuscript/scripts/sh/modules/compile_tex.sh

# THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
# LOG_PATH="$THIS_DIR/.$(basename $0).log"
# touch "$LOG_PATH" >/dev/null 2>&1


# YELLOW="\033[1;33m"
# NC="\033[0m"

# echo -e "$0 ..."

# source ./scripts/sh/modules/config.sh

# compile_tex() {
#     structure_tex="./structure.tex"
#     compiled_tex="./compiled.tex"

#     process_input() {
#         local file_path="$1"
#         local temp_file=$(mktemp)

#         while IFS= read -r line; do
#             if [[ "$line" =~ \\input\{(.+)\} ]]; then
#                 local input_path="${BASH_REMATCH[1]}.tex"
#                 if [[ -f "$input_path" ]]; then
#                     echo "Processing $input_path"
#                     cat "$input_path" >> "$temp_file"
#                 else
#                     echo "Warning: File $input_path not found."
#                     echo "$line" >> "$temp_file"
#                 fi
#             else
#                 echo "$line" >> "$temp_file"
#             fi
#         done < "$file_path"

#         mv "$temp_file" "$compiled_tex"
#     }

#     # Call process_input on the output file and repeat until no \input commands are left
#     while grep -q '\\input{' "$structure_tex"; do
#         process_input "$compiled_tex"
#     done

#     echo -e "${YELLOW}Compiled: $compiled_tex${NC}"
# }

# compile_tex

# # EOF

# EOF