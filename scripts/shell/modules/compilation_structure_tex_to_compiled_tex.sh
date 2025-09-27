#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 18:00:21 (ywatanabe)"
# File: ./paper/scripts/shell/modules/compilation_structure_tex_to_compiled_tex.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

NC='\033[0m'

# Configurations
source ./config/load_config.sh $STXW_DOC_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0 ..."

gather_tex_contents() {
    # First, create initial compiled.tex from base.tex
    cp "$STXW_BASE_TEX" "$STXW_COMPILED_TEX"

    process_input() {
        local file_path="$1"
        local temp_file=$(mktemp)

        while IFS= read -r line; do
            if [[ "$line" =~ \\input\{(.+)\} ]]; then
                local input_path="${BASH_REMATCH[1]}"
                # Add .tex extension if not present
                [[ "$input_path" != *.tex ]] && input_path="${input_path}.tex"

                if [[ -f "$input_path" ]]; then
                    echo_info "    Processing $input_path"
                    echo -e "\n%% ========================================" >> "$temp_file"
                    echo -e "%% $input_path" >> "$temp_file"
                    echo -e "%% ========================================" >> "$temp_file"
                    cat "$input_path" >> "$temp_file"
                    # echo "    \n" >> "$temp_file"
                    echo -e "\n" >> "$temp_file"
                else
                    echo_warn "$input_path not found."
                    echo "$line" >> "$temp_file"
                fi
            else
                echo "$line" >> "$temp_file"
            fi
        done < "$file_path"

        mv "$temp_file" "$STXW_COMPILED_TEX"
    }

    # Process until no more \input commands remain
    while grep -q '\\input{' "$STXW_COMPILED_TEX"; do
        process_input "$STXW_COMPILED_TEX"
    done

    echo_success "    $STXW_COMPILED_TEX compiled"
}

gather_tex_contents

# EOF