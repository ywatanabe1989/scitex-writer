#!/bin/bash

echo -e "$0 ...\n"

function cleanup() {
    LOGDIR=./.logs
    mkdir -p $LOGDIR

    # Remove all bak files from the repository
    find . -type f -name "*bak*" -exec rm {} +

    # Remove Emacs temporary files
    find . -type f -name "#*#" -exec rm {} \;

    # Move files with these extensions (aux log out bbl blg spl dvi toc bak stderr stdout) under LOGDIR
    for ext in log out bbl blg spl dvi toc bak stderr stdout; do # aux 
        # mv *.$ext $LOGDIR > /dev/null 2>&1
        mv *.$ext ./main > /dev/null 2>&1        
    done

    # mv main.aux ./main/
}

cleanup

## EOF
