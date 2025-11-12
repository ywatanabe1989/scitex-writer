#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 10:52:59 (ywatanabe)"
# File: ./paper/scripts/shell/modules/custom_tree.sh

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
echo_info "$0..."

# Main
mkdir -p "$(dirname $SCITEX_WRITER_TREE_TXT)"
tree -I "compiled_*|diff_*|*.pyc|*.cpython-38.pyc|*.so|*.pdf|*.tif|*.csv|*.ipynb|env|__pycache__|*.dist-info|*.whl|*.exe|*.tmpl|*.sh|cache|*.txt|*.md|manually_edited|old|*.xml|*.1" config/ > $SCITEX_WRITER_TREE_TXT
echo_success "    $SCITEX_WRITER_TREE_TXT created"

# EOF