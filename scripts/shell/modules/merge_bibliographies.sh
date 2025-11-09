#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-10 00:00:00 (ywatanabe)"
# File: ./scripts/shell/modules/merge_bibliographies.sh

# ============================================================================
# Merge Multiple Bibliography Files
# ============================================================================
# This script checks if multiple .bib files exist in 00_shared/bib_files/
# and merges them into a single bibliography.bib file with deduplication.
#
# Features:
# - Smart deduplication by DOI and title+year
# - Hash-based caching (skips merge if files unchanged)
# - Automatic during compilation
#
# Usage:
#   source ./scripts/shell/modules/merge_bibliographies.sh
# ============================================================================

BIB_DIR="./00_shared/bib_files"
BIB_OUTPUT="bibliography.bib"
MERGE_SCRIPT="./scripts/python/merge_bibliographies.py"

# Count .bib files excluding the output file
bib_file_count=$(find "$BIB_DIR" -maxdepth 1 -name "*.bib" ! -name "$BIB_OUTPUT" -type f 2>/dev/null | wc -l)

if [ "$bib_file_count" -gt 0 ]; then
    # Multiple .bib files exist - merge them
    if [ -f "$MERGE_SCRIPT" ]; then
        python3 "$MERGE_SCRIPT" "$BIB_DIR" -o "$BIB_OUTPUT" -q
    else
        echo_warning "Multiple .bib files found but merge script missing: $MERGE_SCRIPT"
        echo_warning "Skipping bibliography merge"
    fi
elif [ "$bib_file_count" -eq 0 ]; then
    # No separate .bib files, check if main bibliography.bib exists
    if [ ! -f "$BIB_DIR/$BIB_OUTPUT" ]; then
        echo_warning "No bibliography files found in $BIB_DIR"
    fi
fi

# EOF
