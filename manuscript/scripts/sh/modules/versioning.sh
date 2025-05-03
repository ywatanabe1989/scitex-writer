#!/bin/bash

echo -e "$0 ...\n"

OLD_DIR=./old/

COMPILED_PDF=./main/manuscript.pdf
COMPILED_TEX=./main/manuscript.tex

DIFF_TEX=./diff.tex
DIFF_PDF=./diff.pdf

VERSION_COUNTER_TXT="${OLD_DIR}.version_counter.txt"

function versioning() {
    mkdir -p $OLD_DIR

    remove_old_versions

    count_version

    store_files $COMPILED_PDF "pdf"
    store_files $COMPILED_TEX "tex"
    store_files $DIFF_PDF "pdf"
    store_files $DIFF_TEX "tex"
    }

function remove_old_versions() {
    rm ./compiled_v* -f #  > /dev/bull 2>&1
    rm ./diff_v* -f #> /dev/bull 2>&1
    }

function count_version() {
    if [ ! -f $VERSION_COUNTER_TXT ]; then
        echo "001" > $VERSION_COUNTER_TXT
    else
        version=$(<$VERSION_COUNTER_TXT)
        # next_version=$(printf "%03d" $((10#$version + 1)))
        next_version=$(printf "%03d" $((version + 1)))
        echo $next_version > $VERSION_COUNTER_TXT
    fi
}

function store_files() {
    local file=$1
    local extension=$2
    local filename=$(basename ${file%.*})

    if [ -f $file ]; then
        version=$(<"$VERSION_COUNTER_TXT")

        # local hidden_link="./.${filename}.${extension}"
        local hidden_link="${OLD_DIR}.${filename}.${extension}"
        rm $hidden_link -f > /dev/null 2>&1

        local tgt_path_current="./${filename}_v${version}.${extension}"
        local tgt_path_old="${OLD_DIR}${filename}_v${version}.${extension}"

        # cp $file $tgt_path_current
        cp $file $tgt_path_old
        # rm $file
        ln -s $tgt_path_current $hidden_link
    fi
}

versioning

## EOF
