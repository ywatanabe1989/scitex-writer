#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 20:50:09 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/pptx2tif_all.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


echo -e "$0 ..."

source ./scripts/shell/modules/config.src

# PowerPoint to TIF
total=$(ls "$FIGURE_SRC_DIR"/Figure_ID_*.pptx | wc -l)
ls "$FIGURE_SRC_DIR"/Figure_ID_*.pptx | \
parallel --eta --progress --joblog progress.log \
    './scripts/shell/modules/pptx2tif_single.sh -i "$(realpath {})" -o "$(realpath {.}.tif)"; \
    echo "Processed: {#}/$total"'

## EOF

# EOF