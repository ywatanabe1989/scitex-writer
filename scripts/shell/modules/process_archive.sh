#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-28 18:49:30 (ywatanabe)"
# File: ./paper/scripts/shell/modules/process_archive.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

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

# Configurations
source ./config/load_config.sh $SCITEX_WRITER_DOC_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running ${BASH_SOURCE[0]}..."


function process_archive() {
    # echo_info "    Starting versioning process..."
    mkdir -p $SCITEX_WRITER_VERSIONS_DIR
    # echo_info "    Created backup directory: $SCITEX_WRITER_VERSIONS_DIR"

    count_version

    # echo_info "    Processing v$(cat $SCITEX_WRITER_VERSION_COUNTER_TXT) files..."
    store_files $SCITEX_WRITER_COMPILED_PDF "pdf"
    store_files $SCITEX_WRITER_COMPILED_TEX "tex"
    store_files $SCITEX_WRITER_DIFF_PDF "pdf"
    store_files $SCITEX_WRITER_DIFF_TEX "tex"

    # Git auto-commit (if enabled)
    if [ -f "./scripts/shell/modules/git_auto_commit.sh" ]; then
        source ./scripts/shell/modules/git_auto_commit.sh
        git_auto_commit || echo_warning "    Git auto-commit failed"
    fi

    # Archive cleanup (if enabled)
    if [ -f "./scripts/shell/modules/archive_cleanup.sh" ]; then
        source ./scripts/shell/modules/archive_cleanup.sh
        cleanup_old_archives || echo_warning "    Archive cleanup failed"
    fi
}

function count_version() {
    # echo_info "    Updating version counter..."
    if [ ! -f $SCITEX_WRITER_VERSION_COUNTER_TXT ]; then
        echo "000" > $SCITEX_WRITER_VERSION_COUNTER_TXT
        # echo_info "    $SCITEX_WRITER_VERSION_COUNTER_TXT Not Found"
        echo_success "    Initialized version counter: 000"
    fi

    if [ -f $SCITEX_WRITER_VERSION_COUNTER_TXT ]; then
        # Read ONLY the first line (version number)
        # Later lines may contain cleanup history comments
        version=$(head -n 1 "$SCITEX_WRITER_VERSION_COUNTER_TXT" | tr -d '[:space:]')

        # Validate and provide default if empty
        if [ -z "$version" ] || ! [[ "$version" =~ ^[0-9]+$ ]]; then
            echo_warning "    Invalid version counter, resetting to 000"
            version="000"
        fi

        # Increment version
        next_version=$(printf "%03d" $((10#${version} + 1)))

        # Preserve cleanup history if it exists
        if [ -f "$SCITEX_WRITER_VERSION_COUNTER_TXT" ]; then
            # Save cleanup history (all lines except first)
            cleanup_history=$(tail -n +2 "$SCITEX_WRITER_VERSION_COUNTER_TXT" 2>/dev/null || echo "")

            # Write new version and restore history
            echo "$next_version" > "$SCITEX_WRITER_VERSION_COUNTER_TXT"
            if [ -n "$cleanup_history" ]; then
                echo "$cleanup_history" >> "$SCITEX_WRITER_VERSION_COUNTER_TXT"
            fi
        else
            echo "$next_version" > "$SCITEX_WRITER_VERSION_COUNTER_TXT"
        fi

        echo_success "    Version allocated as: v$next_version"
    fi
}

function store_files() {
    local file=$1
    local extension=$2
    local filename=$(basename ${file%.*})

    # echo_info "    Processing file: $file"

    if [ -f $file ]; then
        # Read ONLY the first line (version number)
        version=$(head -n 1 "$SCITEX_WRITER_VERSION_COUNTER_TXT" | tr -d '[:space:]')

        # Special handling for diff files: change {doc_type}_diff to {doc_type}_vXXX_diff
        if [[ "$filename" =~ _diff$ ]]; then
            # Extract doc type (manuscript, supplementary, revision)
            local doc_base="${filename%_diff}"
            local versioned_name="${doc_base}_v${version}_diff"
        else
            local versioned_name="${filename}_v${version}"
        fi

        local hidden_link="${SCITEX_WRITER_VERSIONS_DIR}/.${filename}.${extension}"
        local tgt_path_current="./${versioned_name}.${extension}"
        local tgt_path_old="${SCITEX_WRITER_VERSIONS_DIR}/${versioned_name}.${extension}"

        # echo_info "    Copying to: $tgt_path_old"
        cp $file $tgt_path_old

        # echo_info "    Creating current version: $tgt_path_current"
        cp $file $tgt_path_current

        # echo_info "    Creating symbolic link: $hidden_link"
        rm $hidden_link -f > /dev/null 2>&1
        ln -s $tgt_path_current $hidden_link
    else
        echo_warn "    File not found: $file"
    fi
}

process_archive

# EOF