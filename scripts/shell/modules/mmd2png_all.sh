#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-28 17:55:24 (ywatanabe)"
# File: ./paper/scripts/shell/modules/mmd2png_all.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
echo_header() { echo_info "=== $1 ==="; }
# ---------------------------------------

# Configurations
source ./config/load_config.sh $SCITEX_WRITER_DOC_TYPE

# Source the 00_shared commands module for mmdc
source "$(dirname ${BASH_SOURCE[0]})/command_switching.src"

# Override echo_xxx functions
source ./config/load_config.sh $SCITEX_WRITER_DOC_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running ${BASH_SOURCE[0]}..."

mmd2png(){
    # Early exit if no .mmd files (saves ~30s container setup time)
    # Check for both hidden (.*.mmd) and numbered ([0-9]*.mmd) files
    local n_hidden=$(ls "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR"/.*.mmd 2>/dev/null | wc -l)
    local n_numbered=$(ls "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR"/[0-9]*.mmd 2>/dev/null | wc -l)
    local n_mmd_files=$((n_hidden + n_numbered))

    if [[ $n_mmd_files -eq 0 ]]; then
        echo_info "    No .mmd files found in $SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR"
        return 0
    fi

    echo_info "    Found $n_mmd_files .mmd files ($n_hidden hidden, $n_numbered numbered)"

    # Get mmdc command only if we have files to process
    local mmdc_cmd=$(get_cmd_mmdc "$ORIG_DIR")

    if [ -z "$mmdc_cmd" ]; then
        echo_warn "    mmdc not found (native or container)"
        return 1
    fi

    # Process .mmd files - handle both hidden and numbered files
    for mmd_file in "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR"/.*.mmd "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR"/[0-9]*.mmd; do
        [ -e "$mmd_file" ] || continue

        png_file="${mmd_file%.mmd}.png"
        jpg_file="$SCITEX_WRITER_FIGURE_JPG_DIR/$(basename "${mmd_file%.mmd}.jpg")"

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
}

mmd2png

# EOF