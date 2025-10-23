#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-27 00:29:33 (ywatanabe)"
# File: ./paper/scripts/shell/modules/png2tif_all.sh

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

# Source the shared command module
source "$(dirname ${BASH_SOURCE[0]})/command_switching.src"

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0..."

png2tif_all(){
    # Get convert command from shared module
    local convert_cmd=$(get_cmd_convert "$ORIG_DIR")

    if [ -z "$convert_cmd" ]; then
        echo_error "No ImageMagick installation found (native, module, or container)"
        return 1
    fi

    find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -maxdepth 1 \
         -name '.*.png' | \
    parallel --no-notice --silent \
        'in={}; out={.}.tif
         '"$convert_cmd"' -density 300 -units PixelsPerInch "$in" "$out"
         echo "    TIFF {#}/'"$(wc -l <<< "$(find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -maxdepth 1 -name '.*.png')")"' -> $out"'
}

png2tif_all 2>&1 | tee -a "$LOG_PATH"

# EOF