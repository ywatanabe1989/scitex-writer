#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-09 (ywatanabe)"
# File: ./scripts/strip_example_content.sh
# Description: Strip example content for minimal template setup (GitHub Issue #14)

set -e

# Resolve project root
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$THIS_DIR/../.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# Colors
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo "Stripping example content for minimal template..."
echo ""

# Ask for confirmation
read -p "This will remove all example files. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Remove example manuscript content files
echo -e "${YELLOW}Removing example manuscript content...${NC}"
for doc_dir in 01_manuscript 02_supplementary; do
    for section in introduction methods results discussion; do
        file="$doc_dir/contents/${section}.tex"
        if [ -f "$file" ]; then
            echo "% Placeholder for $section" >"$file"
        fi
    done
done

# Remove example figures (keep only .tex stubs)
echo -e "${YELLOW}Removing example figure files...${NC}"
for doc_dir in 01_manuscript 02_supplementary; do
    fig_dir="$doc_dir/contents/figures/caption_and_media"
    if [ -d "$fig_dir" ]; then
        # Remove generated JPGs and PNGs
        find "$fig_dir" -maxdepth 1 \( -name "*.jpg" -o -name "*.png" -o -name "*.mmd" \) -delete
        # Replace .tex files with minimal stubs
        for tex_file in "$fig_dir"/*.tex; do
            if [ -f "$tex_file" ] && [ "$(basename "$tex_file")" != ".gitkeep.tex" ]; then
                name=$(basename "$tex_file" .tex)
                echo "% Figure: $name" >"$tex_file"
            fi
        done
    fi
done

# Remove example tables (keep only .tex stubs)
echo -e "${YELLOW}Removing example table files...${NC}"
for doc_dir in 01_manuscript 02_supplementary; do
    tbl_dir="$doc_dir/contents/tables/caption_and_media"
    if [ -d "$tbl_dir" ]; then
        # Keep only minimal table definitions, remove CSV examples
        for csv_file in "$tbl_dir"/*.csv; do
            if [ -f "$csv_file" ]; then
                rm -f "$csv_file"
            fi
        done
    fi
done

# Remove archived versions
echo -e "${YELLOW}Removing archived document versions...${NC}"
for doc_dir in 01_manuscript 02_supplementary 03_revision; do
    archive_dir="$doc_dir/archive"
    if [ -d "$archive_dir" ]; then
        find "$archive_dir" -type f ! -name ".gitkeep" -delete
    fi
done

# Clean up generated JPG compilation directory
echo -e "${YELLOW}Clearing figure compilation cache...${NC}"
for doc_dir in 01_manuscript 02_supplementary; do
    jpg_dir="$doc_dir/contents/figures/caption_and_media/jpg_for_compilation"
    if [ -d "$jpg_dir" ]; then
        find "$jpg_dir" -type f ! -name ".gitkeep" -delete
    fi
done

echo ""
echo -e "${GREEN}✓ Example content stripped${NC}"
echo ""
echo "Next steps:"
echo "  1. Edit $(pwd)/01_manuscript/contents/abstract.tex"
echo "  2. Edit $(pwd)/01_manuscript/contents/introduction.tex"
echo "  3. Edit $(pwd)/01_manuscript/contents/methods.tex"
echo "  4. Edit $(pwd)/01_manuscript/contents/results.tex"
echo "  5. Edit $(pwd)/01_manuscript/contents/discussion.tex"
echo "  6. Add your references to $(pwd)/00_shared/bib_files/references.bib"
echo "  7. Add your figures to $(pwd)/01_manuscript/contents/figures/caption_and_media/"
echo "  8. Run: ./compile.sh manuscript"
echo ""

# EOF
