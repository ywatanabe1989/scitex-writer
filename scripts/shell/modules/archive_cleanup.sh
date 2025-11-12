#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-12 (ywatanabe)"
# File: ./scripts/shell/modules/archive_cleanup.sh
# Description: Archive cleanup module - keeps only last N versions

# Load version control configuration
if [ -f "./config/version_control.conf" ]; then
    source ./config/version_control.conf
fi

# Logging functions (if not already defined)
if ! command -v echo_info &> /dev/null; then
    GRAY='\033[0;90m'
    GREEN='\033[0;32m'
    YELLOW='\033[0;33m'
    RED='\033[0;31m'
    NC='\033[0m'
    echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
    echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
    echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
    echo_error() { echo -e "${RED}ERRO: $1${NC}"; }
fi

# Main archive cleanup function
cleanup_old_archives() {
    # Check if cleanup is enabled
    if [[ "$ARCHIVE_CLEANUP_ENABLED" != "true" ]]; then
        return 0
    fi

    echo_info "    Archive cleanup: Starting..."

    local keep_last_n="${ARCHIVE_KEEP_LAST_N:-20}"
    local min_keep="${ARCHIVE_MIN_KEEP:-5}"
    local archive_dir="${SCITEX_WRITER_VERSIONS_DIR}"
    local doc_type="${SCITEX_WRITER_DOC_TYPE:-manuscript}"

    # Validate archive directory exists
    if [ ! -d "$archive_dir" ]; then
        echo_warning "    Archive directory not found: $archive_dir"
        return 0
    fi

    # Count total versions (count PDF files, excluding diff files for accuracy)
    local total_versions=$(find "$archive_dir" -maxdepth 1 \
        -name "${doc_type}_v[0-9][0-9][0-9].pdf" \
        2>/dev/null | wc -l)

    echo_info "    Found $total_versions archived versions"

    # Safety check: don't delete if too few versions
    if [ $total_versions -le $min_keep ]; then
        echo_info "    Only $total_versions versions (minimum: $min_keep), skipping cleanup"
        return 0
    fi

    # Check if cleanup is needed
    if [ $total_versions -le $keep_last_n ]; then
        echo_info "    Only $total_versions versions (keeping: $keep_last_n), no cleanup needed"
        return 0
    fi

    # Calculate how many to delete
    local to_delete=$((total_versions - keep_last_n))
    echo_info "    Cleaning up $to_delete old versions (keeping last $keep_last_n)"

    # Get list of version numbers sorted (oldest first)
    # Extract version numbers from filenames
    local versions_to_delete=$(find "$archive_dir" -maxdepth 1 \
        -name "${doc_type}_v[0-9][0-9][0-9].pdf" \
        -printf '%f\n' 2>/dev/null \
        | sed 's/.*_v\([0-9][0-9][0-9]\)\.pdf/\1/' \
        | sort -n \
        | head -n "$to_delete")

    # Delete old versions
    local deleted_count=0
    local deleted_list=""

    for version_num in $versions_to_delete; do
        local version_base="${archive_dir}/${doc_type}_v${version_num}"

        # Delete all 4 files for this version (PDF, TeX, diff PDF, diff TeX)
        local files_deleted=0

        if [ -f "${version_base}.pdf" ]; then
            rm -f "${version_base}.pdf" && ((files_deleted++))
        fi

        if [ -f "${version_base}.tex" ]; then
            rm -f "${version_base}.tex" && ((files_deleted++))
        fi

        if [ -f "${version_base}_diff.pdf" ]; then
            rm -f "${version_base}_diff.pdf" && ((files_deleted++))
        fi

        if [ -f "${version_base}_diff.tex" ]; then
            rm -f "${version_base}_diff.tex" && ((files_deleted++))
        fi

        if [ $files_deleted -gt 0 ]; then
            ((deleted_count++))
            deleted_list="${deleted_list}v${version_num} "
        fi
    done

    if [ $deleted_count -gt 0 ]; then
        echo_success "    Deleted $deleted_count old versions: $deleted_list"

        # Log cleanup to version counter file
        local cleanup_log="${archive_dir}/.cleanup_history.txt"
        echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $deleted_count versions: $deleted_list" >> "$cleanup_log"

        # Update version counter file with cleanup note
        local counter_file="${SCITEX_WRITER_VERSION_COUNTER_TXT}"
        if [ -f "$counter_file" ]; then
            echo "# Last cleanup: $(date '+%Y-%m-%d %H:%M:%S') - Deleted: $deleted_list" >> "$counter_file"
        fi
    else
        echo_info "    No versions deleted"
    fi

    return 0
}

# Export function for use in other scripts
export -f cleanup_old_archives

# EOF
