#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: 2026-02-10
# File: scripts/shell/export_arxiv.sh
# Purpose: Package manuscript as arXiv-ready tarball
# Usage: export_arxiv.sh [--output-dir DIR]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
GRAY='\033[0;90m'
NC='\033[0m'

OUTPUT_DIR="${PROJECT_ROOT}/01_manuscript/export"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
    -h | --help)
        echo "Usage: $(basename "$0") [--output-dir DIR]"
        echo ""
        echo "Package the compiled manuscript as an arXiv-ready tarball."
        echo ""
        echo "Prerequisites:"
        echo "  Run 'make manuscript-compile' first to generate the flattened"
        echo "  manuscript.tex and .bbl file."
        echo ""
        echo "Options:"
        echo "  --output-dir DIR    Export directory (default: 01_manuscript/export/)"
        echo "  -h, --help          Show this help"
        echo ""
        echo "Output:"
        echo "  <output-dir>/manuscript.tar.gz    arXiv-ready tarball"
        echo ""
        echo "The tarball contains:"
        echo "  manuscript.tex     Flattened source with rewritten paths"
        echo "  manuscript.bbl     Pre-compiled bibliography"
        echo "  bibliography.bib   Source bibliography (fallback)"
        echo "  figures/           Figure JPGs"
        echo "  wordcounts/        Word count files"
        echo ""
        echo "Environment:"
        echo "  SCITEX_WRITER_EXPORT_DIR    Override default output directory"
        exit 0
        ;;
    --output-dir)
        OUTPUT_DIR="$2"
        shift 2
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}" >&2
        echo "Use --help for usage." >&2
        exit 1
        ;;
    esac
done

# Allow env var override
OUTPUT_DIR="${SCITEX_WRITER_EXPORT_DIR:-$OUTPUT_DIR}"

# ============================================================================
# Validation
# ============================================================================

echo -e "${YELLOW}=== SciTeX Writer: arXiv Export ===${NC}"
echo ""

MANUSCRIPT_TEX="${PROJECT_ROOT}/01_manuscript/manuscript.tex"
MANUSCRIPT_DIR="${PROJECT_ROOT}/01_manuscript"
FIG_DIR="${PROJECT_ROOT}/01_manuscript/contents/figures/caption_and_media/jpg_for_compilation"
WORDCOUNT_DIR="${PROJECT_ROOT}/01_manuscript/contents/wordcounts"
BIB_FILE="${PROJECT_ROOT}/00_shared/bib_files/bibliography.bib"

# Check flattened tex exists
if [ ! -f "$MANUSCRIPT_TEX" ]; then
    echo -e "${RED}Error: $MANUSCRIPT_TEX not found.${NC}" >&2
    echo "Run 'make manuscript-compile' first." >&2
    exit 1
fi

# Find .bbl file (could be in logs/ or manuscript dir)
BBL_FILE=""
for candidate in \
    "${MANUSCRIPT_DIR}/logs/manuscript.bbl" \
    "${MANUSCRIPT_DIR}/manuscript.bbl" \
    "${MANUSCRIPT_DIR}/logs/"*.bbl; do
    if [ -f "$candidate" ]; then
        BBL_FILE="$candidate"
        break
    fi
done

if [ -z "$BBL_FILE" ]; then
    echo -e "${YELLOW}Warning: No .bbl file found. Bibliography may not render on arXiv.${NC}"
    echo "Ensure 'make manuscript-compile' ran bibtex successfully."
fi

# ============================================================================
# Export
# ============================================================================

# Clean and create export directory
rm -rf "$OUTPUT_DIR"
mkdir -p "$OUTPUT_DIR/figures" "$OUTPUT_DIR/wordcounts"

echo -e "${GRAY}  Export directory: $OUTPUT_DIR${NC}"

# 1. Copy and transform manuscript.tex
cp "$MANUSCRIPT_TEX" "$OUTPUT_DIR/manuscript.tex"
TEX="$OUTPUT_DIR/manuscript.tex"

# Rewrite figure paths: ./01_manuscript/contents/figures/caption_and_media/jpg_for_compilation/ -> figures/
sed -i 's|./01_manuscript/contents/figures/caption_and_media/jpg_for_compilation/|figures/|g' "$TEX"

# Rewrite wordcount paths: ./01_manuscript/contents/wordcounts/ -> wordcounts/
sed -i 's|./01_manuscript/contents/wordcounts/|wordcounts/|g' "$TEX"

# Fix bibliography path: 01_manuscript/contents/bibliography -> bibliography
sed -i 's|\\bibliography{01_manuscript/contents/bibliography}|\\bibliography{bibliography}|g' "$TEX"

# Comment out supplementary link (fails without supplementary .aux)
sed -i 's|^\\link\[supple-\]|% [arXiv export] \\link[supple-]|g' "$TEX"

# Remove bashful package (may fail on arXiv - runs shell commands)
if grep -q 'bashful' "$TEX"; then
    sed -i 's|\\usepackage\(\[.*\]\)\{0,1\}{.*bashful.*}|% [arXiv export] bashful removed (shell commands not supported)|g' "$TEX"
    echo -e "${YELLOW}  Note: bashful package removed (not supported on arXiv)${NC}"
fi

echo -e "${GREEN}  [OK] manuscript.tex (paths rewritten)${NC}"

# 2. Copy figure JPGs
fig_count=0
if [ -d "$FIG_DIR" ]; then
    for jpg in "$FIG_DIR"/*.jpg; do
        [ -f "$jpg" ] || continue
        cp "$jpg" "$OUTPUT_DIR/figures/"
        fig_count=$((fig_count + 1))
    done
fi
echo -e "${GREEN}  [OK] figures/ ($fig_count files)${NC}"

# 3. Copy wordcount files
wc_count=0
if [ -d "$WORDCOUNT_DIR" ]; then
    for wc in "$WORDCOUNT_DIR"/*.txt; do
        [ -f "$wc" ] || continue
        cp "$wc" "$OUTPUT_DIR/wordcounts/"
        wc_count=$((wc_count + 1))
    done
fi
echo -e "${GREEN}  [OK] wordcounts/ ($wc_count files)${NC}"

# 4. Copy .bbl file
if [ -n "$BBL_FILE" ]; then
    cp "$BBL_FILE" "$OUTPUT_DIR/manuscript.bbl"
    echo -e "${GREEN}  [OK] manuscript.bbl${NC}"
fi

# 5. Copy bibliography.bib (fallback)
if [ -f "$BIB_FILE" ]; then
    cp "$BIB_FILE" "$OUTPUT_DIR/bibliography.bib"
    echo -e "${GREEN}  [OK] bibliography.bib${NC}"
fi

# ============================================================================
# Create tarball
# ============================================================================

TARBALL="$OUTPUT_DIR/manuscript.tar.gz"

# Build file list for tarball
tar_files=("manuscript.tex")
[ -f "$OUTPUT_DIR/manuscript.bbl" ] && tar_files+=("manuscript.bbl")
[ -f "$OUTPUT_DIR/bibliography.bib" ] && tar_files+=("bibliography.bib")
[ -d "$OUTPUT_DIR/figures" ] && tar_files+=("figures/")
[ -d "$OUTPUT_DIR/wordcounts" ] && tar_files+=("wordcounts/")

# Create tarball from inside export dir so paths are relative
(cd "$OUTPUT_DIR" && tar czf manuscript.tar.gz "${tar_files[@]}")

echo ""
echo -e "${GREEN}=== Export Complete ===${NC}"
echo ""
echo -e "  Tarball: ${GREEN}$TARBALL${NC}"
local_size=$(du -h "$TARBALL" | cut -f1)
echo -e "  Size:    $local_size"
echo ""

# List contents
echo -e "${GRAY}  Contents:${NC}"
tar tzf "$TARBALL" | sort | while read -r f; do
    echo -e "    ${GRAY}$f${NC}"
done

echo ""
echo "Upload this tarball to https://arxiv.org/submit"

###% EOF
