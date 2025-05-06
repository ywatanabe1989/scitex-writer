#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-07 04:57:31 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/png2tif_all.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config.src

png2tif_all(){
    find "$FIGURE_CAPTION_MEDIA_DIR" -maxdepth 1 \
         -name 'Figure_ID_*.png' | \
    parallel --joblog progress.log \
        'in={}; out={.}.tif
         convert -density 300 -units PixelsPerInch "$in" "$out"
         echo "TIFF {#}/'"$(wc -l <<< "$(find '"$FIGURE_CAPTION_MEDIA_DIR"' -maxdepth 1 -name 'Figure_ID_*.png')")"' -> $out"'
}

png2tif_all 2>&1 | tee -a "$LOG_PATH"

# EOF