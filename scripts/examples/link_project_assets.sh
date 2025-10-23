#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 23:05:00 (ywatanabe)"
# File: ./paper/scripts/examples/link_project_assets.sh
#
# Example: Link research project outputs to manuscript
# Usage: ./link_project_assets.sh ~/proj/neurovista

PROJECT_DIR="${1:-$HOME/proj/neurovista}"
MANUSCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

echo "Linking assets from $PROJECT_DIR to SciTeX Writer..."

# Create target directories
FIGURE_DIR="$MANUSCRIPT_DIR/01_manuscript/contents/figures/caption_and_media"
TABLE_DIR="$MANUSCRIPT_DIR/01_manuscript/contents/tables/caption_and_media"
mkdir -p "$FIGURE_DIR" "$TABLE_DIR"

# Counter for sequential IDs
FIG_COUNTER=1
TAB_COUNTER=1

# Link PAC visualization outputs as figures
if [ -d "$PROJECT_DIR/scripts/pac/visualization" ]; then
    echo "Linking PAC visualizations..."
    for fig in "$PROJECT_DIR"/scripts/pac/visualization/*_out/*.png; do
        if [ -f "$fig" ]; then
            name=$(basename "$fig" .png | sed 's/_out$//' | sed 's/[^a-zA-Z0-9_]/_/g')
            id=$(printf "%02d" $FIG_COUNTER)
            target="$FIGURE_DIR/.${id}_${name}.png"
            
            if [ ! -e "$target" ]; then
                ln -s "$fig" "$target"
                echo "  Linked: .${id}_${name}.png"
                ((FIG_COUNTER++))
            fi
        fi
    done
fi

# Link analysis results as tables
if [ -d "$PROJECT_DIR/data/results" ]; then
    echo "Linking result tables..."
    for csv in "$PROJECT_DIR"/data/results/*.csv; do
        if [ -f "$csv" ]; then
            name=$(basename "$csv" .csv | sed 's/[^a-zA-Z0-9_]/_/g')
            id=$(printf "%02d" $TAB_COUNTER)
            target="$TABLE_DIR/.${id}_${name}.csv"
            
            if [ ! -e "$target" ]; then
                ln -s "$csv" "$target"
                echo "  Linked: .${id}_${name}.csv"
                ((TAB_COUNTER++))
            fi
        fi
    done
fi

# Link Mermaid diagrams
if [ -d "$PROJECT_DIR/docs" ]; then
    echo "Linking diagrams..."
    for mmd in "$PROJECT_DIR"/docs/*.mmd; do
        if [ -f "$mmd" ]; then
            name=$(basename "$mmd" .mmd | sed 's/[^a-zA-Z0-9_]/_/g')
            id=$(printf "%02d" $FIG_COUNTER)
            target="$FIGURE_DIR/.${id}_${name}.mmd"
            
            if [ ! -e "$target" ]; then
                ln -s "$mmd" "$target"
                echo "  Linked: .${id}_${name}.mmd (will auto-convert)"
                ((FIG_COUNTER++))
            fi
        fi
    done
fi

echo
echo "Summary:"
echo "  Figures linked: $((FIG_COUNTER - 1))"
echo "  Tables linked: $((TAB_COUNTER - 1))"
echo
echo "Next steps:"
echo "  1. Add captions for each figure/table"
echo "  2. Reference them in your .tex files"
echo "  3. Run ./compile_manuscript"

# EOF