#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-27 00:15:04 (ywatanabe)"
# File: ./paper/scripts/shell/modules/pptx2tif_all.sh

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

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running ${BASH_SOURCE[0]}..."

# PowerPoint to TIF
total=$(ls "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR"/.*.pptx | wc -l)
ls "$SCITEX_WRITER_FIGURE_CAPTION_MEDIA_DIR"/.*.pptx | \
parallel --no-notice --silent \
    './scripts/shell/modules/pptx2tif_single.sh -i "$(realpath {})" -o "$(realpath {.}.tif)"; \
    echo "Processed: {#}/$total"'

# EOF