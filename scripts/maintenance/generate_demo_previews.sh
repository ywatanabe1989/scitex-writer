#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-10 02:14:17 (ywatanabe)"
# File: ./scripts/maintenance/generate_demo_previews.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo >"$LOG_PATH"

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
# Description: Generate preview images for README from compiled PDFs

# Resolve project root from script location (safe for nested repos)
PROJECT_ROOT="$(cd "$THIS_DIR/../.." && pwd)"

echo_header "Generating Demo Previews for README"

# Output directory
DEMO_DIR="${PROJECT_ROOT}/docs"
mkdir -p "$DEMO_DIR"

# Settings
RESOLUTION=300 # DPI
WIDTH=1200     # Max width in pixels

# Function to convert PDF first page to PNG
convert_pdf_to_preview() {
    local pdf_path="$1"
    local output_path="$2"
    local doc_name="$3"

    if [ ! -f "$pdf_path" ]; then
        echo_warning "Skipping $doc_name: PDF not found at $pdf_path"
        return 1
    fi

    echo_info "Converting $doc_name..."

    # Use ghostscript for best quality
    /usr/bin/gs \
        -dSAFER \
        -dBATCH \
        -dNOPAUSE \
        -sDEVICE=png16m \
        -r${RESOLUTION} \
        -dFirstPage=1 \
        -dLastPage=1 \
        -sOutputFile="$output_path" \
        "$pdf_path" \
        >/dev/null 2>&1

    if [ -f "$output_path" ]; then
        local size=$(du -h "$output_path" | cut -f1)
        echo_success "  Created: $(basename $output_path) (${size})"
        return 0
    else
        echo_error "  Failed to create: $(basename $output_path)"
        return 1
    fi
}

# Generate previews
echo

convert_pdf_to_preview \
    "${PROJECT_ROOT}/01_manuscript/manuscript.pdf" \
    "${DEMO_DIR}/demo-manuscript-preview.png" \
    "Manuscript"

convert_pdf_to_preview \
    "${PROJECT_ROOT}/02_supplementary/supplementary.pdf" \
    "${DEMO_DIR}/demo-supplementary-preview.png" \
    "Supplementary"

convert_pdf_to_preview \
    "${PROJECT_ROOT}/03_revision/revision.pdf" \
    "${DEMO_DIR}/demo-revision-preview.png" \
    "Revision"

echo
echo_success "Demo preview generation complete!"
echo_info "Images saved in: $DEMO_DIR"
echo_info "Use in README.md with:"
echo_info "  <img src=\"docs/demo-manuscript-preview.png\" width=\"600\"/>"

# EOF
