#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-07 04:57:38 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/mmd2png_all.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config.src

mmd2png(){
    total=$(ls "$FIGURE_CAPTION_MEDIA_DIR"/Figure_ID_*.mmd | wc -l)
    ls "$FIGURE_CAPTION_MEDIA_DIR"/Figure_ID_*.mmd | \
    parallel --joblog progress.log \
      'in={}; out={.}.png
       mmdc -i "$in" -o "$out" --backgroundColor white -s 3
       echo "Processed: {#}/'"$total"'"' \
      2>&1 | tee -a "$LOG_PATH"
}

mmd2png

# EOF