#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 10:37:13 (ywatanabe)"
# File: ./manuscript/scripts/sh/modules/versioning.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


echo -e "$0 ...\n"

OLD_DIR=./old/
COMPILED_PDF=./manuscript.pdf
COMPILED_TEX=./manuscript.tex
DIFF_TEX=./diff.tex
DIFF_PDF=./diff.pdf
VERSION_COUNTER_TXT="${OLD_DIR}.version_counter.txt"

function versioning() {
    echo "Starting versioning process..."
    mkdir -p $OLD_DIR
    echo "Created backup directory: $OLD_DIR"

    remove_old_versions
    count_version

    echo "Processing files with version: $(cat $VERSION_COUNTER_TXT)"
    store_files $COMPILED_PDF "pdf"
    store_files $COMPILED_TEX "tex"
    store_files $DIFF_PDF "pdf"
    store_files $DIFF_TEX "tex"

    echo "Versioning completed successfully."
}

function remove_old_versions() {
    echo "Removing old version files from current directory..."
    rm ./compiled_v* -f
    rm ./diff_v* -f
}

function count_version() {
    echo "Updating version counter..."
    if [ ! -f $VERSION_COUNTER_TXT ]; then
        echo "001" > $VERSION_COUNTER_TXT
        echo "Initialized version counter: 001"
    else
        version=$(<$VERSION_COUNTER_TXT)
        next_version=$(printf "%03d" $((10#$version + 1)))
        echo $next_version > $VERSION_COUNTER_TXT
        echo "Incremented version counter: $next_version"
    fi
}

function store_files() {
    local file=$1
    local extension=$2
    local filename=$(basename ${file%.*})

    echo "Processing file: $file"
    if [ -f $file ]; then
        version=$(<"$VERSION_COUNTER_TXT")
        local hidden_link="${OLD_DIR}.${filename}.${extension}"
        rm $hidden_link -f > /dev/null 2>&1

        local tgt_path_current="./${filename}_v${version}.${extension}"
        local tgt_path_old="${OLD_DIR}${filename}_v${version}.${extension}"

        echo "  Copying to: $tgt_path_old"
        cp $file $tgt_path_old

        echo "  Creating current version: $tgt_path_current"
        cp $file $tgt_path_current

        echo "  Creating symbolic link: $hidden_link"
        ln -s $tgt_path_current $hidden_link
    else
        echo "  File not found: $file"
    fi
}

versioning

# EOF