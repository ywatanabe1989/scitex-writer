#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-28 17:55:24 (ywatanabe)"
# File: ./paper/scripts/shell/modules/mmd2png_all.sh

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

# Configurations
source ./config/load_config.sh $STXW_DOC_TYPE

# Source the shared commands module for mmdc
source "$(dirname ${BASH_SOURCE[0]})/command_switching.src"

# Override echo_xxx functions
source ./config/load_config.sh $STXW_DOC_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0..."

mmd2png(){
    # Get mmdc command
    local mmdc_cmd=$(get_cmd_mmdc "$ORIG_DIR")

    if [ -z "$mmdc_cmd" ]; then
        echo_warn "    mmdc not found (native or container)"
        return 1
    fi

    # echo_info "    Using mmdc command: $mmdc_cmd"

    n_mmd_files="$(ls $STXW_FIGURE_CAPTION_MEDIA_DIR/.*.mmd 2>/dev/null | wc -l)"
    if [[ $n_mmd_files -gt 0 ]]; then
        for mmd_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/.*.mmd; do
            png_file="${mmd_file%.mmd}.png"
            jpg_file="$STXW_FIGURE_JPG_DIR/$(basename "${mmd_file%.mmd}.jpg")"

            echo_info "    Converting $(basename "$mmd_file") to PNG..."
            eval "$mmdc_cmd -i \"$mmd_file\" -o \"$png_file\"" > /dev/null 2>&1

            if [ -f "$png_file" ]; then
                echo_success "    Created: $(basename "$png_file")"

                # Convert PNG to JPG using ImageMagick (with container fallback)
                local convert_cmd=$(get_cmd_convert "$ORIG_DIR")
                if [ -n "$convert_cmd" ]; then
                    echo_info "    Converting to JPG..."
                    eval "$convert_cmd \"$png_file\" \"$jpg_file\"" 2>/dev/null
                    if [ -f "$jpg_file" ]; then
                        echo_success "    Created: $(basename "$jpg_file")"
                    fi
                else
                    # Fallback: copy PNG as JPG for LaTeX compatibility
                    echo_warn "    ImageMagick not available, copying PNG as JPG"
                    cp "$png_file" "$jpg_file" 2>/dev/null
                    if [ -f "$jpg_file" ]; then
                        echo_success "    Created: $(basename "$jpg_file") (PNG format)"
                    fi
                fi
            fi
        done 2>&1 | tee -a "$LOG_PATH"
    else
        echo_info "    No .mmd files found in $STXW_FIGURE_CAPTION_MEDIA_DIR" | tee -a "$LOG_PATH"
    fi
}

mmd2png

# EOF