#!/bin/bash

echo -e "$0 ...\n"

function cleanup() {
    LOGDIR=./.logs
    DEBUG_DIR=./main/debug
    
    # Create debug and log directories
    mkdir -p $LOGDIR
    mkdir -p $DEBUG_DIR
    
    # Set the timestamp for backup files
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    
    # Create a debug info file
    echo "Cleanup performed at $(date)" > $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
    echo "Current directory: $(pwd)" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
    echo "Files before cleanup:" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
    ls -la >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
    
    # Backup important intermediate files before cleanup
    if [ -f manuscript.tex ]; then
        cp manuscript.tex $DEBUG_DIR/manuscript_$TIMESTAMP.tex
        echo "Backed up manuscript.tex to $DEBUG_DIR/manuscript_$TIMESTAMP.tex" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
    fi
    
    if [ -f main.tex ]; then
        cp main.tex $DEBUG_DIR/main_$TIMESTAMP.tex
        echo "Backed up main.tex to $DEBUG_DIR/main_$TIMESTAMP.tex" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
    fi
    
    if [ -f main.aux ]; then
        cp main.aux $DEBUG_DIR/main_$TIMESTAMP.aux
        echo "Backed up main.aux to $DEBUG_DIR/main_$TIMESTAMP.aux" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
    fi
    
    # Special backup for figure-related files
    if [ -d ./src/figures ]; then
        echo "Backing up figure-related files" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
        mkdir -p $DEBUG_DIR/figures_$TIMESTAMP
        
        # Backup compiled figures
        if [ -d ./src/figures/compiled ]; then
            mkdir -p $DEBUG_DIR/figures_$TIMESTAMP/compiled
            cp -r ./src/figures/compiled/* $DEBUG_DIR/figures_$TIMESTAMP/compiled/ 2>/dev/null
            echo "Backed up compiled figures" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
        fi
        
        # Backup hidden figure files
        if [ -d ./src/figures/.tex ]; then
            mkdir -p $DEBUG_DIR/figures_$TIMESTAMP/.tex
            cp -r ./src/figures/.tex/* $DEBUG_DIR/figures_$TIMESTAMP/.tex/ 2>/dev/null
            echo "Backed up hidden figure files" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
        fi
    fi

    # Remove Emacs temporary files
    find . -type f -name "#*#" -exec rm {} \;
    echo "Removed Emacs temporary files" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
    
    # Move files with these extensions to main directory instead of deleting
    for ext in log out bbl blg spl dvi toc stderr stdout; do
        if ls *.$ext 1> /dev/null 2>&1; then
            # Copy to debug directory first
            for file in *.$ext; do
                cp "$file" "$DEBUG_DIR/${file%.ext}_$TIMESTAMP.$ext" 2>/dev/null
            done
            # Then move to main directory
            mv *.$ext ./main 2>/dev/null
            echo "Moved *.$ext files to ./main" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
        fi
    done
    
    # Handle .bak files specially - backup to debug before removing
    if ls *.bak 1> /dev/null 2>&1; then
        for file in *.bak; do
            cp "$file" "$DEBUG_DIR/${file%.bak}_$TIMESTAMP.bak" 2>/dev/null
        done
        # Now remove them
        find . -type f -name "*.bak" -exec rm {} + 2>/dev/null
        echo "Backed up and removed .bak files" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
    fi
    
    # Make sure main.aux is in the main directory if it exists
    if [ -f main.aux ]; then
        cp main.aux ./main/
        echo "Copied main.aux to ./main/" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
    fi
    
    echo "Files after cleanup:" >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
    ls -la >> $DEBUG_DIR/cleanup_info_$TIMESTAMP.txt
}

cleanup

## EOF
