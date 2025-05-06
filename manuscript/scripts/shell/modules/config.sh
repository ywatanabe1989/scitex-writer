#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 12:50:54 (ywatanabe)"
# File: ./manuscript/scripts/sh/modules/config.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


# Figure
FIGURE_SRC_DIR="./src/figures/src"
FIGURE_JPG_DIR="$FIGURE_SRC_DIR"/jpg
FIGURE_COMPILED_DIR="./src/figures/compiled"
FIGURE_HIDDEN_DIR="./src/figures/.tex"

# Table
TABLE_SRC_DIR="./src/tables/src"
TABLE_COMPILED_DIR="./src/tables/compiled"
TABLE_HIDDEN_DIR="./src/tables/.tex"

# Word Count
WORDCOUNT_DIR="./src/wordcounts"

# EOF