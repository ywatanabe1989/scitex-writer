#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-09-28 18:49:30 (ywatanabe)"
# File: ./paper/scripts/shell/modules/process_archive.sh

ORIG_DIR="$(pwd)"
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

# Configurations
source ./config/load_config.sh $STXW_DOC_TYPE

# Logging
touch "$LOG_PATH" >/dev/null 2>&1
echo
echo_info "Running $0..."


function process_archive() {
    # echo_info "    Starting versioning process..."
    mkdir -p $STXW_VERSIONS_DIR
    # echo_info "    Created backup directory: $STXW_VERSIONS_DIR"

    count_version

    # echo_info "    Processing v$(cat $STXW_VERSION_COUNTER_TXT) files..."
    store_files $STXW_COMPILED_PDF "pdf"
    store_files $STXW_COMPILED_TEX "tex"
    store_files $STXW_DIFF_PDF "pdf"
    store_files $STXW_DIFF_TEX "tex"
}

function count_version() {
    # echo_info "    Updating version counter..."
    if [ ! -f $STXW_VERSION_COUNTER_TXT ]; then
        echo "000" > $STXW_VERSION_COUNTER_TXT
        # echo_info "    $STXW_VERSION_COUNTER_TXT Not Found"
        echo_success "    Initialized version counter: 000"
    fi

    if [ -f $STXW_VERSION_COUNTER_TXT ]; then
        version=$(<$STXW_VERSION_COUNTER_TXT)
        next_version=$(printf "%03d" $((10#$version + 1)))
        echo $next_version > $STXW_VERSION_COUNTER_TXT
        echo_success "    Version allocated as: v$next_version"
    fi
}

function store_files() {
    local file=$1
    local extension=$2
    local filename=$(basename ${file%.*})

    # echo_info "    Processing file: $file"

    if [ -f $file ]; then
        version=$(<"$STXW_VERSION_COUNTER_TXT")

        # Special handling for diff files: change manuscript_diff to manuscript_vXXX_diff
        if [[ "$filename" == "manuscript_diff" ]]; then
            local versioned_name="manuscript_v${version}_diff"
        else
            local versioned_name="${filename}_v${version}"
        fi

        local hidden_link="${STXW_VERSIONS_DIR}/.${filename}.${extension}"
        local tgt_path_current="./${versioned_name}.${extension}"
        local tgt_path_old="${STXW_VERSIONS_DIR}/${versioned_name}.${extension}"

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