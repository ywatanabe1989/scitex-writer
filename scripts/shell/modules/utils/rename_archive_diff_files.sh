#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-26 23:30:00 (ywatanabe)"
# File: ./paper/scripts/shell/modules/utils/rename_archive_diff_files.sh
# Description: One-time script to rename existing diff files from manuscript_diff_vXXX to manuscript_vXXX_diff

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"

GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"

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

# Configuration
source ./config/load_config.sh $SCITEX_WRITER_DOC_TYPE

echo
echo_info "Renaming archive diff files to new naming convention..."
echo_info "From: manuscript_diff_vXXX.ext"
echo_info "To:   manuscript_vXXX_diff.ext"
echo

# Process all diff files in archive
cd "$SCITEX_WRITER_VERSIONS_DIR" || exit 1

# Count files to rename
count=0
for file in manuscript_diff_v[0-9][0-9][0-9].*; do
    if [ -f "$file" ]; then
        ((count++))
    fi
done

if [ $count -eq 0 ]; then
    echo_info "No files to rename."
    exit 0
fi

echo_info "Found $count file(s) to rename."
echo

# Rename files
renamed=0
for file in manuscript_diff_v[0-9][0-9][0-9].*; do
    if [ -f "$file" ]; then
        # Extract version number and extension
        if [[ "$file" =~ manuscript_diff_v([0-9][0-9][0-9])\.(.+)$ ]]; then
            version="${BASH_REMATCH[1]}"
            extension="${BASH_REMATCH[2]}"
            new_name="manuscript_v${version}_diff.${extension}"
            
            if [ -f "$new_name" ]; then
                echo_warning "    Target file already exists: $new_name (skipping)"
            else
                mv "$file" "$new_name"
                echo_success "    Renamed: $file -> $new_name"
                ((renamed++))
            fi
        fi
    fi
done

echo
echo_success "Renamed $renamed file(s) successfully."

# Also rename any current version files in the root directory
cd "$ORIG_DIR" || exit 1
echo
echo_info "Checking for current version files in root directory..."

for file in manuscript_diff_v[0-9][0-9][0-9].*; do
    if [ -f "$file" ]; then
        # Extract version number and extension
        if [[ "$file" =~ manuscript_diff_v([0-9][0-9][0-9])\.(.+)$ ]]; then
            version="${BASH_REMATCH[1]}"
            extension="${BASH_REMATCH[2]}"
            new_name="manuscript_v${version}_diff.${extension}"
            
            if [ -f "$new_name" ]; then
                echo_warning "    Target file already exists: $new_name (skipping)"
            else
                mv "$file" "$new_name"
                echo_success "    Renamed: $file -> $new_name"
            fi
        fi
    fi
done

echo
echo_success "Archive renaming complete!"

# EOF