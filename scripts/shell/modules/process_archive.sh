#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2026-01-19 (ywatanabe)"
# File: ./scripts/shell/modules/process_archive.sh
# Description: Archive compiled documents with git-based naming (timestamp + commit hash)

THIS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_PATH="$THIS_DIR/.$(basename "$0").log"
echo >"$LOG_PATH"

GRAY='\033[0;90m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

echo_info() { echo -e "${GRAY}INFO: $1${NC}"; }
log_info() {
    if [ "${SCITEX_LOG_LEVEL:-1}" -ge 2 ]; then
        echo -e "  \033[0;90m→ $1\033[0m"
    fi
}
echo_success() { echo -e "${GREEN}SUCC: $1${NC}"; }
echo_warning() { echo -e "${YELLOW}WARN: $1${NC}"; }
echo_error() { echo -e "${RED}ERRO: $1${NC}"; }

# Load configuration
# shellcheck source=../../../config/load_config.sh
source ./config/load_config.sh "$SCITEX_WRITER_DOC_TYPE"

touch "$LOG_PATH" >/dev/null 2>&1
echo
log_info "Running ${BASH_SOURCE[0]}..."

# Check if working directory is clean (no uncommitted changes)
is_git_clean() {
    if ! git rev-parse --git-dir >/dev/null 2>&1; then
        return 1 # Not a git repo
    fi
    if ! git rev-parse HEAD >/dev/null 2>&1; then
        return 1 # No commits yet
    fi
    # Check for uncommitted changes (staged or unstaged)
    git diff --quiet HEAD -- 2>/dev/null && git diff --cached --quiet HEAD -- 2>/dev/null
}

# Get git-based identifier: YYYYMMDD-HHMMSS_abc1234
get_git_identifier() {
    local timestamp
    timestamp=$(date +%Y%m%d-%H%M%S)
    local hash

    if git rev-parse --git-dir >/dev/null 2>&1; then
        hash=$(git rev-parse --short=7 HEAD 2>/dev/null)
        if [ -z "$hash" ]; then
            hash="nocommit"
        fi
    else
        hash="nogit"
    fi

    echo "${timestamp}_${hash}"
}

# Store a file to archive with git-based naming
store_file() {
    local file=$1
    local extension=$2
    local git_id=$3
    local filename
    filename=$(basename "${file%.*}")

    if [ ! -f "$file" ]; then
        log_info "File not found: $file"
        return 0
    fi

    # Handle diff files: manuscript_diff -> manuscript_YYYYMMDD-HHMMSS_abc1234_diff
    if [[ "$filename" =~ _diff$ ]]; then
        local doc_base="${filename%_diff}"
        local archived_name="${doc_base}_${git_id}_diff"
    else
        local archived_name="${filename}_${git_id}"
    fi

    local archive_path="${SCITEX_WRITER_VERSIONS_DIR}/${archived_name}.${extension}"

    log_info "Archiving: $file -> $archive_path"
    cp "$file" "$archive_path"

    # Also keep a "current" copy without timestamp for easy access
    local current_path="${SCITEX_WRITER_VERSIONS_DIR}/${filename}.${extension}"
    cp "$file" "$current_path"
}

process_archive() {
    mkdir -p "$SCITEX_WRITER_VERSIONS_DIR"

    # Only archive on clean commits
    if ! is_git_clean; then
        echo_warning "    Skipping archive (uncommitted changes detected)"
        echo_warning "    Commit your changes to create an archive snapshot"
        return 0
    fi

    local git_id
    git_id=$(get_git_identifier)
    echo_success "    Archive identifier: $git_id"

    # Archive compiled files
    store_file "$SCITEX_WRITER_COMPILED_PDF" "pdf" "$git_id"
    store_file "$SCITEX_WRITER_COMPILED_TEX" "tex" "$git_id"
    store_file "$SCITEX_WRITER_DIFF_PDF" "pdf" "$git_id"
    store_file "$SCITEX_WRITER_DIFF_TEX" "tex" "$git_id"

    echo_success "    Files archived to: $SCITEX_WRITER_VERSIONS_DIR"
}

process_archive

# EOF
