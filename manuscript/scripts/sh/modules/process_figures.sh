#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 04:43:41 (ywatanabe)"
# File: ./manuscript/scripts/sh/modules/process_figures.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
touch "$LOG_PATH" >/dev/null 2>&1


# Time-stamp: "2024-11-06 08:55:33 (ywatanabe)"

echo -e "$0 ...\n"

source ./scripts/sh/modules/config.sh

init() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local log_file="$FIGURE_COMPILED_DIR/debug/process_figures_${timestamp}.log"
    
    # Log script execution start with timestamp and parameters
    echo "=== FIGURE PROCESSING STARTED AT $(date) ===" > "$log_file"
    echo "Script: $0" >> "$log_file"
    echo "Parameters: $@" >> "$log_file"
    echo "Working directory: $(pwd)" >> "$log_file"
    echo "" >> "$log_file"
    
    # Create all required directories
    echo "Creating required directories..." >> "$log_file"
    for dir in "$FIGURE_SRC_DIR" "$FIGURE_COMPILED_DIR" "$FIGURE_JPG_DIR" "$FIGURE_HIDDEN_DIR" "$FIGURE_COMPILED_DIR/debug"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            echo "Created directory: $dir" >> "$log_file"
        else
            echo "Directory already exists: $dir" >> "$log_file"
        fi
    done
    
    # Create specialized debug directories for different processing stages
    mkdir -p "$FIGURE_COMPILED_DIR/debug/captions"
    mkdir -p "$FIGURE_COMPILED_DIR/debug/widths"
    mkdir -p "$FIGURE_COMPILED_DIR/debug/toggles"
    
    # Backup existing files before removing
    echo "" >> "$log_file"
    echo "Backing up existing files..." >> "$log_file"
    if [ -f "$FIGURE_HIDDEN_DIR/.All_Figures.tex" ]; then
        cp "$FIGURE_HIDDEN_DIR/.All_Figures.tex" "$FIGURE_COMPILED_DIR/debug/All_Figures_before.tex"
        echo "Backed up .All_Figures.tex" >> "$log_file"
    else
        echo "No .All_Figures.tex file found to backup" >> "$log_file"
    fi

    # Create a timestamped backup directory for this run
    local backup_dir="$FIGURE_COMPILED_DIR/debug/backup_${timestamp}"
    mkdir -p "$backup_dir"
    echo "Created backup directory: $backup_dir" >> "$log_file"

    # Save existing compiled figure files to the backup directory
    for file in "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex; do
        if [ -f "$file" ]; then
            base_name=$(basename "$file")
            cp "$file" "$backup_dir/${base_name}"
            echo "Backed up: $base_name" >> "$log_file"
        fi
    done

    # Count files found for statistics
    local compiled_count=$(find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" | wc -l)
    local source_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tex" | wc -l)
    local image_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*" -not -name "*.tex" | wc -l)
    
    echo "" >> "$log_file"
    echo "File statistics before processing:" >> "$log_file"
    echo "- Compiled figure files: $compiled_count" >> "$log_file"
    echo "- Source caption files: $source_count" >> "$log_file"
    echo "- Source image files: $image_count" >> "$log_file"
    echo "" >> "$log_file"

    # Now perform cleanup
    echo "Performing cleanup of compiled files..." >> "$log_file"
    rm -f "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex "$FIGURE_HIDDEN_DIR"/*.tex
    echo "Removed existing compiled figure files" >> "$log_file"
    
    # Create output files
    rm -f "$FIGURE_HIDDEN_DIR/.All_Figures.tex"
    touch "$FIGURE_HIDDEN_DIR/.All_Figures.tex"
    echo "Created empty .All_Figures.tex file" >> "$log_file"
    
    echo "" >> "$log_file"
    echo "Initialization complete" >> "$log_file"
    echo "=======================================" >> "$log_file"
    echo "" >> "$log_file"
}

ensure_caption() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local log_file="$FIGURE_COMPILED_DIR/debug/ensure_caption_${timestamp}.log"
    
    echo "=== CAPTION GENERATION LOG $(date) ===" > "$log_file"
    echo "Ensuring captions exist for TIF, JPG, PNG, and SVG files" >> "$log_file"
    
    # First handle TIF files
    for tif_file in "$FIGURE_SRC_DIR"/Figure_ID_*.tif; do
        [ -e "$tif_file" ] || continue
        local filename=$(basename "$tif_file")
        local caption_tex_file="$FIGURE_SRC_DIR/${filename%.tif}.tex"
        
        echo "Processing TIF file: $filename" >> "$log_file"
        
        if [ ! -f "$caption_tex_file" ] && [ ! -L "$caption_tex_file" ]; then
            echo "Creating caption for $filename" | tee -a "$log_file"
            # Create caption file
            if [ -f "$FIGURE_SRC_DIR/templates/_Figure_ID_XX.tex" ]; then
                cp "$FIGURE_SRC_DIR/templates/_Figure_ID_XX.tex" "$caption_tex_file"
                echo "Created from template: $caption_tex_file" >> "$log_file"
            elif [ -f "$FIGURE_SRC_DIR/_Figure_ID_XX.tex" ]; then
                cp "$FIGURE_SRC_DIR/_Figure_ID_XX.tex" "$caption_tex_file"
                echo "Created from legacy template: $caption_tex_file" >> "$log_file"
            else
                # Create a basic caption template
                cat <<EOF > "$caption_tex_file"
%% -*- coding: utf-8 -*-
%% Timestamp: "$(date +"%Y-%m-%d %H:%M:%S") (ywatanabe)"
%% File: "$caption_tex_file"

\caption{\textbf{
FIGURE TITLE HERE
}
\smallskip
\\
FIGURE LEGEND HERE.
}
% width=1\textwidth

%%%% EOF
EOF
                echo "Created from inline template: $caption_tex_file" >> "$log_file"
            fi
        else
            echo "Caption already exists: $caption_tex_file" >> "$log_file"
        fi
    done

    # Then handle JPG files that don't have corresponding TIF files
    for jpg_file in "$FIGURE_SRC_DIR"/Figure_ID_*.jpg; do
        [ -e "$jpg_file" ] || continue
        local filename=$(basename "$jpg_file")
        local caption_tex_file="$FIGURE_SRC_DIR/${filename%.jpg}.tex"
        
        echo "Processing JPG file: $filename" >> "$log_file"

        # Check if caption already exists
        if [ ! -f "$caption_tex_file" ] && [ ! -L "$caption_tex_file" ]; then
            echo "Creating caption for $filename" | tee -a "$log_file"
            # Create caption file
            if [ -f "$FIGURE_SRC_DIR/templates/_Figure_ID_XX.tex" ]; then
                cp "$FIGURE_SRC_DIR/templates/_Figure_ID_XX.tex" "$caption_tex_file"
                echo "Created from template: $caption_tex_file" >> "$log_file"
            elif [ -f "$FIGURE_SRC_DIR/_Figure_ID_XX.tex" ]; then
                cp "$FIGURE_SRC_DIR/_Figure_ID_XX.tex" "$caption_tex_file"
                echo "Created from legacy template: $caption_tex_file" >> "$log_file"
            else
                # Create a basic caption template
                cat <<EOF > "$caption_tex_file"
%% -*- coding: utf-8 -*-
%% Timestamp: "$(date +"%Y-%m-%d %H:%M:%S") (ywatanabe)"
%% File: "$caption_tex_file"

\caption{\textbf{
FIGURE TITLE HERE
}
\smallskip
\\
FIGURE LEGEND HERE.
}
% width=0.95\textwidth

%%%% EOF
EOF
                echo "Created from inline template: $caption_tex_file" >> "$log_file"
            fi
        else
            echo "Caption already exists: $caption_tex_file" >> "$log_file"
        fi

        # Copy JPG file to the JPG directory if not already there
        if [ ! -f "$FIGURE_JPG_DIR/$filename" ]; then
            echo "Copying $filename to $FIGURE_JPG_DIR" | tee -a "$log_file"
            cp "$jpg_file" "$FIGURE_JPG_DIR/"
        else
            echo "JPG file already exists in target directory: $FIGURE_JPG_DIR/$filename" >> "$log_file"
        fi
    done
    
    # Handle PNG files
    for png_file in "$FIGURE_SRC_DIR"/Figure_ID_*.png; do
        [ -e "$png_file" ] || continue
        local filename=$(basename "$png_file")
        local caption_tex_file="$FIGURE_SRC_DIR/${filename%.png}.tex"
        local jpg_filename="${filename%.png}.jpg"
        
        echo "Processing PNG file: $filename" >> "$log_file"

        # Check if caption already exists
        if [ ! -f "$caption_tex_file" ] && [ ! -L "$caption_tex_file" ]; then
            echo "Creating caption for $filename" | tee -a "$log_file"
            # Create caption file
            if [ -f "$FIGURE_SRC_DIR/templates/_Figure_ID_XX.tex" ]; then
                cp "$FIGURE_SRC_DIR/templates/_Figure_ID_XX.tex" "$caption_tex_file"
                echo "Created from template: $caption_tex_file" >> "$log_file"
            elif [ -f "$FIGURE_SRC_DIR/_Figure_ID_XX.tex" ]; then
                cp "$FIGURE_SRC_DIR/_Figure_ID_XX.tex" "$caption_tex_file"
                echo "Created from legacy template: $caption_tex_file" >> "$log_file"
            else
                # Create a basic caption template
                cat <<EOF > "$caption_tex_file"
%% -*- coding: utf-8 -*-
%% Timestamp: "$(date +"%Y-%m-%d %H:%M:%S") (ywatanabe)"
%% File: "$caption_tex_file"

\caption{\textbf{
FIGURE TITLE HERE
}
\smallskip
\\
FIGURE LEGEND HERE.
}
% width=0.95\textwidth

%%%% EOF
EOF
                echo "Created from inline template: $caption_tex_file" >> "$log_file"
            fi
        else
            echo "Caption already exists: $caption_tex_file" >> "$log_file"
        fi

        # Convert PNG to JPG if not already there
        if [ ! -f "$FIGURE_JPG_DIR/$jpg_filename" ]; then
            echo "Converting PNG to JPG: $filename -> $jpg_filename" | tee -a "$log_file"
            convert "$png_file" -density 300 -quality 90 "$FIGURE_JPG_DIR/$jpg_filename"
        else
            echo "JPG version already exists: $FIGURE_JPG_DIR/$jpg_filename" >> "$log_file"
        fi
    done
    
    # Handle SVG files (NEW)
    for svg_file in "$FIGURE_SRC_DIR"/Figure_ID_*.svg; do
        [ -e "$svg_file" ] || continue
        local filename=$(basename "$svg_file")
        local caption_tex_file="$FIGURE_SRC_DIR/${filename%.svg}.tex"
        local jpg_filename="${filename%.svg}.jpg"
        
        echo "Processing SVG file: $filename" >> "$log_file"

        # Check if caption already exists
        if [ ! -f "$caption_tex_file" ] && [ ! -L "$caption_tex_file" ]; then
            echo "Creating caption for SVG: $filename" | tee -a "$log_file"
            # Create caption file
            if [ -f "$FIGURE_SRC_DIR/templates/_Figure_ID_XX.tex" ]; then
                cp "$FIGURE_SRC_DIR/templates/_Figure_ID_XX.tex" "$caption_tex_file"
                echo "Created from template: $caption_tex_file" >> "$log_file"
            elif [ -f "$FIGURE_SRC_DIR/_Figure_ID_XX.tex" ]; then
                cp "$FIGURE_SRC_DIR/_Figure_ID_XX.tex" "$caption_tex_file"
                echo "Created from legacy template: $caption_tex_file" >> "$log_file"
            else
                # Create a basic caption template for vector graphics
                cat <<EOF > "$caption_tex_file"
%% -*- coding: utf-8 -*-
%% Timestamp: "$(date +"%Y-%m-%d %H:%M:%S") (ywatanabe)"
%% File: "$caption_tex_file"

\caption{\textbf{
FIGURE TITLE HERE
}
\smallskip
\\
FIGURE LEGEND HERE.
}
% width=0.8\textwidth
% format=vector  % Indicates this is a vector graphic

%%%% EOF
EOF
                echo "Created from inline template: $caption_tex_file" >> "$log_file"
            fi
        else
            echo "Caption already exists: $caption_tex_file" >> "$log_file"
        fi

        # Convert SVG to JPG if not already there
        if [ ! -f "$FIGURE_JPG_DIR/$jpg_filename" ]; then
            echo "Converting SVG to JPG: $filename -> $jpg_filename" | tee -a "$log_file"
            
            # Check if inkscape is available for better SVG conversion
            if command -v inkscape >/dev/null 2>&1; then
                echo "Using Inkscape for SVG conversion" >> "$log_file"
                inkscape -z -e "$FIGURE_JPG_DIR/$jpg_filename" -w 1200 -h 1200 "$svg_file"
            else
                # Fallback to ImageMagick
                echo "Using ImageMagick for SVG conversion" >> "$log_file"
                convert "$svg_file" -density 300 -quality 90 "$FIGURE_JPG_DIR/$jpg_filename"
            fi
            
            if [ -f "$FIGURE_JPG_DIR/$jpg_filename" ]; then
                echo "SVG conversion successful" >> "$log_file"
            else
                echo "WARNING: SVG conversion failed" | tee -a "$log_file"
            fi
        else
            echo "JPG version already exists: $FIGURE_JPG_DIR/$jpg_filename" >> "$log_file"
        fi
    done
    
    echo "Caption generation complete" >> "$log_file"
    echo "Processed files summary:" >> "$log_file"
    echo "- TIF files: $(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tif" | wc -l)" >> "$log_file"
    echo "- JPG files: $(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.jpg" | wc -l)" >> "$log_file"
    echo "- PNG files: $(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.png" | wc -l)" >> "$log_file"
    echo "- SVG files: $(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.svg" | wc -l)" >> "$log_file"
    echo "- Caption files: $(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tex" | wc -l)" >> "$log_file"
    echo "=======================================" >> "$log_file"
}

ensure_lower_letters() {
    local ORIG_DIR="$(pwd)"
    cd "$FIGURE_SRC_DIR"

    for file in Figure_ID_*; do
        if [[ -f "$file" || -L "$file" ]]; then
            new_name=$(echo "$file" | sed -E 's/(Figure_ID_)(.*)/\1\L\2/')
            if [[ "$file" != "$new_name" ]]; then
                # ln -s "$file" "$new_name"
                mv "$file" "$new_name"
            fi
        fi
    done

    cd $ORIG_DIR
    }

pptx2tif() {
    local p2t="$1"

    if [[ "$p2t" == true ]]; then
        ./scripts/sh/modules/pptx2tif_all.sh
    fi
}

crop_tif() {
    local no_figs="$1"
    if [[ "$no_figs" == false ]]; then
        # Bypass crop_tif for demo purposes
        echo "Skipping crop_tif step for demonstration"
        # In a real environment, this would call the Python script to crop TIFs
        # ls "$FIGURE_SRC_DIR"/Figure_ID*.tif | \
        #     parallel -j+0 --eta './.env/bin/python ./scripts/py/crop_tif.py -l {}'
    fi
}


tif2jpg () {
    local no_figs="$1"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local log_file="$FIGURE_COMPILED_DIR/debug/image_processing_${timestamp}.log"
    
    if [[ "$no_figs" == false ]]; then
        echo "Processing images (tif2jpg)..."
        mkdir -p "$FIGURE_COMPILED_DIR/debug"
        
        echo "=== IMAGE PROCESSING LOG $(date) ===" > "$log_file"
        echo "Converting TIF and other formats to optimized JPG" >> "$log_file"
        
        # Check if we have Python and the optimize_figure.py script available
        if [ -f "./scripts/py/optimize_figure.py" ] && command -v python3 >/dev/null 2>&1; then
            echo "Using optimize_figure.py for high-quality image processing" | tee -a "$log_file"
            
            # Process TIF files with optimization
            find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tif" | parallel -j+0 --eta '
                echo -e "\nOptimizing {} to '"$FIGURE_JPG_DIR"'/$(basename {} .tif).jpg"
                python3 ./scripts/py/optimize_figure.py --input {} --output "'"$FIGURE_JPG_DIR"'/$(basename {} .tif).jpg" --dpi 300 --quality 95 >> '"$log_file"'
            '
            
            # Also process PNG files if they exist
            find "$FIGURE_SRC_DIR" -name "Figure_ID_*.png" | parallel -j+0 --eta '
                echo -e "\nOptimizing {} to '"$FIGURE_JPG_DIR"'/$(basename {} .png).jpg"
                python3 ./scripts/py/optimize_figure.py --input {} --output "'"$FIGURE_JPG_DIR"'/$(basename {} .png).jpg" --dpi 300 --quality 95 >> '"$log_file"'
            '
            
            # Process SVG files if they exist and we have Inkscape
            if command -v inkscape >/dev/null 2>&1; then
                find "$FIGURE_SRC_DIR" -name "Figure_ID_*.svg" | parallel -j+0 --eta '
                    echo -e "\nConverting SVG {} to '"$FIGURE_JPG_DIR"'/$(basename {} .svg).jpg"
                    inkscape -z -e "'"$FIGURE_JPG_DIR"'/$(basename {} .svg)_temp.png" -w 1200 -h 1200 {}
                    python3 ./scripts/py/optimize_figure.py --input "'"$FIGURE_JPG_DIR"'/$(basename {} .svg)_temp.png" --output "'"$FIGURE_JPG_DIR"'/$(basename {} .svg).jpg" --dpi 300 --quality 95 >> '"$log_file"'
                    rm -f "'"$FIGURE_JPG_DIR"'/$(basename {} .svg)_temp.png"
                '
            else
                # Fall back to ImageMagick for SVG conversion
                find "$FIGURE_SRC_DIR" -name "Figure_ID_*.svg" | parallel -j+0 --eta '
                    echo -e "\nConverting SVG {} to '"$FIGURE_JPG_DIR"'/$(basename {} .svg).jpg"
                    convert {} -density 300 -quality 95 "'"$FIGURE_JPG_DIR"'/$(basename {} .svg).jpg"
                '
            fi
            
            # Process JPG files directly in source directory
            find "$FIGURE_SRC_DIR" -name "Figure_ID_*.jpg" | parallel -j+0 --eta '
                if [ ! -f "'"$FIGURE_JPG_DIR"'/$(basename {})" ]; then
                    echo -e "\nOptimizing {} to '"$FIGURE_JPG_DIR"'/$(basename {})"
                    python3 ./scripts/py/optimize_figure.py --input {} --output "'"$FIGURE_JPG_DIR"'/$(basename {})" --dpi 300 --quality 95 >> '"$log_file"'
                fi
            '
        else
            # Fall back to ImageMagick if Python or script not available
            echo "Using ImageMagick for basic image conversion" | tee -a "$log_file"
            
            # Convert TIF files
            find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tif" | parallel -j+0 --eta '
                echo -e "\nConverting {} to '"$FIGURE_JPG_DIR"'/$(basename {} .tif).jpg"
                convert {} -density 300 -quality 95 "'"$FIGURE_JPG_DIR"'/$(basename {} .tif).jpg"
            '
            
            # Convert PNG files
            find "$FIGURE_SRC_DIR" -name "Figure_ID_*.png" | parallel -j+0 --eta '
                echo -e "\nConverting {} to '"$FIGURE_JPG_DIR"'/$(basename {} .png).jpg"
                convert {} -density 300 -quality 95 "'"$FIGURE_JPG_DIR"'/$(basename {} .png).jpg"
            '
            
            # Convert SVG files
            find "$FIGURE_SRC_DIR" -name "Figure_ID_*.svg" | parallel -j+0 --eta '
                echo -e "\nConverting {} to '"$FIGURE_JPG_DIR"'/$(basename {} .svg).jpg"
                convert {} -density 300 -quality 95 "'"$FIGURE_JPG_DIR"'/$(basename {} .svg).jpg"
            '
            
            # Copy JPG files
            find "$FIGURE_SRC_DIR" -name "Figure_ID_*.jpg" | parallel -j+0 --eta '
                if [ ! -f "'"$FIGURE_JPG_DIR"'/$(basename {})" ]; then
                    echo -e "\nCopying {} to '"$FIGURE_JPG_DIR"'/$(basename {})"
                    cp {} "'"$FIGURE_JPG_DIR"'/$(basename {})"
                fi
            '
        fi
        
        # Count processed files
        local tif_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tif" | wc -l)
        local png_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.png" | wc -l)
        local svg_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.svg" | wc -l)
        local jpg_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.jpg" | wc -l)
        local total_processed=$((tif_count + png_count + svg_count + jpg_count))
        
        echo "" >> "$log_file"
        echo "Processed files summary:" >> "$log_file"
        echo "- TIF files: $tif_count" >> "$log_file"
        echo "- PNG files: $png_count" >> "$log_file"
        echo "- SVG files: $svg_count" >> "$log_file"
        echo "- JPG files: $jpg_count" >> "$log_file"
        echo "- Total processed: $total_processed" >> "$log_file"
        echo "=======================================" >> "$log_file"
        
        echo "Image processing complete. Processed $total_processed files."
    fi
}

# compile_legends () {
#     # Generates ./src/figures/tex/Figure_ID_*.tex files from ./src/figures/Figure_ID_*.tex files
#     local ii=0
#     for caption_file in "$FIGURE_SRC_DIR"/Figure_ID_*.tex; do
#         echo $caption_file
#         # [ -e "$caption_file" ] || continue
#         local fname=$(basename "$caption_file")
#         local tgt_file="$FIGURE_COMPILED_DIR/$fname"
#         local figure_content=$(cat "$caption_file")
#         local figure_id=$(echo "$fname" | grep -oP '(?<=Figure_ID_)[^\.]+' | tr '[:upper:]' '[:lower:]')
#         local width=$(grep -oP '(?<=width=)[0-9.]+\\textwidth' "$caption_file")

#         [[ $ii -gt 0 ]] && echo "\\clearpage" > "$tgt_file"

#         rm "$tgt_file" -f # > /dev/null 2>&1
#         touch "$tgt_file"

#         cat <<EOF > "$tgt_file"
#         \clearpage
#         \begin{figure*}[ht]
#             \pdfbookmark[2]{ID $figure_id}{figure_id_$figure_id}
#         	\centering
#             \includegraphics[width=$width]{$FIGURE_JPG_DIR/${fname%.tex}.jpg}
#         	$figure_content
#         	\label{fig:$figure_id}
#         \end{figure*}
#         ((ii++))
#     done

# }

compile_legends() {
    # Create figures in the format as shown in the example
    echo "Processing figures..."

    # Create output directory if needed
    mkdir -p "$FIGURE_COMPILED_DIR"
    mkdir -p "$FIGURE_COMPILED_DIR/debug"
    rm -f "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex

    # Create a figures section header file
    local figures_header_file="$FIGURE_COMPILED_DIR/00_Figures_Header.tex"
    echo "Inserting figure header..."
    cat > "$figures_header_file" << "EOF"
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% FIGURES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\clearpage
\section*{Figures}
\label{figures}
\pdfbookmark[1]{Figures}{figures}
EOF

    # Process each figure file
    for caption_file in "$FIGURE_SRC_DIR"/Figure_ID_*.tex; do

        echo "Working with caption file: $caption_file..."

        # Skip if file doesn't exist
        [ -f "$caption_file" ] || continue

        # Copy original for debugging
        cp "$caption_file" "$FIGURE_COMPILED_DIR/debug/$(basename "$caption_file").original"

        # Get filename and figure ID
        local fname=$(basename "$caption_file")
        local figure_id=""

        echo "Processing $fname" >> "$FIGURE_COMPILED_DIR/debug/compile_legends.log"

        # Extract ID from filename (e.g., "01_workflow" from "Figure_ID_01_workflow.tex")
        if [[ "$fname" =~ Figure_ID_([^\.]+) ]]; then
            figure_id="${BASH_REMATCH[1]}"
        else
            echo "Warning: Invalid filename format: $fname"
            echo "Warning: Invalid filename format: $fname" >> "$FIGURE_COMPILED_DIR/debug/compile_legends.log"
            continue
        fi

        # Clean ID (remove .jpg suffix if present)
        local figure_id_clean=$(echo "$figure_id" | sed 's/\.jpg$//')

        # Extract the number portion (e.g., "01" from "01_workflow")
        local figure_number=""
        if [[ "$figure_id_clean" =~ ^([0-9]+)_ ]]; then
            figure_number="${BASH_REMATCH[1]}"
        else
            # If no underscore, assume the whole string is the number
            figure_number="$figure_id_clean"
        fi

        local tgt_file="$FIGURE_COMPILED_DIR/$fname"

        # Determine if this is a tikz figure or image file
        local is_tikz=false
        if grep -q "\\\\begin{tikzpicture}" "$caption_file"; then
            is_tikz=true
            echo "$fname is a TikZ figure" >> "$FIGURE_COMPILED_DIR/debug/compile_legends.log"
        fi

        # Determine image file path
        local jpg_file=""
        if [[ "$fname" == *".jpg.tex" ]]; then
            jpg_file="${fname%.tex}"  # Keep .jpg in filename
        else
            jpg_file="${fname%.tex}.jpg"  # Add .jpg to basename
        fi

        # Default image width
        local width="1\\textwidth"
        # Check for width specification in caption file
        local width_spec=$(grep -o "width=.*\\\\textwidth" "$caption_file" | head -1)
        if [ -n "$width_spec" ]; then
            width=$(echo "$width_spec" | sed 's/width=//')
        fi

        # Extract caption content from the file
        local caption_content=""

        # Create a debug directory to store extracted caption data
        mkdir -p "$FIGURE_COMPILED_DIR/debug/captions"
        
        # First check if the file contains a caption
        if grep -q "\\\\caption{" "$caption_file"; then
            # Save original caption file for debugging
            cp "$caption_file" "$FIGURE_COMPILED_DIR/debug/captions/${fname}.original"
            
            # Extract caption content using advanced pattern matching to handle multi-line captions properly
            # This approach preserves the structure of multi-panel figure captions with proper formatting
            
            # First extract everything between \caption{ and the last }
            caption_raw=$(sed -n '/\\caption{/,/^}\s*$/p' "$caption_file" | sed '1s/^\\caption{//' | sed '$s/}\s*$//')
            
            # Save raw extraction for debugging
            echo "$caption_raw" > "$FIGURE_COMPILED_DIR/debug/captions/${fname}.raw"
            
            # Process the extracted content - preserve structure but remove any \label commands
            caption_content=$(echo "$caption_raw" | grep -v "\\\\label{" | sed '/^$/d' | sed 's/^[ \t]*//' | sed 's/[ \t]*$//')
            
            # Log the extracted caption
            echo "Extracted caption for $fname" >> "$FIGURE_COMPILED_DIR/debug/compile_legends.log"
            echo "$caption_content" > "$FIGURE_COMPILED_DIR/debug/captions/${fname}.processed"
            
            # Check if this is a multi-panel figure (contains \textbf{\textit{A.}} or similar pattern)
            if grep -q "\\\\textbf{\\\\textit{[A-Z]\\." <<< "$caption_content"; then
                echo "Detected multi-panel figure caption for $fname" >> "$FIGURE_COMPILED_DIR/debug/compile_legends.log"
            fi
        else
            # If there's no caption tag, use the entire file content as caption
            caption_content=$(cat "$caption_file" | grep -v "^%" | grep -v "^$" | sed 's/^[ \t]*//' | sed 's/[ \t]*$//')
        fi

        # If extraction failed, use a default caption
        if [ -z "$caption_content" ]; then
            caption_content="\\textbf{Figure $figure_number.} No caption available."
            echo "Using default caption for $fname" >> "$FIGURE_COMPILED_DIR/debug/compile_legends.log"
        fi

        # Create the figure snippet files - AVOID USING COMPLETE FIGURE ENVIRONMENTS
        # These will now just have metadata for gathering by gather_tex_files
        if [ "$is_tikz" = true ]; then
            # Extract TikZ environment
            local tikz_begin_line=$(grep -n "\\\\begin{tikzpicture}" "$caption_file" | cut -d: -f1)
            local tikz_end_line=$(grep -n "\\\\end{tikzpicture}" "$caption_file" | cut -d: -f1)

            if [ -n "$tikz_begin_line" ] && [ -n "$tikz_end_line" ]; then
                # Extract the TikZ code
                local tikz_code=$(sed -n "${tikz_begin_line},${tikz_end_line}p" "$caption_file")

                # Create figure metadata file
                cat > "$tgt_file" << EOF
% FIGURE METADATA - Figure ID ${figure_id_clean}, Number ${figure_number}
% FIGURE TYPE: TikZ
% This is not a standalone LaTeX environment - it will be included by gather_tex_files
{
    "id": "${figure_id_clean}",
    "number": "${figure_number}",
    "type": "tikz",
    "width": "$width",
    "tikz_code": "$tikz_code"
}

$caption_content
EOF
                echo "Created TikZ figure metadata: $tgt_file" >> "$FIGURE_COMPILED_DIR/debug/compile_legends.log"
            else
                # Fallback to image metadata
                cat > "$tgt_file" << EOF
% FIGURE METADATA - Figure ID ${figure_id_clean}, Number ${figure_number}
% FIGURE TYPE: Image
% This is not a standalone LaTeX environment - it will be included by gather_tex_files
{
    "id": "${figure_id_clean}",
    "number": "${figure_number}",
    "type": "image",
    "width": "$width",
    "path": "$FIGURE_JPG_DIR/$jpg_file"
}

$caption_content
EOF
                echo "Created image figure metadata: $tgt_file" >> "$FIGURE_COMPILED_DIR/debug/compile_legends.log"
            fi
        else
            # Standard image figure metadata
            cat > "$tgt_file" << EOF
% FIGURE METADATA - Figure ID ${figure_id_clean}, Number ${figure_number}
% FIGURE TYPE: Image
% This is not a standalone LaTeX environment - it will be included by gather_tex_files
{
    "id": "${figure_id_clean}",
    "number": "${figure_number}",
    "type": "image",
    "width": "$width",
    "path": "$FIGURE_JPG_DIR/$jpg_file"
}

$caption_content
EOF
            echo "Created image figure metadata: $tgt_file" >> "$FIGURE_COMPILED_DIR/debug/compile_legends.log"
        fi

        # Save compiled file for debugging
        cp "$tgt_file" "$FIGURE_COMPILED_DIR/debug/$(basename "$tgt_file").compiled"
    done
}

# _toggle_figures() {
#     local action=$1
#     local sed_cmd
#     [[ $action == "disable" ]] && sed_cmd='s/^\(\s*\)\\includegraphics/%\1\\includegraphics/g' || sed_cmd='s/^%\(\s*\\includegraphics\)/\1/g'
#     sed -i "$sed_cmd" "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex
# }

# _toggle_figures() {
#     local action=$1
#     local sed_cmd
#     [[ $action == "disable" ]] && sed_cmd='s/^\(\s*\)\\includegraphics/%\1\\includegraphics/g' || sed_cmd='s/^%\(\s*\\includegraphics\)/\1/g'
#     if [[ -d "$FIGURE_COMPILED_DIR" ]]; then
#         find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" -print0 | xargs -0 sed -i "$sed_cmd"
#     else
#         echo "Error: Directory $FIGURE_COMPILED_DIR not found"
#         return 1
#     fi
# }


_toggle_figures() {
    local action=$1
    local sed_cmd

    # Create debug directory
    mkdir -p "$FIGURE_COMPILED_DIR/debug"

    # Check if compiled figures directory exists
    if [ ! -d "$FIGURE_COMPILED_DIR" ]; then
        echo "Compiled figures directory does not exist. Creating it."
        mkdir -p "$FIGURE_COMPILED_DIR"
        return 0
    fi

    # Check if files exist
    if [[ ! -n $(find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" 2>/dev/null) ]]; then
        echo "No matching figure files found. Skipping figure toggle."
        return 0
    fi

    # Log toggle action
    echo "Toggling figures: $action" > "$FIGURE_COMPILED_DIR/debug/toggle_figures_$(date +"%Y%m%d_%H%M%S").log"

    if [[ $action == "disable" ]]; then
        # Disable all includegraphics
        sed -i 's/^\(\s*\)\\includegraphics/%\1\\includegraphics/g' "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex
    else
        # First make sure jpg directory exists
        mkdir -p "$FIGURE_JPG_DIR"

        # Copy all JPG files from src to jpg directory if they don't exist there already
        echo "Checking for JPG files to copy to $FIGURE_JPG_DIR" >> "$FIGURE_COMPILED_DIR/debug/toggle_figures_$(date +"%Y%m%d_%H%M%S").log"
        find "$FIGURE_SRC_DIR" -name "*.jpg" | while read src_jpg; do
            base_jpg=$(basename "$src_jpg")
            if [ ! -f "$FIGURE_JPG_DIR/$base_jpg" ]; then
                echo "Copying $base_jpg from src to jpg directory" >> "$FIGURE_COMPILED_DIR/debug/toggle_figures_$(date +"%Y%m%d_%H%M%S").log"
                cp "$src_jpg" "$FIGURE_JPG_DIR/"
            fi
        done

        # Log which figures will be processed
        find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" | sort > "$FIGURE_COMPILED_DIR/debug/figure_files_to_process.txt"

        # Now enable includegraphics for files that have corresponding images
        for fig_tex in "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex; do
            [ -e "$fig_tex" ] || continue
            local fname=$(basename "$fig_tex")

            # Determine jpg filename
            local jpg_file=""
            if [[ "$fname" == *".jpg.tex" ]]; then
                jpg_file="${fname%.tex}"  # For .jpg.tex files
            else
                jpg_file="${fname%.tex}.jpg"  # For regular .tex files
            fi

            echo "Processing $fname -> jpg_file=$jpg_file" >> "$FIGURE_COMPILED_DIR/debug/toggle_figures_$(date +"%Y%m%d_%H%M%S").log"

            # Check if image exists, enable includegraphics only if it does
            if [ -f "$FIGURE_JPG_DIR/$jpg_file" ]; then
                # Save original for debugging
                cp "$fig_tex" "$FIGURE_COMPILED_DIR/debug/${fname}.before"

                # Enable includegraphics (uncomment)
                sed -i 's/^%\(\s*\\includegraphics\)/\1/g' "$fig_tex"

                # Update the path to point to the correct image, but only for includegraphics
                # Extract width value from caption file - handle both comment format and direct specification in \includegraphics
                local width_spec=$(grep -o "width=.*\\\\textwidth" "$caption_file" | head -1 | sed 's/width=//')
                
                # If not found in caption file, check for width in the target file itself
                if [[ -z "$width_spec" ]] && [[ -f "$fig_tex" ]]; then
                    width_spec=$(grep -o "width=.*\\\\textwidth" "$fig_tex" | head -1 | sed 's/width=//')
                fi
                
                # Use default width if still not found
                if [[ -z "$width_spec" ]]; then
                    echo "Using default width (1\\textwidth) for $fig_tex" >> "$FIGURE_COMPILED_DIR/debug/width_handling.log"
                    width_spec="1\\\\textwidth"
                else
                    echo "Using width $width_spec for $fig_tex" >> "$FIGURE_COMPILED_DIR/debug/width_handling.log"
                fi
                
                # Ensure width format is correct (add \textwidth if missing)
                if [[ ! "$width_spec" == *"\\textwidth"* ]]; then
                    if [[ "$width_spec" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
                        width_spec="${width_spec}\\\\textwidth"
                        echo "Fixed width format to $width_spec" >> "$FIGURE_COMPILED_DIR/debug/width_handling.log"
                    fi
                fi
                
                # Update includegraphics with correct width and path
                sed -i "s|\\\\includegraphics\[width=[^]]*\]{[^}]*}|\\\\includegraphics[width=$width_spec]{$FIGURE_JPG_DIR/$jpg_file}|g" "$fig_tex"
                # Fix case where width is empty
                sed -i "s|\\\\includegraphics\[width=\]{|\\\\includegraphics[width=$width_spec]{|g" "$fig_tex"
                # Fix case where width has a typo (e.g., extwidth instead of textwidth)
                sed -i "s|\\\\includegraphics\[width=.*extwidth\]{|\\\\includegraphics[width=$width_spec]{|g" "$fig_tex"

                # Make sure [ht] option is set correctly
                sed -i 's/\\begin{figure\*}\[[^\]]*\]/\\begin{figure\*}[ht]/g' "$fig_tex"

                # Save after changes for debugging
                cp "$fig_tex" "$FIGURE_COMPILED_DIR/debug/${fname}.after"

                echo "Updated $fname with path to $FIGURE_JPG_DIR/$jpg_file" >> "$FIGURE_COMPILED_DIR/debug/toggle_figures_$(date +"%Y%m%d_%H%M%S").log"
            else
                echo "WARNING: Image not found: $FIGURE_JPG_DIR/$jpg_file" >> "$FIGURE_COMPILED_DIR/debug/toggle_figures_$(date +"%Y%m%d_%H%M%S").log"
            fi
        done
    fi
}

handle_figure_visibility() {
    local no_figs="$1"

    if [[ "$no_figs" == true ]]; then
        _toggle_figures disable
    else
        tif2jpg
        [[ -n $(find "$FIGURE_JPG_DIR" -name "*.jpg") ]] && _toggle_figures enable || _toggle_figures disable
    fi
}

gather_tex_files () {
    local output_file="$FIGURE_HIDDEN_DIR/.All_Figures.tex"
    local debug_dir="$FIGURE_COMPILED_DIR/debug"

    # Create debug directory if it doesn't exist
    mkdir -p "$debug_dir"

    # Start fresh with a clear file
    echo "% Generated by gather_tex_files() on $(date)" > "$output_file"
    echo "% This file includes all figure files in order" >> "$output_file"
    echo "" >> "$output_file"
    echo "% Set up proper figure structure - using figure* environment to wrap all figures" >> "$output_file"
    echo "% We don't need the headers since we're already in the Figures section" >> "$output_file"
    echo "" >> "$output_file"

    # Save a list of all figure files in a debug file
    find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" | sort > "$debug_dir/figure_files_list.txt"

    # Process each figure file and extract its contents to create proper figure entries
    for fig_tex in $(find "$FIGURE_COMPILED_DIR" -maxdepth 1 -name "Figure_ID_*.tex" | sort); do
        [ -e "$fig_tex" ] || continue

        # Save a copy of each figure file for debugging
        cp "$fig_tex" "$debug_dir/$(basename "$fig_tex").debug"

        # Get filename and figure ID
        local basename=$(basename "$fig_tex")
        local figure_id=""
        local figure_number=""
        local figure_title=""
        local image_path=""
        local width="0.9\\\\textwidth"
        local figure_type="image"
        local caption_content=""

        # Extract ID from filename (e.g., "01_workflow" from "Figure_ID_01_workflow.tex")
        if [[ "$basename" =~ Figure_ID_([^\.]+) ]]; then
            figure_id="${BASH_REMATCH[1]}"
            # Extract the number portion (e.g., "01" from "01_workflow")
            if [[ "$figure_id" =~ ^([0-9]+)_ ]]; then
                figure_number="${BASH_REMATCH[1]}"
            else
                # If no underscore, assume the whole string is the number
                figure_number="$figure_id"
            fi
        fi

        # Create a debug file to trace metadata extraction
        echo "Processing $basename" > "$debug_dir/metadata_${basename}.log"
        
        # Check if the file contains JSON metadata (new format)
        if grep -q "^{" "$fig_tex"; then
            # Create a temporary file with just the JSON content
            sed -n '/^{/,/^}/p' "$fig_tex" > "$debug_dir/metadata_${basename}.json"
            
            # Extract image path from JSON
            if grep -q '"path":' "$debug_dir/metadata_${basename}.json"; then
                image_path=$(grep -o '"path": *"[^"]*"' "$debug_dir/metadata_${basename}.json" | sed 's/"path": *"\(.*\)"/\1/')
                echo "Extracted image path from JSON: $image_path" >> "$debug_dir/metadata_${basename}.log"
            fi
            
            # Extract width from JSON
            if grep -q '"width":' "$debug_dir/metadata_${basename}.json"; then
                width=$(grep -o '"width": *"[^"]*"' "$debug_dir/metadata_${basename}.json" | sed 's/"width": *"\(.*\)"/\1/')
                echo "Extracted width from JSON: $width" >> "$debug_dir/metadata_${basename}.log"
            fi
            
            # Extract figure type from JSON
            if grep -q '"type":' "$debug_dir/metadata_${basename}.json"; then
                figure_type=$(grep -o '"type": *"[^"]*"' "$debug_dir/metadata_${basename}.json" | sed 's/"type": *"\(.*\)"/\1/')
                echo "Extracted figure type from JSON: $figure_type" >> "$debug_dir/metadata_${basename}.log"
            fi
            
            # Extract caption content - everything after the JSON block
            caption_content=$(sed -n '/^}/,$p' "$fig_tex" | tail -n +2 | sed 's/^[ \t]*//' | sed '/^$/d')
            echo "Extracted caption content: $caption_content" >> "$debug_dir/metadata_${basename}.log"
            
            # Extract title from caption content (textbf part)
            if [[ "$caption_content" =~ \\textbf\{([^}]*)\} ]]; then
                figure_title="${BASH_REMATCH[1]}"
                echo "Extracted title from caption: $figure_title" >> "$debug_dir/metadata_${basename}.log"
            fi
        else
            # Legacy format - use older extraction methods
            # Read through the file to extract image path, caption, etc.
            image_path=$(grep -o "\\\\includegraphics\[.*\]{[^}]*}" "$fig_tex" | grep -o "{[^}]*}" | tr -d "{}")
            width_spec=$(grep -o "width=[^,\]}]*" "$fig_tex" | sed 's/width=//' | head -1)
            
            if [ -n "$width_spec" ]; then
                width="$width_spec"
            fi

            echo "Using legacy extraction for $basename" >> "$debug_dir/metadata_${basename}.log"
            echo "Image path: $image_path" >> "$debug_dir/metadata_${basename}.log"
            echo "Width: $width" >> "$debug_dir/metadata_${basename}.log"
            
            # Extract caption title - the text within \textbf{...}
            figure_title=$(sed -n '/\\caption{/,/}/p' "$fig_tex" | grep -A1 "\\\\textbf{" | sed -n 's/.*\\textbf{\(.*\)}.*/\1/p' | tr -d '\n' | xargs)
            
            # Extract caption content from the file
            caption_content=$(sed -n '/\\caption{/,/}/p' "$fig_tex" | sed '1s/^\\caption{//' | sed '$s/}\s*$//')
        fi

        # Ensure path correctness for image - add prefix if missing
        if [[ -n "$image_path" && ! "$image_path" =~ ^[./] ]]; then
            # If path doesn't start with ./ or /, add ./ 
            image_path="./$image_path"
        fi
        
        # Ensure we have figure title
        if [ -z "$figure_title" ]; then
            # Check if we can extract it from caption content
            if [[ "$caption_content" =~ \\textbf\{([^}]*)\} ]]; then
                figure_title="${BASH_REMATCH[1]}"
                echo "Extracted title from caption content: $figure_title" >> "$debug_dir/metadata_${basename}.log"
            else
                # Use default title
                figure_title="Figure $figure_number"
                echo "Using default title: $figure_title" >> "$debug_dir/metadata_${basename}.log"
            fi
        fi
        
        # Use original caption from source file if available
        local original_caption_file="$FIGURE_SRC_DIR/${basename}"
        if [ -f "$original_caption_file" ]; then
            # Extract caption content using advanced pattern matching
            local original_caption=$(sed -n '/\\caption{/,/^}\s*$/p' "$original_caption_file" | sed '1s/^\\caption{//' | sed '$s/}\s*$//')
            if [ -n "$original_caption" ]; then
                caption_content="$original_caption"
                echo "Using original caption from source file" >> "$debug_dir/metadata_${basename}.log"
            fi
        fi
        
        # Prepare caption text - everything after \textbf{...} but before the final }
        local caption_text=""
        if [[ "$caption_content" =~ \\textbf\{.*\}(.*) ]]; then
            caption_text="${BASH_REMATCH[1]}"
            caption_text=$(echo "$caption_text" | grep -v "^%" | sed 's/^[ \t]*//' | sed 's/[ \t]*$//')
            echo "Extracted caption text: $caption_text" >> "$debug_dir/metadata_${basename}.log"
        fi
        
        # Ensure we have caption text
        if [ -z "$caption_text" ]; then
            caption_text="Description for figure $figure_number."
            echo "Using default caption text: $caption_text" >> "$debug_dir/metadata_${basename}.log"
        fi

        # Add figure entry to the output file with proper structure - using [p] to force figures on separate pages
        echo "% Figure $figure_number: ${figure_title}" >> "$output_file"
        echo "\\clearpage" >> "$output_file"
        echo "\\begin{figure*}[p]" >> "$output_file"
        echo "    \\pdfbookmark[2]{Figure $figure_number}{figure_id_$figure_number}" >> "$output_file"
        echo "    \\centering" >> "$output_file"
        
        # Include image based on type
        if [ "$figure_type" = "tikz" ]; then
            # Extract TikZ code from original file
            local tikz_code=$(grep -A100 "\\\\begin{tikzpicture}" "$fig_tex" | sed -n '/\\begin{tikzpicture}/,/\\end{tikzpicture}/p')
            if [ -n "$tikz_code" ]; then
                echo "$tikz_code" >> "$output_file"
                echo "Included TikZ code for $basename" >> "$debug_dir/metadata_${basename}.log"
            else
                echo "    % TikZ code not found in source file" >> "$output_file"
                echo "TikZ code not found for $basename" >> "$debug_dir/metadata_${basename}.log"
                # Fall back to image if available
                if [ -n "$image_path" ]; then
                    echo "    \\includegraphics[width=$width]{$image_path}" >> "$output_file"
                    echo "Falling back to image for $basename" >> "$debug_dir/metadata_${basename}.log"
                fi
            fi
        else
            # Standard image
            if [ -n "$image_path" ]; then
                echo "    \\includegraphics[width=$width]{$image_path}" >> "$output_file"
                echo "Included image path $image_path for $basename" >> "$debug_dir/metadata_${basename}.log"
            else
                echo "    % Image path missing or not found in source file" >> "$output_file"
                echo "Image path missing for $basename" >> "$debug_dir/metadata_${basename}.log"
            fi
        fi
        
        # Add caption with proper structure
        echo "    \\caption{" >> "$output_file"
        echo "\\textbf{" >> "$output_file"
        echo "$figure_title" >> "$output_file"
        echo "}" >> "$output_file"
        echo "\\smallskip" >> "$output_file"
        echo "\\\\" >> "$output_file"
        echo "$caption_text" >> "$output_file"
        echo "}" >> "$output_file"
        
        # Add label
        echo "    \\label{fig:${figure_id}}" >> "$output_file"
        echo "\\end{figure*}" >> "$output_file"
        echo "" >> "$output_file"
        
        # Log processing for debugging
        echo "Processed figure: $basename with ID $figure_id and number $figure_number" >> "$debug_dir/figure_processing.log"
    done

    # Save a copy of the final figures include file for debugging
    cp "$output_file" "$debug_dir/All_Figures.tex.final"
}

main () {
    local no_figs="${1:-true}"
    local p2t="${2:-false}"
    local verbose="${3:-false}"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local log_file="$FIGURE_COMPILED_DIR/debug/process_figures_${timestamp}.log"
    local error_log="$FIGURE_COMPILED_DIR/debug/errors_${timestamp}.log"
    local start_time=$(date +%s)
    
    # Create directories if they don't exist yet
    mkdir -p "$FIGURE_COMPILED_DIR/debug"
    
    # Initialize error log
    echo "=== FIGURE PROCESSING ERROR LOG $(date) ===" > "$error_log"
    echo "Script: $0" >> "$error_log"
    echo "Parameters: no_figs=$no_figs, p2t=$p2t, verbose=$verbose" >> "$error_log"
    echo "=======================================" >> "$error_log"
    
    # Stage tracking
    echo "=== FIGURE PROCESSING PROGRESS TRACKING ===" >> "$log_file"
    
    # Print status to console if verbose mode is enabled
    if [ "$verbose" = true ]; then
        echo "Figure processing: Starting with parameters: no_figs=$no_figs, p2t=$p2t"
    fi
    
    # Initialize the system
    echo "Starting initialization..." >> "$log_file"
    if [ "$verbose" = true ]; then
        echo "Figure processing: Initializing figure directories and processing"
    fi
    
    if init "$@"; then
        echo "[SUCCESS] Initialization completed" >> "$log_file"
        [ "$verbose" = true ] && echo "Figure processing: Initialization completed successfully"
    else
        echo "[ERROR] Initialization failed" | tee -a "$log_file" "$error_log"
        echo "Error in init ($0)" | tee -a "$error_log"
        echo "ERROR: Figure processing initialization failed. See logs at $error_log" >&2
        return 1
    fi
    
    # PowerPoint to TIF conversion if requested
    echo "PowerPoint to TIF conversion (enabled: $p2t)..." >> "$log_file"
    if [ "$verbose" = true ] && [ "$p2t" = true ]; then
        echo "Figure processing: Converting PowerPoint files to TIF format"
    fi
    
    if pptx2tif "$p2t"; then
        echo "[SUCCESS] PowerPoint to TIF conversion completed" >> "$log_file"
        [ "$verbose" = true ] && [ "$p2t" = true ] && echo "Figure processing: PowerPoint conversion completed"
    else
        echo "[ERROR] PowerPoint to TIF conversion failed" | tee -a "$log_file" "$error_log"
        echo "Error in pptx2tif ($0)" | tee -a "$error_log"
        echo "ERROR: PowerPoint to TIF conversion failed. See logs at $error_log" >&2
        return 1
    fi
    
    # Normalize filenames to lowercase
    echo "Normalizing filenames..." >> "$log_file"
    if ensure_lower_letters; then
        echo "[SUCCESS] Filename normalization completed" >> "$log_file"
    else
        echo "[ERROR] Filename normalization failed" | tee -a "$log_file" "$error_log"
        echo "Error in ensure_lower_letters ($0)" | tee -a "$error_log"
        return 1
    fi
    
    # Create caption files if missing
    echo "Checking for missing caption files..." >> "$log_file"
    if ensure_caption; then
        echo "[SUCCESS] Caption files verified" >> "$log_file"
    else
        echo "[ERROR] Caption verification failed" | tee -a "$log_file" "$error_log"
        echo "Error in ensure_caption ($0)" | tee -a "$error_log"
        return 1
    fi
    
    # Crop TIF files if needed
    echo "Cropping TIF files (skipped: $no_figs)..." >> "$log_file"
    if crop_tif "$no_figs"; then
        echo "[SUCCESS] TIF cropping completed" >> "$log_file"
    else
        echo "[ERROR] TIF cropping failed" | tee -a "$log_file" "$error_log"
        echo "Error in crop_tif ($0)" | tee -a "$error_log"
        return 1
    fi
    
    # Convert TIF to JPG
    echo "Converting TIF to JPG (skipped: $no_figs)..." >> "$log_file"
    if tif2jpg "$no_figs"; then
        echo "[SUCCESS] TIF to JPG conversion completed" >> "$log_file"
    else
        echo "[ERROR] TIF to JPG conversion failed" | tee -a "$log_file" "$error_log"
        echo "Error in tif2jpg ($0)" | tee -a "$error_log"
        return 1
    fi
    
    # Compile legends
    echo "Compiling figure legends..." >> "$log_file"
    if compile_legends; then
        echo "[SUCCESS] Legend compilation completed" >> "$log_file"
    else
        echo "[WARNING] Legend compilation may have issues" | tee -a "$log_file" "$error_log"
    fi
    
    # Handle figure visibility
    echo "Setting figure visibility (no_figs: $no_figs)..." >> "$log_file"
    if handle_figure_visibility "$no_figs"; then
        echo "[SUCCESS] Figure visibility set" >> "$log_file"
    else
        echo "[ERROR] Figure visibility handling failed" | tee -a "$log_file" "$error_log"
        echo "Error in handle_figure_visibility ($0)" | tee -a "$error_log"
        return 1
    fi
    
    # Gather all TEX files
    echo "Gathering TeX files..." >> "$log_file"
    if gather_tex_files; then
        echo "[SUCCESS] TeX files gathered" >> "$log_file"
    else
        echo "[ERROR] TeX file gathering failed" | tee -a "$log_file" "$error_log"
        echo "Error in gather_tex_files ($0)" | tee -a "$error_log"
        return 1
    fi
    
    # Calculate statistics
    local compiled_count=$(find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" | wc -l)
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    echo "" >> "$log_file"
    echo "=== FIGURE PROCESSING COMPLETED ===" >> "$log_file"
    echo "Processed $compiled_count figures" >> "$log_file"
    echo "Processing time: $duration seconds" >> "$log_file"
    echo "Log file: $log_file" >> "$log_file"
    echo "Error log: $error_log" >> "$log_file"
    echo "Timestamp: $(date)" >> "$log_file"
    echo "=======================================" >> "$log_file"
    
    # Print success message to console
    echo "Figure processing completed successfully."
    if [ "$no_figs" = true ]; then
        echo "Figures are disabled for this compilation."
    else
        echo "Generated $compiled_count figure files."
        if [ $compiled_count -eq 0 ]; then
            echo "WARNING: No figures were processed. Check your figure files in $FIGURE_SRC_DIR" >&2
        elif [ $compiled_count -eq 1 ]; then
            echo "One figure will be rendered on its own page in the document."
        else
            echo "All $compiled_count figures will be rendered on separate pages in the document."
        fi
    fi
    
    # Provide detailed logs location
    if [ "$verbose" = true ]; then
        echo "Figure processing details:"
        echo "- Processing time: $duration seconds"
        echo "- Log files: $FIGURE_COMPILED_DIR/debug/"
        echo "- Error logs: $error_log"
    else
        echo "See logs in $FIGURE_COMPILED_DIR/debug/ for details."
    fi
}

main "$@"

# /home/ywatanabe/proj/ripple-wm/paper/manuscript/scripts/sh/modules/process_figures.sh true true

# EOF