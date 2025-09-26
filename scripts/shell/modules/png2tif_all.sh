#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 10:53:39 (ywatanabe)"
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
source ./config/load_config.sh $MANUSCRIPT_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo "Running $0..."

png2tif_all(){
    find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -maxdepth 1 \
         -name 'Figure_ID_*.png' | \
    parallel --joblog progress.log \
        'in={}; out={.}.tif
         convert -density 300 -units PixelsPerInch "$in" "$out"
         echo "TIFF {#}/'"$(wc -l <<< "$(find "$STXW_FIGURE_CAPTION_MEDIA_DIR" -maxdepth 1 -name 'Figure_ID_*.png')")"' -> $out"'
}

png2tif_all 2>&1 | tee -a "$LOG_PATH"

# EOF