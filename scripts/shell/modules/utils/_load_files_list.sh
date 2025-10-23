#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 12:58:17 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/load_files_list.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


# Function to load file paths from a config file
load_files_list() {
    local config_file_path="$1"
    local tex_files=()

    # Check if the configuration file exists
    if [[ ! -f "$config_file_path" ]]; then
        echo "Configuration file not found: $config_file_path"
        return 1
    fi

    # Read the configuration file line by line
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Trim leading and trailing whitespace
        local trimmed_line=$(echo "$line" | xargs)
        # Skip empty lines and comments
        if [[ -n "$trimmed_line" && ! "$trimmed_line" =~ ^# ]]; then
            # Append the file path to the array
            tex_files+=("$trimmed_line")
        fi
    done < "$config_file_path"

    # Return the array of file paths
    echo "${tex_files[@]}"
}

# EOF