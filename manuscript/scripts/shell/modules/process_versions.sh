#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 23:09:30 (ywatanabe)"
# File: ./manuscript/scripts/shell/modules/process_versions.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


source ./config.src
echo_info "$0..."


function process_versions() {
    echo_info "Starting versioning process..."
    mkdir -p $VERSIONS_DIR
    echo_info "Created backup directory: $VERSIONS_DIR"

    count_version

    echo_info "Processing files with version: $(cat $VERSION_COUNTER_TXT)"
    store_files $COMPILED_PDF "pdf"
    store_files $COMPILED_TEX "tex"
    store_files $DIFF_PDF "pdf"
    store_files $DIFF_TEX "tex"
}

function count_version() {
    echo_info "Updating version counter..."
    if [ ! -f $VERSION_COUNTER_TXT ]; then
        echo "001" > $VERSION_COUNTER_TXT
        echo_info "$VERSION_COUNTER_TXT Not Found"
        echo_info "Initialized version counter: 001"
    fi

    if [ -f $VERSION_COUNTER_TXT ]; then
        version=$(<$VERSION_COUNTER_TXT)
        next_version=$(printf "%03d" $((10#$version + 1)))
        echo $next_version > $VERSION_COUNTER_TXT
        echo_success "v$next_version allocated"
    fi
}

function store_files() {
    local file=$1
    local extension=$2
    local filename=$(basename ${file%.*})

    echo_info "Processing file: $file"

    if [ -f $file ]; then
        version=$(<"$VERSION_COUNTER_TXT")
        local hidden_link="${VERSIONS_DIR}/.${filename}.${extension}"
        local tgt_path_current="./${filename}_v${version}.${extension}"
        local tgt_path_old="${VERSIONS_DIR}/${filename}_v${version}.${extension}"

        echo_info "  Copying to: $tgt_path_old"
        cp $file $tgt_path_old

        echo_info "  Creating current version: $tgt_path_current"
        cp $file $tgt_path_current

        echo_info "  Creating symbolic link: $hidden_link"
        rm $hidden_link -f > /dev/null 2>&1
        ln -s $tgt_path_current $hidden_link
    else
        echo_error "  File not found: $file"
    fi
}

process_versions

# EOF