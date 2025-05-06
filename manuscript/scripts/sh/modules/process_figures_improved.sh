#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-06 10:25:00 (ywatanabe)"
# File: ./manuscript/scripts/sh/modules/process_figures.sh

# Source common modules
THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
source "${THIS_DIR}/error_handling.sh"
source "${THIS_DIR}/config.sh"

# Set up error trapping
setup_error_trap

# Make sure required directories exist
init() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local log_file="$FIGURE_COMPILED_DIR/debug/process_figures_${timestamp}.log"
    
    print_section_header "Initializing Figure Processing"
    log_info "Setting up figure processing environment"
    
    # Create all required directories with proper logging
    for dir in "$FIGURE_SRC_DIR" "$FIGURE_COMPILED_DIR" "$FIGURE_JPG_DIR" "$FIGURE_HIDDEN_DIR" "$FIGURE_COMPILED_DIR/debug"; do
        if [ ! -d "$dir" ]; then
            log_debug "Creating directory: $dir" "$log_file"
            mkdir -p "$dir"
        else
            log_debug "Directory already exists: $dir" "$log_file"
        fi
    done
    
    # Create specialized debug directories
    mkdir -p "$FIGURE_COMPILED_DIR/debug/captions"
    mkdir -p "$FIGURE_COMPILED_DIR/debug/widths"
    mkdir -p "$FIGURE_COMPILED_DIR/debug/toggles"
    
    # Backup existing files before removing
    log_debug "Backing up existing files" "$log_file"
    if [ -f "$FIGURE_HIDDEN_DIR/.All_Figures.tex" ]; then
        cp "$FIGURE_HIDDEN_DIR/.All_Figures.tex" "$FIGURE_COMPILED_DIR/debug/All_Figures_before.tex"
        log_debug "Backed up .All_Figures.tex" "$log_file"
    else
        log_debug "No .All_Figures.tex file found to backup" "$log_file"
    fi

    # Create a timestamped backup directory for this run
    local backup_dir="$FIGURE_COMPILED_DIR/debug/backup_${timestamp}"
    mkdir -p "$backup_dir"
    log_debug "Created backup directory: $backup_dir" "$log_file"

    # Save existing compiled figure files to the backup directory
    local compiled_count=0
    for file in "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex; do
        if [ -f "$file" ]; then
            base_name=$(basename "$file")
            cp "$file" "$backup_dir/${base_name}"
            log_debug "Backed up: $base_name" "$log_file"
            ((compiled_count++))
        fi
    done
    log_info "Backed up $compiled_count compiled figure files" "$log_file"

    # Count files found for statistics
    local source_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tex" 2>/dev/null | wc -l)
    local image_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*" -not -name "*.tex" 2>/dev/null | wc -l)
    
    log_info "File statistics before processing:" "$log_file"
    log_info "- Compiled figure files: $compiled_count" "$log_file"
    log_info "- Source caption files: $source_count" "$log_file"
    log_info "- Source image files: $image_count" "$log_file"

    # Now perform cleanup
    log_info "Performing cleanup of compiled files" "$log_file"
    rm -f "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex "$FIGURE_HIDDEN_DIR"/*.tex
    
    # Create output files
    rm -f "$FIGURE_HIDDEN_DIR/.All_Figures.tex"
    touch "$FIGURE_HIDDEN_DIR/.All_Figures.tex"
    log_debug "Created empty .All_Figures.tex file" "$log_file"
    
    log_info "Initialization complete" "$log_file"
    return 0
}

# Create caption files for figures if they don't exist
ensure_caption() {
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local log_file="$FIGURE_COMPILED_DIR/debug/ensure_caption_${timestamp}.log"
    
    print_section_header "Ensuring Figure Captions"
    log_info "Checking for missing caption files" "$log_file"
    
    local created_count=0
    local existing_count=0
    
    # Process all image types (TIF, JPG, PNG, SVG)
    for img_type in "tif" "jpg" "png" "svg"; do
        log_debug "Processing $img_type files" "$log_file"
        
        for img_file in "$FIGURE_SRC_DIR"/Figure_ID_*.$img_type; do
            [ -e "$img_file" ] || continue
            local filename=$(basename "$img_file")
            local caption_tex_file="$FIGURE_SRC_DIR/${filename%.$img_type}.tex"
            
            log_debug "Processing $img_type file: $filename" "$log_file"
            
            if [ ! -f "$caption_tex_file" ] && [ ! -L "$caption_tex_file" ]; then
                log_info "Creating caption for $filename" "$log_file"
                # Try to find a template to use
                if [ -f "$FIGURE_SRC_DIR/templates/_Figure_ID_XX.tex" ]; then
                    cp "$FIGURE_SRC_DIR/templates/_Figure_ID_XX.tex" "$caption_tex_file"
                    log_debug "Created from template: $caption_tex_file" "$log_file"
                elif [ -f "$FIGURE_SRC_DIR/_Figure_ID_XX.tex" ]; then
                    cp "$FIGURE_SRC_DIR/_Figure_ID_XX.tex" "$caption_tex_file"
                    log_debug "Created from legacy template: $caption_tex_file" "$log_file"
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
                    log_debug "Created from inline template: $caption_tex_file" "$log_file"
                fi
                ((created_count++))
            else
                log_debug "Caption already exists: $caption_tex_file" "$log_file"
                ((existing_count++))
            fi
            
            # If it's a JPG file, make sure it's in the JPG directory
            if [ "$img_type" = "jpg" ] && [ ! -f "$FIGURE_JPG_DIR/$filename" ]; then
                log_debug "Copying $filename to $FIGURE_JPG_DIR" "$log_file"
                cp "$img_file" "$FIGURE_JPG_DIR/"
            fi
            
            # If it's PNG or SVG, convert to JPG if not already there
            if [[ "$img_type" = "png" || "$img_type" = "svg" ]] && [ ! -f "$FIGURE_JPG_DIR/${filename%.$img_type}.jpg" ]; then
                local jpg_filename="${filename%.$img_type}.jpg"
                log_info "Converting $img_type to JPG: $filename -> $jpg_filename" "$log_file"
                
                if [ "$img_type" = "svg" ] && command -v inkscape >/dev/null 2>&1; then
                    log_debug "Using Inkscape for SVG conversion" "$log_file"
                    if ! inkscape -z -e "$FIGURE_JPG_DIR/$jpg_filename" -w 1200 -h 1200 "$img_file"; then
                        log_warning "Inkscape conversion failed, falling back to ImageMagick" "$log_file"
                        convert "$img_file" -density 300 -quality 90 "$FIGURE_JPG_DIR/$jpg_filename" || 
                            log_error "ImageMagick conversion failed for $img_file" "$log_file"
                    fi
                else
                    # Use ImageMagick for conversion
                    log_debug "Using ImageMagick for conversion" "$log_file"
                    convert "$img_file" -density 300 -quality 90 "$FIGURE_JPG_DIR/$jpg_filename" || 
                        log_error "ImageMagick conversion failed for $img_file" "$log_file"
                fi
            fi
        done
    done
    
    log_info "Caption generation complete" "$log_file"
    log_info "Created $created_count new caption files, $existing_count already existed" "$log_file"
    log_info "Processed files summary:" "$log_file"
    log_info "- TIF files: $(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tif" 2>/dev/null | wc -l)" "$log_file"
    log_info "- JPG files: $(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.jpg" 2>/dev/null | wc -l)" "$log_file"
    log_info "- PNG files: $(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.png" 2>/dev/null | wc -l)" "$log_file"
    log_info "- SVG files: $(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.svg" 2>/dev/null | wc -l)" "$log_file"
    log_info "- Caption files: $(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tex" 2>/dev/null | wc -l)" "$log_file"
    
    return 0
}

# Ensure filenames use lowercase letters
ensure_lower_letters() {
    local ORIG_DIR="$(pwd)"
    
    print_section_header "Normalizing Filenames"
    log_info "Converting figure filenames to lowercase"
    
    cd "$FIGURE_SRC_DIR" || {
        log_error "Failed to change directory to $FIGURE_SRC_DIR"
        return 1
    }

    local renamed_count=0
    for file in Figure_ID_*; do
        if [[ -f "$file" || -L "$file" ]]; then
            new_name=$(echo "$file" | sed -E 's/(Figure_ID_)(.*)/\1\L\2/')
            if [[ "$file" != "$new_name" ]]; then
                log_debug "Renaming $file to $new_name"
                mv "$file" "$new_name" || log_error "Failed to rename $file to $new_name"
                ((renamed_count++))
            fi
        fi
    done

    cd "$ORIG_DIR" || {
        log_error "Failed to return to original directory $ORIG_DIR"
        return 1
    }
    
    log_info "Renamed $renamed_count files to lowercase"
    return 0
}

# Convert PowerPoint files to TIF if requested
pptx2tif() {
    local p2t="$1"

    if [[ "$p2t" == true ]]; then
        print_section_header "Converting PowerPoint to TIF"
        log_info "Starting PowerPoint to TIF conversion"
        
        if [ -f "./scripts/sh/modules/pptx2tif_all.sh" ]; then
            # Run the conversion script
            run_command_verbose "./scripts/sh/modules/pptx2tif_all.sh" "PowerPoint to TIF conversion"
        else
            log_error "pptx2tif_all.sh script not found in expected location"
            return 1
        fi
    else
        log_debug "Skipping PowerPoint to TIF conversion (not requested)"
    fi
    
    return 0
}

# Crop TIF files if needed
crop_tif() {
    local no_figs="$1"
    
    if [[ "$no_figs" == false ]]; then
        print_section_header "Cropping TIF Files"
        
        # Check if the Python script exists
        if [ -f "./scripts/py/crop_tif.py" ] && command -v python3 >/dev/null 2>&1; then
            log_info "Starting TIF cropping process"
            
            # Find all TIF files and process them
            local tif_files=($(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tif" 2>/dev/null))
            if [ ${#tif_files[@]} -eq 0 ]; then
                log_info "No TIF files found to crop"
                return 0
            fi
            
            log_info "Found ${#tif_files[@]} TIF files to process"
            
            # Check if parallel is available
            if command -v parallel >/dev/null 2>&1; then
                log_debug "Using GNU parallel for TIF cropping"
                if ! find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tif" | 
                     parallel -j+0 --eta 'python3 ./scripts/py/crop_tif.py -l {}'; then
                    log_error "Error during parallel TIF cropping"
                    return 1
                fi
            else
                log_warning "GNU parallel not found, processing TIF files sequentially"
                for tif_file in "${tif_files[@]}"; do
                    log_debug "Cropping $tif_file"
                    if ! python3 ./scripts/py/crop_tif.py -l "$tif_file"; then
                        log_error "Error cropping $tif_file"
                    fi
                done
            fi
            
            log_info "TIF cropping complete"
        else
            log_warning "crop_tif.py script not found or Python not available, skipping TIF cropping"
        fi
    else
        log_debug "Skipping TIF cropping (figures not included)"
    fi
    
    return 0
}

# Convert images to JPG for inclusion in the document
tif2jpg() {
    local no_figs="$1"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local log_file="$FIGURE_COMPILED_DIR/debug/image_processing_${timestamp}.log"
    
    if [[ "$no_figs" == false ]]; then
        print_section_header "Converting Images to JPG"
        log_info "Starting image conversion to JPG format" "$log_file"
        mkdir -p "$FIGURE_COMPILED_DIR/debug"
        
        # Check if we have Python and the optimize_figure.py script available
        if [ -f "./scripts/py/optimize_figure.py" ] && command -v python3 >/dev/null 2>&1; then
            log_info "Using optimize_figure.py for high-quality image processing" "$log_file"
            
            # Check for parallel
            if ! command -v parallel >/dev/null 2>&1; then
                log_warning "GNU parallel not found, image processing may be slower" "$log_file"
            fi
            
            # Process different image types
            for img_type in "tif" "png" "svg" "jpg"; do
                local img_files=($(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.$img_type" 2>/dev/null))
                if [ ${#img_files[@]} -eq 0 ]; then
                    log_debug "No $img_type files found to process" "$log_file"
                    continue
                fi
                
                log_info "Processing ${#img_files[@]} $img_type files" "$log_file"
                
                # Use parallel if available
                if command -v parallel >/dev/null 2>&1; then
                    # Handle different image types
                    if [ "$img_type" = "svg" ] && command -v inkscape >/dev/null 2>&1; then
                        # SVG with Inkscape
                        find "$FIGURE_SRC_DIR" -name "Figure_ID_*.$img_type" | parallel -j+0 --eta '
                            echo -e "\nConverting SVG {} to '"$FIGURE_JPG_DIR"'/$(basename {} .'"$img_type"').jpg"
                            inkscape -z -e "'"$FIGURE_JPG_DIR"'/$(basename {} .'"$img_type"')_temp.png" -w 1200 -h 1200 {}
                            python3 ./scripts/py/optimize_figure.py --input "'"$FIGURE_JPG_DIR"'/$(basename {} .'"$img_type"')_temp.png" --output "'"$FIGURE_JPG_DIR"'/$(basename {} .'"$img_type"').jpg" --dpi 300 --quality 95 >> '"$log_file"'
                            rm -f "'"$FIGURE_JPG_DIR"'/$(basename {} .'"$img_type"')_temp.png"
                        ' || log_error "Error processing SVG files" "$log_file"
                    elif [ "$img_type" = "jpg" ]; then
                        # JPG direct copy/optimize
                        find "$FIGURE_SRC_DIR" -name "Figure_ID_*.$img_type" | parallel -j+0 --eta '
                            if [ ! -f "'"$FIGURE_JPG_DIR"'/$(basename {})" ]; then
                                echo -e "\nOptimizing {} to '"$FIGURE_JPG_DIR"'/$(basename {})"
                                python3 ./scripts/py/optimize_figure.py --input {} --output "'"$FIGURE_JPG_DIR"'/$(basename {})" --dpi 300 --quality 95 >> '"$log_file"'
                            fi
                        ' || log_error "Error processing JPG files" "$log_file"
                    else
                        # TIF and PNG with Python
                        find "$FIGURE_SRC_DIR" -name "Figure_ID_*.$img_type" | parallel -j+0 --eta '
                            echo -e "\nOptimizing {} to '"$FIGURE_JPG_DIR"'/$(basename {} .'"$img_type"').jpg"
                            python3 ./scripts/py/optimize_figure.py --input {} --output "'"$FIGURE_JPG_DIR"'/$(basename {} .'"$img_type"').jpg" --dpi 300 --quality 95 >> '"$log_file"'
                        ' || log_error "Error processing $img_type files" "$log_file"
                    fi
                else
                    # Sequential processing without parallel
                    for img_file in "${img_files[@]}"; do
                        local basename_no_ext=$(basename "$img_file" ".$img_type")
                        
                        if [ "$img_type" = "svg" ] && command -v inkscape >/dev/null 2>&1; then
                            # SVG with Inkscape
                            log_debug "Converting SVG $img_file to JPG" "$log_file"
                            if inkscape -z -e "$FIGURE_JPG_DIR/${basename_no_ext}_temp.png" -w 1200 -h 1200 "$img_file"; then
                                python3 ./scripts/py/optimize_figure.py --input "$FIGURE_JPG_DIR/${basename_no_ext}_temp.png" --output "$FIGURE_JPG_DIR/${basename_no_ext}.jpg" --dpi 300 --quality 95 >> "$log_file"
                                rm -f "$FIGURE_JPG_DIR/${basename_no_ext}_temp.png"
                            else
                                log_error "Error converting SVG: $img_file" "$log_file"
                            fi
                        elif [ "$img_type" = "jpg" ]; then
                            # JPG direct copy/optimize
                            if [ ! -f "$FIGURE_JPG_DIR/$(basename "$img_file")" ]; then
                                log_debug "Optimizing JPG $img_file" "$log_file"
                                python3 ./scripts/py/optimize_figure.py --input "$img_file" --output "$FIGURE_JPG_DIR/$(basename "$img_file")" --dpi 300 --quality 95 >> "$log_file" || 
                                    log_error "Error optimizing JPG: $img_file" "$log_file"
                            fi
                        else
                            # TIF and PNG with Python
                            log_debug "Converting $img_type $img_file to JPG" "$log_file"
                            python3 ./scripts/py/optimize_figure.py --input "$img_file" --output "$FIGURE_JPG_DIR/${basename_no_ext}.jpg" --dpi 300 --quality 95 >> "$log_file" || 
                                log_error "Error converting $img_type: $img_file" "$log_file"
                        fi
                    done
                fi
            done
        else
            # Fall back to ImageMagick if Python or script not available
            log_warning "Python or optimize_figure.py not found, using ImageMagick for basic image conversion" "$log_file"
            
            # Process different image types
            for img_type in "tif" "png" "svg" "jpg"; do
                local img_files=($(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.$img_type" 2>/dev/null))
                if [ ${#img_files[@]} -eq 0 ]; then
                    log_debug "No $img_type files found to process" "$log_file"
                    continue
                fi
                
                log_info "Processing ${#img_files[@]} $img_type files with ImageMagick" "$log_file"
                
                # Use parallel if available
                if command -v parallel >/dev/null 2>&1; then
                    if [ "$img_type" = "jpg" ]; then
                        # Just copy JPG files
                        find "$FIGURE_SRC_DIR" -name "Figure_ID_*.$img_type" | parallel -j+0 --eta '
                            if [ ! -f "'"$FIGURE_JPG_DIR"'/$(basename {})" ]; then
                                echo -e "\nCopying {} to '"$FIGURE_JPG_DIR"'/$(basename {})"
                                cp {} "'"$FIGURE_JPG_DIR"'/$(basename {})"
                            fi
                        ' || log_error "Error copying JPG files" "$log_file"
                    else
                        # Convert other formats to JPG
                        find "$FIGURE_SRC_DIR" -name "Figure_ID_*.$img_type" | parallel -j+0 --eta '
                            echo -e "\nConverting {} to '"$FIGURE_JPG_DIR"'/$(basename {} .'"$img_type"').jpg"
                            convert {} -density 300 -quality 95 "'"$FIGURE_JPG_DIR"'/$(basename {} .'"$img_type"').jpg"
                        ' || log_error "Error converting $img_type files" "$log_file"
                    fi
                else
                    # Sequential processing without parallel
                    for img_file in "${img_files[@]}"; do
                        local basename_no_ext=$(basename "$img_file" ".$img_type")
                        
                        if [ "$img_type" = "jpg" ]; then
                            # Just copy JPG files
                            if [ ! -f "$FIGURE_JPG_DIR/$(basename "$img_file")" ]; then
                                log_debug "Copying JPG $img_file" "$log_file"
                                cp "$img_file" "$FIGURE_JPG_DIR/" || 
                                    log_error "Error copying JPG: $img_file" "$log_file"
                            fi
                        else
                            # Convert other formats to JPG
                            log_debug "Converting $img_type $img_file to JPG" "$log_file"
                            convert "$img_file" -density 300 -quality 95 "$FIGURE_JPG_DIR/${basename_no_ext}.jpg" || 
                                log_error "Error converting $img_type: $img_file" "$log_file"
                        fi
                    done
                fi
            done
        fi
        
        # Count processed files
        local tif_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tif" 2>/dev/null | wc -l)
        local png_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.png" 2>/dev/null | wc -l)
        local svg_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.svg" 2>/dev/null | wc -l)
        local jpg_count=$(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.jpg" 2>/dev/null | wc -l)
        local total_processed=$((tif_count + png_count + svg_count + jpg_count))
        local jpg_output_count=$(find "$FIGURE_JPG_DIR" -name "*.jpg" 2>/dev/null | wc -l)
        
        log_info "Image processing complete. Processed $total_processed source files." "$log_file"
        log_info "Generated $jpg_output_count JPG files in output directory." "$log_file"
        log_info "Processed files summary:" "$log_file"
        log_info "- TIF files: $tif_count" "$log_file"
        log_info "- PNG files: $png_count" "$log_file"
        log_info "- SVG files: $svg_count" "$log_file"
        log_info "- JPG files: $jpg_count" "$log_file"
        log_info "- Total processed: $total_processed" "$log_file"
    else
        log_debug "Skipping image conversion (figures not included)"
    fi
    
    return 0
}

# Compile figure legends into LaTeX files
compile_legends() {
    print_section_header "Compiling Figure Legends"
    log_info "Processing figure captions and preparing for LaTeX inclusion"
    
    # Create output directory if needed
    mkdir -p "$FIGURE_COMPILED_DIR"
    mkdir -p "$FIGURE_COMPILED_DIR/debug"
    rm -f "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex
    
    # Create a figures section header file
    local figures_header_file="$FIGURE_COMPILED_DIR/00_Figures_Header.tex"
    log_info "Creating figure header file"
    cat > "$figures_header_file" << "EOF"
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% FIGURES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\clearpage
\section*{Figures}
\label{figures}
\pdfbookmark[1]{Figures}{figures}
EOF
    
    # Process each caption file
    local caption_files=($(find "$FIGURE_SRC_DIR" -name "Figure_ID_*.tex" 2>/dev/null))
    log_info "Found ${#caption_files[@]} caption files to process"
    
    local processed_count=0
    for caption_file in "${caption_files[@]}"; do
        local fname=$(basename "$caption_file")
        log_debug "Processing caption file: $fname"
        
        # Copy original for debugging
        cp "$caption_file" "$FIGURE_COMPILED_DIR/debug/${fname}.original"
        
        # Extract ID from filename (e.g., "01_workflow" from "Figure_ID_01_workflow.tex")
        local figure_id=""
        local figure_number=""
        
        if [[ "$fname" =~ Figure_ID_([^\.]+) ]]; then
            figure_id="${BASH_REMATCH[1]}"
        else
            log_warning "Invalid filename format: $fname"
            continue
        fi
        
        # Clean ID (remove .jpg suffix if present)
        local figure_id_clean=$(echo "$figure_id" | sed 's/\.jpg$//')
        
        # Extract the number portion (e.g., "01" from "01_workflow")
        if [[ "$figure_id_clean" =~ ^([0-9]+)_ ]]; then
            figure_number="${BASH_REMATCH[1]}"
        else
            # If no underscore, assume the whole string is the number
            figure_number="$figure_id_clean"
        fi
        
        local tgt_file="$FIGURE_COMPILED_DIR/$fname"
        
        # Determine if this is a tikz figure
        local is_tikz=false
        if grep -q "\\\\begin{tikzpicture}" "$caption_file"; then
            is_tikz=true
            log_debug "$fname is a TikZ figure"
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
        mkdir -p "$FIGURE_COMPILED_DIR/debug/captions"
        
        local caption_content=""
        # Check if the file contains a caption
        if grep -q "\\\\caption{" "$caption_file"; then
            # Save original caption file for debugging
            cp "$caption_file" "$FIGURE_COMPILED_DIR/debug/captions/${fname}.original"
            
            # Extract caption content
            caption_raw=$(sed -n '/\\caption{/,/^}\s*$/p' "$caption_file" | sed '1s/^\\caption{//' | sed '$s/}\s*$//')
            echo "$caption_raw" > "$FIGURE_COMPILED_DIR/debug/captions/${fname}.raw"
            
            # Process the extracted content
            caption_content=$(echo "$caption_raw" | grep -v "\\\\label{" | sed '/^$/d' | sed 's/^[ \t]*//' | sed 's/[ \t]*$//')
            echo "$caption_content" > "$FIGURE_COMPILED_DIR/debug/captions/${fname}.processed"
        else
            # If there's no caption tag, use the entire file content as caption
            caption_content=$(cat "$caption_file" | grep -v "^%" | grep -v "^$" | sed 's/^[ \t]*//' | sed 's/[ \t]*$//')
        fi
        
        # If extraction failed, use a default caption
        if [ -z "$caption_content" ]; then
            caption_content="\\textbf{Figure $figure_number.} No caption available."
            log_warning "Using default caption for $fname"
        fi
        
        # Create the figure snippet file
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
                log_debug "Created TikZ figure metadata: $tgt_file"
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
                log_debug "Created image figure metadata: $tgt_file"
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
            log_debug "Created image figure metadata: $tgt_file"
        fi
        
        # Save compiled file for debugging
        cp "$tgt_file" "$FIGURE_COMPILED_DIR/debug/${fname}.compiled"
        ((processed_count++))
    done
    
    log_info "Successfully processed $processed_count figure captions"
    return 0
}

# Toggle figure inclusion in compiled files
_toggle_figures() {
    local action=$1
    
    print_section_header "Toggling Figure Visibility ($action)"
    
    # Create debug directory
    mkdir -p "$FIGURE_COMPILED_DIR/debug"
    
    # Check if compiled figures directory exists
    if [ ! -d "$FIGURE_COMPILED_DIR" ]; then
        log_warning "Compiled figures directory does not exist. Creating it."
        mkdir -p "$FIGURE_COMPILED_DIR"
        return 0
    fi
    
    # Check if files exist
    local fig_files=($(find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" 2>/dev/null))
    if [ ${#fig_files[@]} -eq 0 ]; then
        log_warning "No matching figure files found. Skipping figure toggle."
        return 0
    fi
    
    # Log toggle action
    local debug_log="$FIGURE_COMPILED_DIR/debug/toggle_figures_$(date +"%Y%m%d_%H%M%S").log"
    log_info "Toggling figures: $action" "$debug_log"
    
    if [[ $action == "disable" ]]; then
        # Disable all includegraphics
        log_info "Disabling figure inclusion in ${#fig_files[@]} files"
        sed -i 's/^\(\s*\)\\includegraphics/%\1\\includegraphics/g' "$FIGURE_COMPILED_DIR"/Figure_ID_*.tex || 
            log_error "Error disabling figures" "$debug_log"
    else
        # First make sure jpg directory exists
        mkdir -p "$FIGURE_JPG_DIR"
        
        # Copy all JPG files from src to jpg directory if they don't exist there already
        log_debug "Checking for JPG files to copy to $FIGURE_JPG_DIR" "$debug_log"
        local src_jpg_files=($(find "$FIGURE_SRC_DIR" -name "*.jpg" 2>/dev/null))
        
        for src_jpg in "${src_jpg_files[@]}"; do
            base_jpg=$(basename "$src_jpg")
            if [ ! -f "$FIGURE_JPG_DIR/$base_jpg" ]; then
                log_debug "Copying $base_jpg from src to jpg directory" "$debug_log"
                cp "$src_jpg" "$FIGURE_JPG_DIR/" || log_error "Failed to copy $src_jpg to $FIGURE_JPG_DIR" "$debug_log"
            fi
        done
        
        # Log which figures will be processed
        find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" 2>/dev/null | sort > "$FIGURE_COMPILED_DIR/debug/figure_files_to_process.txt"
        
        # Enable includegraphics for files that have corresponding images
        local enabled_count=0
        local missing_count=0
        
        for fig_tex in "${fig_files[@]}"; do
            local fname=$(basename "$fig_tex")
            
            # Determine jpg filename
            local jpg_file=""
            if [[ "$fname" == *".jpg.tex" ]]; then
                jpg_file="${fname%.tex}"  # For .jpg.tex files
            else
                jpg_file="${fname%.tex}.jpg"  # For regular .tex files
            fi
            
            log_debug "Processing $fname -> jpg_file=$jpg_file" "$debug_log"
            
            # Check if image exists, enable includegraphics only if it does
            if [ -f "$FIGURE_JPG_DIR/$jpg_file" ]; then
                # Save original for debugging
                cp "$fig_tex" "$FIGURE_COMPILED_DIR/debug/${fname}.before"
                
                # Enable includegraphics (uncomment)
                sed -i 's/^%\(\s*\\includegraphics\)/\1/g' "$fig_tex" || 
                    log_error "Failed to enable includegraphics in $fig_tex" "$debug_log"
                
                # Extract width from caption or figure metadata
                local width_spec=$(grep -o "width=.*\\\\textwidth" "$caption_file" 2>/dev/null | head -1 | sed 's/width=//')
                
                # If not found in caption file, check the target file itself
                if [[ -z "$width_spec" ]] && [[ -f "$fig_tex" ]]; then
                    width_spec=$(grep -o "width=.*\\\\textwidth" "$fig_tex" 2>/dev/null | head -1 | sed 's/width=//')
                fi
                
                # Use default width if still not found
                if [[ -z "$width_spec" ]]; then
                    log_debug "Using default width (1\\textwidth) for $fig_tex" "$debug_log"
                    width_spec="1\\\\textwidth"
                else
                    log_debug "Using width $width_spec for $fig_tex" "$debug_log"
                fi
                
                # Ensure width format is correct (add \textwidth if missing)
                if [[ ! "$width_spec" == *"\\textwidth"* ]]; then
                    if [[ "$width_spec" =~ ^[0-9]+(\.[0-9]+)?$ ]]; then
                        width_spec="${width_spec}\\\\textwidth"
                        log_debug "Fixed width format to $width_spec" "$debug_log"
                    fi
                fi
                
                # Update includegraphics with correct width and path
                sed -i "s|\\\\includegraphics\[width=[^]]*\]{[^}]*}|\\\\includegraphics[width=$width_spec]{$FIGURE_JPG_DIR/$jpg_file}|g" "$fig_tex" || 
                    log_error "Failed to update includegraphics path in $fig_tex" "$debug_log"
                
                # Fix case where width is empty
                sed -i "s|\\\\includegraphics\[width=\]{|\\\\includegraphics[width=$width_spec]{|g" "$fig_tex"
                
                # Fix case where width has a typo
                sed -i "s|\\\\includegraphics\[width=.*extwidth\]{|\\\\includegraphics[width=$width_spec]{|g" "$fig_tex"
                
                # Make sure [ht] option is set correctly
                sed -i 's/\\begin{figure\*}\[[^\]]*\]/\\begin{figure\*}[ht]/g' "$fig_tex"
                
                # Save after changes for debugging
                cp "$fig_tex" "$FIGURE_COMPILED_DIR/debug/${fname}.after"
                
                log_debug "Updated $fname with path to $FIGURE_JPG_DIR/$jpg_file" "$debug_log"
                ((enabled_count++))
            else
                log_warning "Image not found: $FIGURE_JPG_DIR/$jpg_file" "$debug_log"
                ((missing_count++))
            fi
        done
        
        log_info "Enabled $enabled_count figure inclusions, $missing_count figures had missing images" "$debug_log"
    fi
    
    return 0
}

# Handle figure visibility based on no_figs parameter
handle_figure_visibility() {
    local no_figs="$1"
    
    print_section_header "Managing Figure Visibility"
    
    if [[ "$no_figs" == true ]]; then
        log_info "Figures disabled - removing figure inclusions"
        _toggle_figures disable
    else
        log_info "Figures enabled - ensuring JPG files exist"
        tif2jpg false
        
        # Check if any JPG files exist and enable figures accordingly
        if [[ -n $(find "$FIGURE_JPG_DIR" -name "*.jpg" 2>/dev/null) ]]; then
            log_info "JPG files found - enabling figure inclusions"
            _toggle_figures enable
        else
            log_warning "No JPG files found - disabling figure inclusions"
            _toggle_figures disable
        fi
    fi
    
    return 0
}

# Gather all figure TEX files into a single file for inclusion
gather_tex_files() {
    local output_file="$FIGURE_HIDDEN_DIR/.All_Figures.tex"
    local debug_dir="$FIGURE_COMPILED_DIR/debug"
    
    print_section_header "Gathering Figure Files"
    log_info "Creating combined figure file at $output_file"
    
    # Create debug directory if it doesn't exist
    mkdir -p "$debug_dir"
    
    # Start fresh with a clear file
    echo "% Generated by gather_tex_files() on $(date)" > "$output_file"
    echo "% This file includes all figure files in order" >> "$output_file"
    echo "" >> "$output_file"
    
    # Save a list of all figure files in a debug file
    find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" 2>/dev/null | sort > "$debug_dir/figure_files_list.txt"
    
    local fig_files=($(find "$FIGURE_COMPILED_DIR" -maxdepth 1 -name "Figure_ID_*.tex" 2>/dev/null | sort))
    log_info "Found ${#fig_files[@]} figure files to process"
    
    if [ ${#fig_files[@]} -eq 0 ]; then
        log_warning "No figure files found to process"
        echo "% No figures found to include" >> "$output_file"
        return 0
    fi
    
    # Process each figure file
    local processed_count=0
    for fig_tex in "${fig_files[@]}"; do
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
        
        # Extract ID from filename
        if [[ "$basename" =~ Figure_ID_([^\.]+) ]]; then
            figure_id="${BASH_REMATCH[1]}"
            # Extract the number portion
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
        
        # Add figure entry to the output file with proper structure
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
        ((processed_count++))
    done
    
    # Save a copy of the final figures include file for debugging
    cp "$output_file" "$debug_dir/All_Figures.tex.final"
    
    log_info "Successfully processed $processed_count figures into combined file"
    return 0
}

# Main function to coordinate all figure processing
main() {
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
    
    print_section_header "Figure Processing"
    log_info "Starting figure processing with parameters: no_figs=$no_figs, p2t=$p2t, verbose=$verbose"
    
    # Print status to console if verbose mode is enabled
    if [ "$verbose" = true ]; then
        echo "Figure processing: Starting with parameters: no_figs=$no_figs, p2t=$p2t"
    fi
    
    # Stage 1: Initialize the system
    log_info "Stage 1: Initialization" "$log_file"
    if init; then
        log_info "Initialization completed successfully" "$log_file"
        [ "$verbose" = true ] && echo "Figure processing: Initialization completed successfully"
    else
        log_error "Initialization failed" "$error_log"
        echo "ERROR: Figure processing initialization failed. See logs at $error_log" >&2
        return 1
    fi
    
    # Stage 2: PowerPoint to TIF conversion if requested
    log_info "Stage 2: PowerPoint to TIF conversion (enabled: $p2t)" "$log_file"
    if [ "$verbose" = true ] && [ "$p2t" = true ]; then
        echo "Figure processing: Converting PowerPoint files to TIF format"
    fi
    
    if pptx2tif "$p2t"; then
        log_info "PowerPoint to TIF conversion completed" "$log_file"
        [ "$verbose" = true ] && [ "$p2t" = true ] && 
            echo "Figure processing: PowerPoint conversion completed"
    else
        log_error "PowerPoint to TIF conversion failed" "$error_log"
        echo "ERROR: PowerPoint to TIF conversion failed. See logs at $error_log" >&2
        return 1
    fi
    
    # Stage 3: Normalize filenames to lowercase
    log_info "Stage 3: Normalizing filenames" "$log_file"
    if ensure_lower_letters; then
        log_info "Filename normalization completed" "$log_file"
    else
        log_error "Filename normalization failed" "$error_log"
        echo "ERROR: Filename normalization failed. See logs at $error_log" >&2
        return 1
    fi
    
    # Stage 4: Create caption files if missing
    log_info "Stage 4: Checking for missing caption files" "$log_file"
    if ensure_caption; then
        log_info "Caption files verified" "$log_file"
    else
        log_error "Caption verification failed" "$error_log"
        echo "ERROR: Caption verification failed. See logs at $error_log" >&2
        return 1
    fi
    
    # Stage 5: Crop TIF files if needed
    log_info "Stage 5: Cropping TIF files (skipped: $no_figs)" "$log_file"
    if crop_tif "$no_figs"; then
        log_info "TIF cropping completed" "$log_file"
    else
        log_error "TIF cropping failed" "$error_log"
        echo "ERROR: TIF cropping failed. See logs at $error_log" >&2
        return 1
    fi
    
    # Stage 6: Convert TIF to JPG
    log_info "Stage 6: Converting TIF to JPG (skipped: $no_figs)" "$log_file"
    if tif2jpg "$no_figs"; then
        log_info "TIF to JPG conversion completed" "$log_file"
    else
        log_error "TIF to JPG conversion failed" "$error_log"
        echo "ERROR: TIF to JPG conversion failed. See logs at $error_log" >&2
        return 1
    fi
    
    # Stage 7: Compile legends
    log_info "Stage 7: Compiling figure legends" "$log_file"
    if compile_legends; then
        log_info "Legend compilation completed" "$log_file"
    else
        log_warning "Legend compilation may have issues" "$error_log"
    fi
    
    # Stage 8: Handle figure visibility
    log_info "Stage 8: Setting figure visibility (no_figs: $no_figs)" "$log_file"
    if handle_figure_visibility "$no_figs"; then
        log_info "Figure visibility set" "$log_file"
    else
        log_error "Figure visibility handling failed" "$error_log"
        echo "ERROR: Figure visibility handling failed. See logs at $error_log" >&2
        return 1
    fi
    
    # Stage 9: Gather all TEX files
    log_info "Stage 9: Gathering TeX files" "$log_file"
    if gather_tex_files; then
        log_info "TeX files gathered" "$log_file"
    else
        log_error "TeX file gathering failed" "$error_log"
        echo "ERROR: TeX file gathering failed. See logs at $error_log" >&2
        return 1
    fi
    
    # Calculate statistics
    local compiled_count=$(find "$FIGURE_COMPILED_DIR" -name "Figure_ID_*.tex" 2>/dev/null | wc -l)
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    log_info "=== FIGURE PROCESSING COMPLETED ===" "$log_file"
    log_info "Processed $compiled_count figures" "$log_file"
    log_info "Processing time: $duration seconds" "$log_file"
    
    # Print success message to console
    echo "Figure processing completed successfully."
    if [ "$no_figs" = true ]; then
        echo "Figures are disabled for this compilation."
    else
        echo "Generated $compiled_count figure files."
        if [ $compiled_count -eq 0 ]; then
            echo "WARNING: No figures were processed. Check your figure files in $FIGURE_SRC_DIR"
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
    
    return 0
}

# Run the main function with provided arguments
main "$@"

# EOF