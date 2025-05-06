#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 12:50:53 (ywatanabe)"
# File: ./manuscript/scripts/sh/modules/take_diff_tex.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


echo -e "$0 ..."

YELLOW="\033[1;33m"
NC="\033[0m"
RED="\033[1;31m"


function determine_previous() {
    # Determines the base TeX file for diff comparison
    # Usage: previous=$(determine_previous)

    local base_tex=$(ls -v ./old/compiled_v*base.tex 2>/dev/null | tail -n 1)
    local latest_tex=$(ls -v ./old/compiled_v[0-9]*.tex 2>/dev/null | tail -n 1)
    local current_tex="./manuscript.tex"

    if [[ -n "$base_tex" ]]; then echo "$base_tex"
    elif [[ -n "$latest_tex" ]]; then echo "$latest_tex"
    else echo "$current_tex"; fi
}

function cleanup_if_fake_previous() {
    local previous=$1
    [[ "$previous" == /tmp/* ]] && rm -f "$previous"
}

function take_diff_tex() {
    # Generates LaTeX diff between base and current manuscript
    # Usage: take_diff_tex
    local previous=$(determine_previous)
    local current_tex="./compiled.tex"
    local diff_tex="./diff.tex"

    # echo -e "Taking diff between $previous & $current_tex"
    if [ -f "$current_tex" ]; then
        latexdiff "$previous" "$current_tex" > "$diff_tex" 2>/dev/null
        if [ -s "$diff_tex" ]; then
            echo -e "${YELLOW}Created: $diff_tex${NC}"
        else
            echo -e "${YELLOW}$diff_tex is empty.${NC}"
        fi
    else
        echo -e "${RED}Error: $current_tex not found.${NC}"
    fi

    # cleanup_if_fake_previous "$previous"
}

take_diff_tex

## EOF

# EOF