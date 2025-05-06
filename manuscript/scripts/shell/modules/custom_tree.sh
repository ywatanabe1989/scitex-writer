#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 22:19:58 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/custom_tree.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./scripts/shell/modules/config.src
echo_info "$0..."

mkdir -p "$(dirname $TREE_TXT)"
tree -I "compiled_*|diff_*|*.pyc|*.cpython-38.pyc|*.so|*.pdf|*.tif|*.csv|*.ipynb|env|__pycache__|*.dist-info|*.whl|*.exe|*.tmpl|*.sh|cache|*.txt|*.md|manually_edited|old|*.xml|*.1" config/ > $TREE_TXT
echo_success "$TREE_TXT created"

# EOF