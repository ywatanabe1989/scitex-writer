#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-09 (ywatanabe)"
# File: ./scripts/installation/init_project.sh
# Description: Initialize project with required preprocessing artifacts
#              Addresses GitHub Issue #12

set -e

# Resolve project root from script location (handles any working directory)
THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$THIS_DIR/.." && pwd)"

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

log_success() { echo -e "${GREEN}✓${NC} $1"; }
log_info() { echo -e "  → $1"; }

echo "Initializing SciTeX Writer project..."
echo ""

# Create wordcount directories and placeholder files
create_wordcount_placeholders() {
    local doc_dir="$1"
    local wordcount_dir="$PROJECT_ROOT/$doc_dir/contents/wordcounts"

    if [ ! -d "$wordcount_dir" ]; then
        mkdir -p "$wordcount_dir"
        log_info "Created $doc_dir/contents/wordcounts/"
    fi

    # Create placeholder files with zero values
    local files=(
        "abstract_count.txt"
        "introduction_count.txt"
        "methods_count.txt"
        "results_count.txt"
        "discussion_count.txt"
        "figure_count.txt"
        "table_count.txt"
        "imrd_count.txt"
    )

    for file in "${files[@]}"; do
        if [ ! -f "$wordcount_dir/$file" ]; then
            echo "0" >"$wordcount_dir/$file"
        fi
    done
}

# Create merged bibliography placeholder
create_bibliography_placeholder() {
    local bib_dir="$PROJECT_ROOT/00_shared/bib_files"
    local merged_bib="$PROJECT_ROOT/00_shared/bibliography.bib"

    if [ ! -d "$bib_dir" ]; then
        mkdir -p "$bib_dir"
        log_info "Created 00_shared/bib_files/"
    fi

    # Create empty bibliography if none exists
    if [ ! -f "$bib_dir/references.bib" ] && [ ! -f "$merged_bib" ]; then
        echo "% Bibliography file - add your references here" >"$bib_dir/references.bib"
        log_info "Created placeholder references.bib"
    fi
}

# Create figure/table compiled directories
create_compiled_dirs() {
    local doc_dir="$1"

    # Figures
    local fig_compiled="$PROJECT_ROOT/$doc_dir/contents/figures/compiled"
    if [ ! -d "$fig_compiled" ]; then
        mkdir -p "$fig_compiled"
    fi

    local fig_jpg="$PROJECT_ROOT/$doc_dir/contents/figures/caption_and_media/jpg_for_compilation"
    if [ ! -d "$fig_jpg" ]; then
        mkdir -p "$fig_jpg"
    fi

    # Tables
    local tbl_compiled="$PROJECT_ROOT/$doc_dir/contents/tables/compiled"
    if [ ! -d "$tbl_compiled" ]; then
        mkdir -p "$tbl_compiled"
    fi
}

# Create log directories
create_log_dirs() {
    local log_dir="$PROJECT_ROOT/logs"
    mkdir -p "$log_dir"

    for doc in 01_manuscript 02_supplementary 03_revision; do
        mkdir -p "$PROJECT_ROOT/$doc/logs"
    done
}

# Create container cache directory
create_container_dirs() {
    mkdir -p "$PROJECT_ROOT/.cache/containers"
    mkdir -p "$PROJECT_ROOT/scripts/containers"

    # Create README for containers directory
    if [ ! -f "$PROJECT_ROOT/scripts/containers/README.md" ]; then
        cat >"$PROJECT_ROOT/scripts/containers/README.md" <<'EOF'
# Container Definitions

This directory contains Apptainer/Singularity container definition files.

## Files

- `texlive.def` - TeX Live container for LaTeX compilation
- `mermaid.def` - Mermaid CLI container for diagram generation

## Usage

Build containers:
```bash
./scripts/installation/download_containers.sh
```

Containers are cached in `.cache/containers/` after first build/download.
EOF
    fi
}

# Main
echo "Creating preprocessing artifacts..."

# Process each document type
for doc in 01_manuscript 02_supplementary; do
    create_wordcount_placeholders "$doc"
    create_compiled_dirs "$doc"
done

log_success "Wordcount placeholders created"

create_bibliography_placeholder
log_success "Bibliography structure ready"

create_log_dirs
log_success "Log directories created"

create_container_dirs
log_success "Container directories created"

echo ""
echo -e "${GREEN}Project initialization complete!${NC}"
echo ""
echo "Next steps:"
echo "  1. Add your references to 00_shared/bib_files/references.bib"
echo "  2. Add your content to 01_manuscript/contents/"
echo "  3. Run: ./compile.sh manuscript"
echo ""

# EOF
