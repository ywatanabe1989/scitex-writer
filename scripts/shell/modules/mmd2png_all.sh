#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 10:53:33 (ywatanabe)"
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
source ./config/load_config.sh $STXW_MANUSCRIPT_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo "Running $0..."

mmd2png(){
    n_mmd_files="$(ls $STXW_FIGURE_CAPTION_MEDIA_DIR/Figure_ID_*.mmd 2>/dev/null | wc -l)"
    if [[ $n_mmd_files -gt 0 ]]; then
        for mmd_file in "$STXW_FIGURE_CAPTION_MEDIA_DIR"/Figure_ID_*.mmd; do
            png_file="${mmd_file%.mmd}.png"
            mmdc -i "$mmd_file" -o "$png_file"
            echo "Processed: $(basename "$mmd_file")"
        done 2>&1 | tee -a "$LOG_PATH"
    else
        echo "No .mmd files found in $STXW_FIGURE_CAPTION_MEDIA_DIR" | tee -a "$LOG_PATH"
    fi
}

mmd2png

# EOF