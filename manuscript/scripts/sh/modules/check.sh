#!/bin/bash

echo -e "$0 ...\n"

function check_commands() {
    echo -e "\nChecking necessary commands..."
    for COMMAND in "$@"; do
        if ! command -v $COMMAND &> /dev/null; then
            echo "${COMMAND} could not be found. Please install the necessary package. (e.g., sudo apt-get install ${COMMAND} -y)"
            exit 1
        fi
    done
    echo -e "OK."
}

check_commands pdflatex bibtex xlsx2csv csv2latex parallel

## EOF
