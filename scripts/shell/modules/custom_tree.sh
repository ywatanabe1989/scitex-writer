#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 23:09:28 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/custom_tree.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config/config_manuscript.src
echo_info "$0..."

mkdir -p "$(dirname $STXW_TREE_TXT)"
tree -I "compiled_*|diff_*|*.pyc|*.cpython-38.pyc|*.so|*.pdf|*.tif|*.csv|*.ipynb|env|__pycache__|*.dist-info|*.whl|*.exe|*.tmpl|*.sh|cache|*.txt|*.md|manually_edited|old|*.xml|*.1" config/ > $STXW_TREE_TXT
echo_success "$STXW_TREE_TXT created"

# EOF